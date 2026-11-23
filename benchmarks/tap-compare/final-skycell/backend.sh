# Sourced by every driver in this directory (PROTOCOL.md, "What is verified").
# check_backend <db container> <api container> <executor container> <backend>
# refuses unless the stack is really on <backend>: the variable in both
# query-serving containers, the skycell build pinned by commit and version,
# ivoa.obscore's footprint column of that backend's type, and the cone index
# of that backend on ivoa.obscore. Needs the drivers' `expect` and `fail`.

# skycell release v0.58. Its SQL extension version is not the release tag
# (v0.58 installs extension version 0.50, which several releases may share),
# so the build is identified by the commit db/Dockerfile records in the
# image, and the extension version is checked beside it.
SKYCELL_COMMIT=0d998bd928e026da05631e6f0e9b3b6dbab7570d
SKYCELL_EXTVERSION=0.50

check_backend() {
    local db=$1 api=$2 executor=$3 backend=$4 container
    local psql=(docker exec "$db" psql -U tap -d tap -Atc)
    for container in "$api" "$executor"; do
        expect "$container TAP_GEOMETRY_BACKEND" \
            "$(docker inspect "$container" --format '{{join .Config.Env "\n"}}' \
                | sed -n 's/^TAP_GEOMETRY_BACKEND=//p')" "$backend"
    done
    local column cone
    column=$("${psql[@]}" "select format_type(atttypid, atttypmod) from pg_attribute \
        where attrelid = 'ivoa.obscore'::regclass and attname = 's_region_geom'")
    case $backend in
        skycell)
            expect "$db skycell commit" \
                "$(docker exec "$db" cat /usr/share/skycell/COMMIT)" "$SKYCELL_COMMIT"
            expect "$db skycell extension version" \
                "$("${psql[@]}" "select extversion from pg_extension where extname = 'skycell'")" \
                "$SKYCELL_EXTVERSION"
            expect "$db ivoa.obscore.s_region_geom type" "$column" skyregion
            # the HEALPix cell B-tree that holds the position (docs/deployment.md)
            cone=$("${psql[@]}" "select count(*) from pg_indexes where schemaname = 'ivoa' \
                and tablename = 'obscore' and indexdef ilike '%skycell_ang2cell%'")
            ;;
        pgsphere)
            expect "$db ivoa.obscore.s_region_geom type" "$column" spoly
            cone=$("${psql[@]}" "select count(*) from pg_indexes where schemaname = 'ivoa' \
                and tablename = 'obscore' and indexdef ilike '%gist%spoint%'")
            ;;
        *) fail "unknown backend '$backend'" ;;
    esac
    [ "$cone" -ge 1 ] || fail "$db: no $backend cone index on ivoa.obscore"
}

# refuse_cone_disagreement <gates.json>: the cone classes are what this rerun
# exists to measure, so a disagreement on any of them stops the experiment
# (PROTOCOL.md, "Pre-flight"; amendment 1). `compare --gates-only` itself
# fails only on taplint: a class that fails agreement is excluded and the
# rest measured, which is the base protocols' rule and stays theirs for every
# other class.
CONE_CLASSES="Q05 Q06 Q07 Q12"
refuse_cone_disagreement() {
    local gates=$1 disagreed
    [ -f "$gates" ] || fail "no gate record at $gates"
    disagreed=$(python3 -c '
import json, sys
gates = json.load(open(sys.argv[1]))
if "agreement" not in gates:
    sys.exit("no agreement verdict in " + sys.argv[1])
print(" ".join(sorted(set(gates["agreement"]["disagreed"]) & set(sys.argv[2:]))))
' "$gates" $CONE_CLASSES) || fail "cannot read the agreement verdict in $gates"
    [ -z "$disagreed" ] || fail "cone classes disagree across targets: $disagreed" \
        "($gates) - a skycell correctness finding; nothing is measured (PROTOCOL.md)"
    log "PROGRESS cone classes agree ($CONE_CLASSES)"
}

# -- amendment 2 -------------------------------------------------------------
# DaCHS records every request, sync included, as a UWS job in its own
# database (tap_schema.tapjobs, on a volume). Rows a dead request left
# EXECUTING outlive the container and fill the async run slots, so taplint's
# async check queues forever (the first scaling attempt, 2026-11-19). Each
# DaCHS bring-up starts from an empty job table, as argus's already does.
clear_dachs_jobs() {
    docker exec tap-compare-dachs-1 su postgres -c \
        "psql -Atc 'delete from tap_schema.tapjobs' gavo" > /dev/null
    expect "dachs job table" "$(docker exec tap-compare-dachs-1 su postgres -c \
        "psql -Atc 'select count(*) from tap_schema.tapjobs' gavo")" 0
}

# The evidence a stopped measurement leaves: every server's logs, DaCHS's own
# log files and its postgres log, which die with the container on the next
# --force-recreate (they did on 2026-11-19).
dump_server_logs() {
    local dir=$1 c
    mkdir -p "$dir"
    for c in $(docker ps --format '{{.Names}}' | grep -E '^(egernia|egernia-pgs|tap-compare)-'); do
        docker logs --timestamps "$c" > "$dir/$c.log" 2>&1 || true
    done
    if docker ps --format '{{.Names}}' | grep -qx tap-compare-dachs-1; then
        docker cp tap-compare-dachs-1:/var/gavo/logs "$dir/dachs-gavo-logs" > /dev/null 2>&1 || true
        docker cp tap-compare-dachs-1:/var/log/postgresql "$dir/dachs-postgresql" > /dev/null 2>&1 || true
        docker exec tap-compare-dachs-1 su postgres -c \
            "psql -Atc 'select jobid, phase, starttime from tap_schema.tapjobs' gavo" \
            > "$dir/dachs-tapjobs.txt" 2>&1 || true
    fi
    log "PROGRESS server logs saved to $dir"
}

# A rung over this error fraction stops the run (compare --abort-error-fraction):
# a server that has stopped answering is a finding, not a measurement.
ABORT_ERROR_FRACTION=0.5

# The EXIT trap of experiments 2 and 3: the sampler stops as before, and a
# run that stops after its gates began keeps every server's logs.
stop_and_keep_logs() {
    local rc=$?
    stop_sampler
    if [ "$rc" != 0 ] && [ -n "${RUN_NAME:-}" ]; then
        dump_server_logs "$SUITE/results/$RUN_NAME/logs"
    fi
}

# -- amendment 3 -------------------------------------------------------------
# DaCHS must serve as `gavo`, never root (pins/dachs-as-gavo.sh): as root, its
# os.kill(-1, SIGTERM) on a timed-out sync job shuts PostgreSQL down.
check_dachs_user() {
    expect "dachs serving user" \
        "$(docker exec tap-compare-dachs-1 ps -o user= -p 1 | tr -d ' ')" gavo
    expect "dachs serving command" \
        "$(docker exec tap-compare-dachs-1 ps -o args= -p 1)" "/usr/bin/python3 /usr/bin/dachs serve debug"
}

# Amendment 4: PostgreSQL's /dev/shm is a quarter of the db container's
# memory limit (docs/postgres-performance.md, "Shared memory for parallel
# queries"). The runtime's 64 MiB default is what failed Q13 at 32 clients.
check_shm() {
    local memory shm
    memory=$(docker inspect egernia-db-1 --format '{{.HostConfig.Memory}}')
    shm=$(docker inspect egernia-db-1 --format '{{.HostConfig.ShmSize}}')
    expect "egernia db /dev/shm (a quarter of $memory)" "$shm" "$((memory / 4))"
}

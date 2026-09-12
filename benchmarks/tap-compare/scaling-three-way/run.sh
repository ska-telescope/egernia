#!/usr/bin/env bash
# The three-server resource-scaling driver (PROTOCOL.md): for each tier, bring
# the tier's stacks up under its pins, verify every promise they make before
# anything is timed, run the gates with all three up, then measure — all three
# interleaved at tier 8, one server at a time above it — into ONE run
# directory.
#
#   nohup setsid benchmarks/tap-compare/scaling-three-way/run.sh > s3.log 2>&1 &
#   grep PROGRESS s3.log
#
# Environment: SCENARIO (scaling3 | scaling3-smoke), TIERS ("8 16 24"),
# GEN_CPUS (taskset list for the generator, "24-29"), RUN_NAME (an existing
# run directory to resume), ALLOW_NEIGHBOURS, ALLOW_CONCURRENT.
#
# Requires the seeded egernia volume, DaCHS's ingested data, argus's ingested
# database, and the exported corpus at ../corpus/obscore.csv.
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SUITE=$(dirname "$HERE")
REPO=$(cd "$SUITE/../.." && pwd)
SCENARIO=${SCENARIO:-scaling3}
TIERS=${TIERS:-8 16 24}
GEN_CPUS=${GEN_CPUS:-24-29}
RUN_NAME=${RUN_NAME:-}
ALLOW_NEIGHBOURS=${ALLOW_NEIGHBOURS:-0}
CLASSES=${CLASSES:-Q01 Q05 Q11 Q13 mix}

# Explicit compose project names: the volumes and container names this
# benchmark's data lives in belong to the projects `egernia` (the repo root)
# and `tap-compare` (this suite). A checkout in a differently named directory
# — a git worktree, say — would otherwise create empty new ones.
EGERNIA_PROJECT=egernia
SUITE_PROJECT=tap-compare

TARGETS="egernia-scaling3 dachs-scaling3 argus-scaling3"
EGERNIA_URL=http://localhost:8080/tap
DACHS_URL=http://localhost:8081/tap
ARGUS_URL=http://localhost/argus
EGERNIA_CONTAINERS="egernia-db-1 egernia-tap-api-1 egernia-tap-executor-1"
DACHS_CONTAINERS="tap-compare-dachs-1"
ARGUS_CONTAINERS="tap-compare-argus-1 tap-compare-argus-db-1"
EXPECTED_ROWS=500096
EXPECTED_FKS=16
EXPECTED_CORPUS_SHA=bc4110500860dfdf09377bf1c1442220c424a8edd58217e21d78734b009f6007
NEIGHBOUR_CPU_PERCENT_MAX=50
SAMPLER_PID=""

# the order the servers are measured in, per tier: alternated so host drift
# over a tier's hours does not always land on the same server (PROTOCOL.md)
order_for() {
    case $1 in
        16) echo "egernia dachs argus" ;;
        *) echo "argus dachs egernia" ;;
    esac
}
server_of() { case $1 in egernia) echo egernia-scaling3 ;; dachs) echo dachs-scaling3 ;; argus) echo argus-scaling3 ;; esac; }

stop_sampler() {
    [ -n "$SAMPLER_PID" ] || return 0
    kill "$SAMPLER_PID" 2>/dev/null || true
    echo "$(date -u +%FT%TZ) PROGRESS sampler stopped pid=$SAMPLER_PID"
    SAMPLER_PID=""
}
trap stop_sampler EXIT INT TERM

log() { echo "$(date -u +%FT%TZ) $*"; }
fail() { log "FAIL $*"; exit 1; }
fail_early() { echo "FAIL $*" >&2; exit 1; }
expect() { [ "$2" = "$3" ] || fail "$1: got '$2', expected '$3'"; }

# The generator's cores must be disjoint from every tier's server cpusets: a
# generator sharing a measured stack's cores reports its own contention as the
# server's. The largest tier claims 0-23, so that is what GEN_CPUS is checked
# against, and an override is validated here rather than trusted.
GEN_CORES=$(python3 -c '
import sys

def cores(spec):
    out = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return out

generator, servers = cores(sys.argv[1]), cores(sys.argv[2])
print(" ".join(str(c) for c in sorted(generator)))
sys.exit(1 if not generator or (generator & servers) else 0)
' "$GEN_CPUS" "0-23") \
    || fail_early "GEN_CPUS='$GEN_CPUS' is empty, malformed, or overlaps the" \
        "server cores 0-23 that the largest tier claims"

tap() {
    (cd "$REPO" && taskset -c "$GEN_CPUS" uv run --group tap-compare \
        python benchmarks/tap-compare --config-dir "$HERE" "$@")
}
compose_egernia() {
    docker compose -p "$EGERNIA_PROJECT" -f "$REPO/docker-compose.yml" \
        -f "$HERE/pins/egernia-$1.yml" "${@:2}"
}
compose_dachs() {
    docker compose -p "$SUITE_PROJECT" -f "$SUITE/docker-compose.dachs.yml" \
        -f "$HERE/pins/dachs-$1.yml" "${@:2}"
}
compose_argus() {
    docker compose -p "$SUITE_PROJECT" -f "$SUITE/docker-compose.argus.yml" \
        -f "$HERE/pins/argus-$1.yml" "${@:2}"
}
pg_egernia() { docker exec egernia-db-1 psql -U tap -d tap -Atc "$1"; }
pg_dachs() { docker exec tap-compare-dachs-1 su postgres -c "psql -Atc \"$1\" gavo"; }
pg_argus() { docker exec tap-compare-argus-db-1 psql -U tap -d argus -Atc "$1"; }
promised() { grep -o "$2=[^ \"]*" "$1" | head -1 | cut -d= -f2; }
promised_workers() { grep -o 'TAP_API_WORKERS: "[0-9]*"' "$1" | grep -o '[0-9]*'; }
cpuset_of() { grep -o 'cpuset: "[0-9-]*"' "$1" | head -1 | sed 's/.*"\(.*\)"/\1/'; }
SHOW_SETTINGS="select name || ' = ' || current_setting(name) from pg_settings where name in \
    ('shared_buffers', 'effective_cache_size', 'work_mem', 'max_parallel_workers', \
    'max_worker_processes', 'max_connections')"

wait_tap() {
    for _ in $(seq 1 120); do
        curl -fsS -o /dev/null "$1/capabilities" && return 0
        sleep 5
    done
    fail "$1 did not answer within 10 minutes"
}

check_cpuset() {
    local expected=$1
    shift
    for container in "$@"; do
        expect "$container cpuset" \
            "$(docker inspect "$container" --format '{{.HostConfig.CpusetCpus}}')" "$expected"
    done
}

# Every core of this host belongs to a server stack or to the generator, so a
# pinned foreign container is no safer than an unpinned one.
HOT=""
check_neighbours() {
    local ours=" $EGERNIA_CONTAINERS $DACHS_CONTAINERS $ARGUS_CONTAINERS "
    HOT=""
    while read -r name cpu cpuset; do
        case $ours in *" $name "*) continue ;; esac
        if awk -v c="${cpu%\%}" -v max="$NEIGHBOUR_CPU_PERCENT_MAX" \
            'BEGIN {exit !(c > max)}'; then
            HOT="$HOT $name($cpu on cpuset '${cpuset:-none}')"
        fi
    done < <(docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' \
        | while read -r n c; do
            printf '%s %s %s\n' "$n" "$c" \
                "$(docker inspect "$n" --format '{{.HostConfig.CpusetCpus}}' 2>/dev/null)"
          done)
    log "PROGRESS neighbours hot='${HOT:-none}'"
    if [ -n "$HOT" ] && [ "$ALLOW_NEIGHBOURS" != 1 ]; then
        fail "foreign containers are burning CPU:$HOT — pin them off the" \
            "benchmark's cores or stop them, or set ALLOW_NEIGHBOURS=1"
    fi
}

up_egernia() {
    local tier=$1 pins="$HERE/pins/egernia-$tier.yml"
    log "PROGRESS tier=$tier server=egernia step=up"
    compose_egernia "$tier" up -d --no-build --force-recreate db tap-api tap-executor
    wait_tap $EGERNIA_URL
    expect "egernia rows" "$(pg_egernia 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
    expect "egernia ivoa.obscore relkind" \
        "$(pg_egernia "select relkind from pg_class where oid = 'ivoa.obscore'::regclass")" r
    expect "egernia foreign keys" "$(pg_egernia "select count(*) from pg_constraint \
        where contype = 'f' and connamespace = 'srcnet'::regnamespace")" $EXPECTED_FKS
    for container in egernia-tap-api-1 egernia-tap-executor-1; do
        [ -z "$(docker inspect "$container" --format '{{join .Config.Env "\n"}}' \
            | grep '^TAP_QUERY_DATABASE_URL=' || true)" ] \
            || fail "$container has TAP_QUERY_DATABASE_URL set;" \
                "this protocol measures one database"
    done
    for setting in shared_buffers effective_cache_size work_mem max_parallel_workers \
        max_worker_processes; do
        expect "egernia $setting" "$(pg_egernia "show $setting")" "$(promised "$pins" $setting)"
    done
    local workers processes minimum
    workers=$(promised_workers "$pins")
    expect "egernia container TAP_API_WORKERS" \
        "$(docker inspect egernia-tap-api-1 --format '{{join .Config.Env "\n"}}' \
            | sed -n 's/^TAP_API_WORKERS=//p')" "$workers"
    processes=$(docker top egernia-tap-api-1 -o pid,args | grep -c '/srv/.venv/bin/python')
    minimum=$([ "$workers" = 1 ] && echo 1 || echo $((workers + 1)))
    [ "$processes" -ge "$minimum" ] || fail "egernia api processes: $processes < $minimum"
    check_cpuset "$(cpuset_of "$pins")" $EGERNIA_CONTAINERS
}

up_dachs() {
    local tier=$1
    log "PROGRESS tier=$tier server=dachs step=up"
    compose_dachs "$tier" up -d --no-build --force-recreate
    wait_tap $DACHS_URL
    expect "dachs rows" "$(pg_dachs 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
    for setting in shared_buffers effective_cache_size max_parallel_workers \
        max_worker_processes; do
        expect "dachs $setting" "$(pg_dachs "show $setting")" \
            "$(awk -v s=$setting '$1 == s {print $3}' "$HERE/pins/dachs-postgres-$tier.conf")"
    done
    check_cpuset "$(cpuset_of "$HERE/pins/dachs-$tier.yml")" $DACHS_CONTAINERS
}

up_argus() {
    local tier=$1 pins="$HERE/pins/argus-$tier.yml"
    log "PROGRESS tier=$tier server=argus step=up"
    compose_argus "$tier" up -d --no-build --force-recreate
    wait_tap $ARGUS_URL
    expect "argus rows" "$(pg_argus 'select count(*) from caom2.obscore')" $EXPECTED_ROWS
    expect "argus caom2.obscore relkind" "$(pg_argus "select c.relkind::text from pg_class c \
        join pg_namespace n on n.oid = c.relnamespace \
        where n.nspname = 'caom2' and c.relname = 'obscore'")" r
    for setting in shared_buffers effective_cache_size max_parallel_workers \
        max_worker_processes; do
        expect "argus $setting" "$(pg_argus "show $setting")" "$(promised "$pins" $setting)"
    done
    truncate_argus_jobs
    check_cpuset "$(cpuset_of "$pins")" $ARGUS_CONTAINERS
}

# argus's throughput decays with its own UWS history, so every block starts
# from the same empty store (PROTOCOL.md, "argus").
truncate_argus_jobs() {
    pg_argus "truncate uws.jobdetail, uws.job" > /dev/null
    expect "argus job store" "$(pg_argus 'select count(*) from uws.job')" 0
}

up_server() { case $1 in egernia) up_egernia "$2" ;; dachs) up_dachs "$2" ;; argus) up_argus "$2" ;; esac; }

# The gates' sync probes and the warm pass are synchronous requests, and argus
# persists a UWS job for every one of them — so a block that truncated only at
# `up` would still start on a few hundred rows, and on a *different* few
# hundred at each tier (tier 8 warms three servers, the others warm one). That
# would put history on the tier axis. Truncate again immediately before every
# measured block; a no-op when argus is stopped, which is every non-argus
# block above tier 8.
truncate_argus_jobs_if_up() {
    [ "$(docker inspect -f '{{.State.Running}}' tap-compare-argus-db-1 2>/dev/null)" = true ] \
        || return 0
    truncate_argus_jobs
    log "PROGRESS argus job store emptied before the measured block"
}

down_server() {
    log "PROGRESS tier=$2 server=$1 step=down"
    case $1 in
        egernia) compose_egernia "$2" stop db tap-api tap-executor ;;
        dachs) compose_dachs "$2" stop ;;
        argus) compose_argus "$2" stop ;;
    esac
}

record_host() {
    local tier=$1 dir="$SUITE/results/$RUN_NAME/pins"
    mkdir -p "$dir"
    {
        echo "# $(date -u +%FT%TZ) tier $tier, host"
        echo "generator_cpus=$GEN_CPUS"
        echo "generator_cores=$GEN_CORES"
        echo "generator_processes=$(awk -v s="  $SCENARIO:" '$0 == s {f = 1} \
            f && /generator_processes:/ {print $2; exit}' "$HERE/scenarios.yaml")"
        echo "classes=$CLASSES"
        echo "order=$(order_for "$tier")"
        echo "allow_neighbours=$ALLOW_NEIGHBOURS"
        echo "neighbours_hot=${HOT:-none}"
        echo "## docker stats (all containers, name / cpu / mem / cpuset)"
        docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}' \
            | while read -r n rest; do
                printf '%s %s cpuset=%s\n' "$n" "$rest" \
                    "$(docker inspect "$n" --format '{{.HostConfig.CpusetCpus}}' 2>/dev/null)"
              done
    } > "$dir/t$tier-host.txt"
}

record() {
    local server=$1 tier=$2 dir="$SUITE/results/$RUN_NAME/pins" containers
    mkdir -p "$dir"
    case $server in
        egernia) containers="$EGERNIA_CONTAINERS" ;;
        dachs) containers="$DACHS_CONTAINERS" ;;
        argus) containers="$ARGUS_CONTAINERS" ;;
    esac
    # shellcheck disable=SC2086
    docker inspect $containers --format '{{json .HostConfig}}' | python3 -c '
import json, sys
print(json.dumps([{k: h[k] for k in ("CpusetCpus", "NanoCpus", "Memory")}
                  for h in map(json.loads, sys.stdin)], indent=2))' > "$dir/t$tier-$server.json"
    {
        echo "# $(date -u +%FT%TZ) tier $tier $server"
        for c in $containers; do
            echo "## $c"
            docker inspect "$c" --format 'cpuset={{.HostConfig.CpusetCpus}} nanocpus={{.HostConfig.NanoCpus}} memory={{.HostConfig.Memory}}'
            docker inspect "$c" --format '{{join .Config.Cmd " "}}'
            docker inspect "$c" --format '{{join .Config.Env "\n"}}' | grep -E '^TAP_API_WORKERS=' || true
            docker top "$c" -o pid,args | sed 's/^/  /'
        done
        echo "## SHOW"
        case $server in
            egernia) pg_egernia "$SHOW_SETTINGS" ;;
            dachs) pg_dachs "$SHOW_SETTINGS" ;;
            argus) pg_argus "$SHOW_SETTINGS"; echo "## uws.job rows"; pg_argus 'select count(*) from uws.job' ;;
        esac
    } > "$dir/t$tier-$server.txt"
}

start_sampler() {
    local samples="$SUITE/results/$RUN_NAME/resources.jsonl"
    if pgrep -f "sample_resources.sh $samples" > /dev/null; then
        log "PROGRESS sampler already running for $samples (not ours; left alone)"
        return 0
    fi
    [ -n "$SAMPLER_PID" ] && return 0
    taskset -c "$GEN_CPUS" "$SUITE/scaling/sample_resources.sh" "$samples" > /dev/null 2>&1 &
    SAMPLER_PID=$!
    log "PROGRESS sampler pid=$SAMPLER_PID -> $samples"
}

# The interlock: this driver's first act is to recreate stacks, which rewrites
# the pins of whatever is running on them. Exclusion is by identity — our
# ancestors (the launching shell carries this script's path) and our own
# session — never by string. `|| true`: pgrep exits 1 when nothing matches,
# which is the good case, and pipefail would otherwise kill the driver.
mine=" $$ "
walk=$$
while [ -n "$walk" ] && [ "$walk" != 0 ] && [ "$walk" != 1 ]; do
    walk=$(ps -o ppid= -p "$walk" 2>/dev/null | tr -d ' ')
    [ -n "$walk" ] && mine="$mine$walk "
done
mysid=$(ps -o sid= -p $$ | tr -d ' ')
others=$({ pgrep -af 'benchmarks/tap-compare +(--config-dir|compare|run|publish|gates)' \
    || true; } | while read -r p args; do
        case $mine in *" $p "*) continue ;; esac
        if [ "$(ps -o sid= -p "$p" 2>/dev/null | tr -d ' ')" = "$mysid" ]; then
            continue
        fi
        echo "$p $args"
      done)
if [ -n "$others" ] && [ "${ALLOW_CONCURRENT:-0}" != 1 ]; then
    log "$others"
    fail_early "another tap-compare measurement is running (above): recreating the" \
        "stacks now would rewrite its pins mid-rung. Wait for it, or set" \
        "ALLOW_CONCURRENT=1 if you know it is finished."
fi

log "PROGRESS start scenario=$SCENARIO tiers='$TIERS' classes='$CLASSES' generator_cpus=$GEN_CPUS"
expect "corpus sha256" "$(sha256sum "$SUITE/corpus/obscore.csv" | cut -d' ' -f1)" \
    "$EXPECTED_CORPUS_SHA"
check_neighbours

for tier in $TIERS; do
    ORDER=$(order_for "$tier")
    log "PROGRESS tier=$tier order='$ORDER'"
    # every server up for the gates, whatever the tier measures afterwards
    up_egernia "$tier"
    up_dachs "$tier"
    up_argus "$tier"

    log "PROGRESS tier=$tier step=gates"
    # shellcheck disable=SC2086
    if [ -z "$RUN_NAME" ]; then
        tap compare --targets $TARGETS --scenario "$SCENARIO" --tier "$tier" --gates-only
        RUN_NAME=$(basename "$(ls -td "$SUITE"/results/*-tap-compare-scaling | head -1)")
        log "PROGRESS run=$RUN_NAME"
    else
        tap compare --targets $TARGETS --scenario "$SCENARIO" --tier "$tier" --gates-only \
            --resume "$RUN_NAME"
    fi
    for s in egernia dachs argus; do record "$s" "$tier"; done
    record_host "$tier"
    start_sampler

    if [ "$tier" = 8 ]; then
        # all three fit: interleave A,B,C inside every cell
        for target in $TARGETS; do
            log "PROGRESS tier=$tier step=warm target=$target"
            tap run --target "$target" --scenario warm
        done
        truncate_argus_jobs_if_up
        log "PROGRESS tier=$tier step=measure interleaved"
        # shellcheck disable=SC2086
        tap compare --targets $TARGETS --scenario "$SCENARIO" --tier "$tier" \
            --classes $CLASSES --resume "$RUN_NAME"
    else
        for server in $ORDER; do
            for other in egernia dachs argus; do
                [ "$other" = "$server" ] || down_server "$other" "$tier"
            done
            # a restarted-alone stack is re-verified and re-recorded, and argus
            # starts its block with an empty job store
            up_server "$server" "$tier"
            record "$server" "$tier"
            local_target=$(server_of "$server")
            log "PROGRESS tier=$tier step=warm target=$local_target"
            tap run --target "$local_target" --scenario warm
            truncate_argus_jobs_if_up
            log "PROGRESS tier=$tier step=measure target=$local_target"
            # shellcheck disable=SC2086
            tap compare --targets $TARGETS --scenario "$SCENARIO" --tier "$tier" \
                --only "$local_target" --classes $CLASSES --resume "$RUN_NAME"
            log "PROGRESS tier=$tier step=done target=$local_target"
        done
    fi
done

stop_sampler
log "PROGRESS complete run=$RUN_NAME"
log "publish with: uv run --group tap-compare python benchmarks/tap-compare publish --run $RUN_NAME"

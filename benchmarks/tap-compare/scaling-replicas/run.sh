#!/usr/bin/env bash
# The read-replica tier driver (PROTOCOL.md): three shapes of the same
# 24-CPU/24-GiB egernia stack — the published tier-24 shape re-measured (24b),
# the same with 8 API workers (24w), and 8 workers over one primary plus three
# streaming standbys (24r) — measured one after another into ONE run
# directory, recording what `docker inspect`, `SHOW` and
# `pg_stat_replication` actually saw.
#
#   nohup setsid benchmarks/tap-compare/scaling-replicas/run.sh > replicas.log 2>&1 &
#   grep PROGRESS replicas.log
#
# Environment: SCENARIO (scaling | scaling-smoke), TIERS ("24b 24r 24w"),
# GEN_CPUS (taskset list for the generator, "24-29"), RUN_NAME (an existing
# run directory to resume), RESTORE (1: end on the pins the stack was found
# under). Requires the seeded egernia volume and images built from a tree that
# carries BOTH TAP_QUERY_DATABASE_URL and PR #160's ivoa.obscore table (the
# volume's obscore is that table; an API without its bootstrap cannot start
# against it).
#
# The standbys clone the primary on first start and keep their volumes. There
# are no replication slots (PROTOCOL.md), so a standby left stopped while the
# primary generated WAL can come back too far behind to catch up — its log
# says "requested WAL segment has already been removed". The fix is to let it
# clone again: `docker compose ... rm -sf db-standby-N && docker volume rm
# egernia_pgdata-standby-N`, then re-run.
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SUITE=$(dirname "$HERE")
SCALING="$SUITE/scaling"
REPO=$(cd "$SUITE/../.." && pwd)
SCENARIO=${SCENARIO:-scaling}
TIERS=${TIERS:-24b 24r 24w}
GEN_CPUS=${GEN_CPUS:-24-29}
RUN_NAME=${RUN_NAME:-}
RESTORE=${RESTORE:-1}
TARGET=egernia-local
EGERNIA_URL=http://localhost:8080/tap
EXPECTED_ROWS=500096
EXPECTED_FKS=16
# The classes the protocol restricts the grid to; 24w is the worker control
# and runs the mixed workload only.
CLASSES="Q01 Q03 Q04 Q10 Q11 Q13 mix"
CONTROL_CLASSES="mix"
# The pins the stack is handed back to (RESTORE=1): the shape it was found
# under, so a neighbouring experiment is not left re-pinned.
RESTORE_PINS="$SUITE/argus-equal-cpu/egernia-equalcpu.yml"

log() { echo "$(date -u +%FT%TZ) $*"; }
fail() { log "FAIL $*"; exit 1; }
expect() { [ "$2" = "$3" ] || fail "$1: got '$2', expected '$3'"; }

tap() {
    (cd "$REPO" && taskset -c "$GEN_CPUS" uv run --group tap-compare \
        python benchmarks/tap-compare --config-dir "$SCALING" "$@")
}
# 24b reuses the published tier-24 pins unmodified; the other two have their own.
pins() {
    case $1 in
        24b) echo "$SCALING/pins/egernia-24.yml" ;;
        *) echo "$HERE/pins/egernia-$1.yml" ;;
    esac
}
compose() { docker compose -f "$REPO/docker-compose.yml" -f "$(pins "$1")" "${@:2}"; }
services() {
    if [ "$1" = 24r ]; then
        echo "db db-standby-1 db-standby-2 db-standby-3 tap-api tap-executor"
    else
        echo "db tap-api tap-executor"
    fi
}
standbys() { echo "egernia-db-standby-1-1 egernia-db-standby-2-1 egernia-db-standby-3-1"; }
pg() { docker exec "$1" psql -U tap -d tap -Atc "$2"; }
# setting <tier> <name> [standby]: what the pins promise for that server. The
# standbys' flags live in their own command block with different values from
# the primary's, so the lookup has to be scoped to one block.
setting() {
    local file; file=$(pins "$1")
    if [ "${3:-}" = standby ]; then
        sed -n '/db-standby-1:/,/^  tap-api:/p' "$file"
    else
        sed -n '/^  db:/,/^  db-standby-1:/p' "$file"
    fi | grep -o "$2=[^ ]*" | head -1 | cut -d= -f2
}
SHOW_SETTINGS="select name || ' = ' || current_setting(name) from pg_settings where name in \
    ('shared_buffers', 'effective_cache_size', 'work_mem', 'max_parallel_workers', \
    'max_worker_processes', 'max_connections', 'hot_standby_feedback')"

wait_tap() {
    for _ in $(seq 1 120); do
        curl -fsS -o /dev/null "$EGERNIA_URL/capabilities" && return 0
        sleep 5
    done
    fail "$EGERNIA_URL did not answer within 10 minutes"
}

# up <tier>: (re)create under the tier's pins, wait, verify the data, the
# settings the pins promised, and (24r) that replication is actually running.
up() {
    local tier=$1
    log "PROGRESS tier=$tier phase=up"
    # shellcheck disable=SC2046
    compose "$tier" up -d --no-build --force-recreate $(services "$tier")
    wait_tap
    expect "obscore rows" "$(pg egernia-db-1 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
    # every tier must see the same ivoa.obscore: PR #160's table, not the view
    # the published scaling run measured (PROTOCOL.md, "Why the published
    # tier 24 is not the baseline")
    expect "obscore is a table" \
        "$(pg egernia-db-1 "select relkind from pg_class where relname = 'obscore' \
            and relnamespace = 'ivoa'::regnamespace")" "r"
    expect "foreign keys" "$(pg egernia-db-1 "select count(*) from pg_constraint \
        where contype = 'f' and connamespace = 'srcnet'::regnamespace")" $EXPECTED_FKS
    for s in shared_buffers effective_cache_size max_parallel_workers max_worker_processes; do
        expect "primary $s" "$(pg egernia-db-1 "show $s")" "$(setting "$tier" $s)"
    done
    local workers processes minimum
    workers=$(grep -o 'TAP_API_WORKERS: "[0-9]*"' "$(pins "$tier")" | grep -o '[0-9]*')
    # one process for a single worker; a supervisor plus one per worker above that
    processes=$(docker top egernia-tap-api-1 -o pid,args | grep -c '/srv/.venv/bin/python')
    minimum=$([ "$workers" = 1 ] && echo 1 || echo $((workers + 1)))
    [ "$processes" -ge "$minimum" ] || fail "api processes: $processes < $minimum"
    [ "$tier" = 24r ] || return 0

    expect "streaming standbys" \
        "$(pg egernia-db-1 "select count(*) from pg_stat_replication where state = 'streaming'")" 3
    for c in $(standbys); do
        expect "$c in recovery" "$(pg "$c" 'select pg_is_in_recovery()')" "t"
        expect "$c rows" "$(pg "$c" 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
        expect "$c pgsphere" "$(pg "$c" "select count(*) from pg_extension where extname = 'pg_sphere'")" 1
        for s in shared_buffers effective_cache_size max_parallel_workers hot_standby_feedback; do
            expect "$c $s" "$(pg "$c" "show $s")" "$(setting "$tier" $s standby)"
        done
    done
    # the API must be pointed at all three, or this tier measures nothing new
    local query_url
    query_url=$(docker inspect egernia-tap-api-1 --format '{{join .Config.Env "\n"}}' |
        grep '^TAP_QUERY_DATABASE_URL=' || true)
    for i in 1 2 3; do
        case $query_url in *db-standby-$i:5432*) ;; *) fail "api query URL misses standby $i" ;; esac
    done
}

down() {
    log "PROGRESS tier=$1 phase=down"
    # shellcheck disable=SC2046
    compose "$1" stop $(services "$1")
}

# record <tier>: the pins as applied, plus the neighbours that share the host.
record() {
    local tier=$1 dir="$SUITE/results/$RUN_NAME/pins" containers
    mkdir -p "$dir"
    containers="egernia-db-1 egernia-tap-api-1 egernia-tap-executor-1"
    if [ "$tier" = 24r ]; then containers="$containers $(standbys)"; fi
    # shellcheck disable=SC2086
    docker inspect $containers --format '{{json .HostConfig}}' | python3 -c '
import json, sys
print(json.dumps([{k: h[k] for k in ("CpusetCpus", "NanoCpus", "Memory")}
                  for h in map(json.loads, sys.stdin)], indent=2))' > "$dir/t$tier-$TARGET.json"
    {
        echo "# $(date -u +%FT%TZ) tier $tier, order: $TIERS"
        for c in $containers; do
            echo "## $c"
            docker inspect "$c" --format 'cpuset={{.HostConfig.CpusetCpus}} nanocpus={{.HostConfig.NanoCpus}} memory={{.HostConfig.Memory}}'
            docker inspect "$c" --format '{{join .Config.Cmd " "}}'
            docker inspect "$c" --format '{{join .Config.Env "\n"}}' |
                grep -E '^(TAP_API_WORKERS|TAP_QUERY_DATABASE_URL)=' || true
            docker top "$c" -o pid,args | sed 's/^/  /'
            echo "### SHOW"
            pg "$c" "$SHOW_SETTINGS" 2>/dev/null || true
        done
        echo "## replication"
        pg egernia-db-1 "select client_addr || ' ' || state || ' write=' || coalesce(write_lag::text, '-') \
            || ' flush=' || coalesce(flush_lag::text, '-') || ' replay=' || coalesce(replay_lag::text, '-') \
            from pg_stat_replication" || true
        echo "## host neighbours (unpinned toolkit containers widen the spread)"
        docker ps --filter name=toolkit --format '{{.Names}} {{.Status}}'
    } > "$dir/t$tier-$TARGET.txt"
}

# lag_probe: the consistency window, measured rather than asserted. Written
# and read inside the database (a shell round trip is ~200 ms and would
# swamp a lag of a few milliseconds), ten small writes with the standbys'
# reported write/flush/replay lag after each. Untimed, outside the grid; the
# measured rungs write nothing.
lag_probe() {
    local out="$SUITE/results/$RUN_NAME/lag-probe.json"
    log "PROGRESS tier=24r phase=lag-probe"
    pg egernia-db-1 "create table if not exists public.lag_probe(n int primary key)" > /dev/null
    {
        echo "["
        for n in $(seq 1 10); do
            pg egernia-db-1 "insert into public.lag_probe(n) values ($n)" > /dev/null
            pg egernia-db-1 "select json_build_object('probe', $n, 'standbys', \
                coalesce(json_agg(json_build_object('client_addr', client_addr, 'state', state, \
                    'write_lag', write_lag, 'flush_lag', flush_lag, 'replay_lag', replay_lag)), '[]'::json)) \
                from pg_stat_replication"
            [ "$n" = 10 ] || echo ","
        done
        echo "]"
    } > "$out"
    pg egernia-db-1 "drop table public.lag_probe" > /dev/null
    log "PROGRESS tier=24r phase=lag-probe-done out=$out"
}

measure() {
    local tier=$1 classes=$2
    log "PROGRESS tier=$tier phase=warm"
    tap run --target "$TARGET" --scenario warm
    log "PROGRESS tier=$tier phase=measure classes='$classes'"
    # shellcheck disable=SC2086
    tap compare --targets "$TARGET" --scenario "$SCENARIO" --tier "$tier" \
        --only "$TARGET" --classes $classes --resume "$RUN_NAME"
    log "PROGRESS tier=$tier phase=done"
}

if docker ps --filter name=toolkit --format '{{.Names}}' | grep -qE 'toolkit-(4|6)$'; then
    fail "toolkit-4/toolkit-6 are running: unpinned neighbours burning 1-2 cores (PROTOCOL.md)"
fi

log "PROGRESS start scenario=$SCENARIO tiers='$TIERS' generator_cpus=$GEN_CPUS"
for tier in $TIERS; do
    up "$tier"
    log "PROGRESS tier=$tier phase=gates"
    if [ -z "$RUN_NAME" ]; then
        tap compare --targets "$TARGET" --scenario "$SCENARIO" --tier "$tier" --gates-only
        RUN_NAME=$(basename "$(ls -td "$SUITE"/results/*-tap-compare-scaling | head -1)")
        log "PROGRESS run=$RUN_NAME"
    else
        tap compare --targets "$TARGET" --scenario "$SCENARIO" --tier "$tier" --gates-only \
            --resume "$RUN_NAME"
    fi
    # resource telemetry beside the run, on the generator's cores; a resumed
    # run gets it too, and never twice
    if ! pgrep -f "[s]ample_resources.sh" > /dev/null; then
        nohup setsid taskset -c "$GEN_CPUS" "$SCALING/sample_resources.sh" \
            "$SUITE/results/$RUN_NAME/resources.jsonl" > /dev/null 2>&1 &
        log "PROGRESS sampler=started"
    fi
    record "$tier"
    if [ "$tier" = 24r ]; then lag_probe; fi
    if [ "$tier" = 24w ]; then measure "$tier" "$CONTROL_CLASSES"; else measure "$tier" "$CLASSES"; fi
    down "$tier"
done

if [ "$RESTORE" = 1 ]; then
    log "PROGRESS phase=restore ($RESTORE_PINS)"
    docker compose -f "$REPO/docker-compose.yml" -f "$RESTORE_PINS" \
        up -d --no-build --force-recreate db tap-api tap-executor
fi
log "PROGRESS complete run=$RUN_NAME"
log "publish with: uv run --group tap-compare python benchmarks/tap-compare publish --run $RUN_NAME"

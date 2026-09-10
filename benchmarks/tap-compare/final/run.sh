#!/usr/bin/env bash
# The final three-way comparison driver (PROTOCOL.md): bring all three stacks
# up on their disjoint cpusets under one phase's pins, verify every promise
# the pins make before anything is timed, run the three-way gates, then
# measure one interleaved run (egernia, DaCHS, argus round-robin per cell)
# into one run directory.
#
#   nohup setsid PHASE=a benchmarks/tap-compare/final/run.sh > final-a.log 2>&1 &
#   grep PROGRESS final-a.log
#
# Environment: PHASE (a: TAP_API_WORKERS=1 | b: 8), SCENARIO (final |
# final-smoke), GEN_CPUS (taskset list for the generator, "24-29"), RUN_NAME
# (an existing run directory to resume), RESTORE (1: leave the stacks up on
# their pins; 0: stop them at the end), ALLOW_NEIGHBOURS (1: measure even
# though an unpinned foreign container is burning CPU).
#
# Requires the seeded egernia volume, DaCHS's ingested data, argus's ingested
# database, and the exported corpus at ../corpus/obscore.csv.
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SUITE=$(dirname "$HERE")
REPO=$(cd "$SUITE/../.." && pwd)
PHASE=${PHASE:?set PHASE=a (one API worker) or PHASE=b (eight)}
SCENARIO=${SCENARIO:-final}
GEN_CPUS=${GEN_CPUS:-24-29}
RUN_NAME=${RUN_NAME:-}
RESTORE=${RESTORE:-1}
ALLOW_NEIGHBOURS=${ALLOW_NEIGHBOURS:-0}

# Explicit compose project names: the volumes and container names this
# benchmark's data lives in belong to the projects `egernia` (the repo root)
# and `tap-compare` (this suite). A checkout in a differently named directory
# — a git worktree, say — would otherwise create empty new ones.
EGERNIA_PROJECT=egernia
SUITE_PROJECT=tap-compare

case $PHASE in
    a) EGERNIA_TARGET=egernia-final-w1; EGERNIA_PINS="$HERE/pins/egernia-w1.yml"
       EGERNIA_SETTINGS="$REPO/docker-compose.yml"; WORKERS=1 ;;
    b) EGERNIA_TARGET=egernia-final-w8; EGERNIA_PINS="$HERE/pins/egernia-w8.yml"
       EGERNIA_SETTINGS="$HERE/pins/egernia-w8.yml"; WORKERS=8 ;;
    *) echo "PHASE must be a or b, not '$PHASE'" >&2; exit 2 ;;
esac
TARGETS="$EGERNIA_TARGET dachs-final argus-final"

EGERNIA_URL=http://localhost:8080/tap
DACHS_URL=http://localhost:8081/tap
ARGUS_URL=http://localhost/argus
EGERNIA_CONTAINERS="egernia-db-1 egernia-tap-api-1 egernia-tap-executor-1"
DACHS_CONTAINERS="tap-compare-dachs-1"
ARGUS_CONTAINERS="tap-compare-argus-1 tap-compare-argus-db-1"
EXPECTED_ROWS=500096
EXPECTED_FKS=16
EXPECTED_CORPUS_SHA=bc4110500860dfdf09377bf1c1442220c424a8edd58217e21d78734b009f6007
# each stack's own eight cores, and the six the generator keeps (PROTOCOL.md)
EGERNIA_CPUSET=0-7
ARGUS_CPUSET=8-15
DACHS_CPUSET=16-23
# a foreign, unpinned container busier than this (percent of one core, as
# `docker stats` reports it) widens the spread of the fast classes by
# 10-20% (learned 2026-09-09 from the unpinned toolkit containers)
NEIGHBOUR_CPU_PERCENT_MAX=50

log() { echo "$(date -u +%FT%TZ) $*"; }
fail() { log "FAIL $*"; exit 1; }
expect() { [ "$2" = "$3" ] || fail "$1: got '$2', expected '$3'"; }

tap() {
    (cd "$REPO" && taskset -c "$GEN_CPUS" uv run --group tap-compare \
        python benchmarks/tap-compare --config-dir "$HERE" "$@")
}
compose_egernia() {
    docker compose -p "$EGERNIA_PROJECT" -f "$REPO/docker-compose.yml" \
        -f "$EGERNIA_PINS" "$@"
}
compose_dachs() {
    docker compose -p "$SUITE_PROJECT" -f "$SUITE/docker-compose.dachs.yml" \
        -f "$HERE/pins/dachs.yml" "$@"
}
compose_argus() {
    docker compose -p "$SUITE_PROJECT" -f "$SUITE/docker-compose.argus.yml" \
        -f "$HERE/pins/argus.yml" "$@"
}
pg_egernia() { docker exec egernia-db-1 psql -U tap -d tap -Atc "$1"; }
pg_dachs() { docker exec tap-compare-dachs-1 su postgres -c "psql -Atc \"$1\" gavo"; }
pg_argus() { docker exec tap-compare-argus-db-1 psql -U tap -d argus -Atc "$1"; }
# the value a compose file's `postgres -c setting=value` promises
promised() { grep -o "$2=[^ \"]*" "$1" | head -1 | cut -d= -f2; }
# the worker count a compose file's `TAP_API_WORKERS: "n"` promises
promised_workers() { grep -o 'TAP_API_WORKERS: "[0-9]*"' "$1" | grep -o '[0-9]*'; }
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

# cpusets: every container of a stack on exactly the cores the protocol gives it
check_cpuset() {
    local expected=$1
    shift
    for container in "$@"; do
        expect "$container cpuset" \
            "$(docker inspect "$container" --format '{{.HostConfig.CpusetCpus}}')" "$expected"
    done
}

# A foreign container with no cpuset floats onto the pinned cores. Ours are
# pinned; anything else that is busy is a measurement hazard, not noise.
check_neighbours() {
    local ours=" $EGERNIA_CONTAINERS $DACHS_CONTAINERS $ARGUS_CONTAINERS " hot=""
    while read -r name cpu; do
        case $ours in *" $name "*) continue ;; esac
        if [ -n "$(docker inspect "$name" --format '{{.HostConfig.CpusetCpus}}')" ]; then
            continue  # pinned: it cannot reach a measured stack's cores
        fi
        if awk -v c="${cpu%\%}" -v max="$NEIGHBOUR_CPU_PERCENT_MAX" \
            'BEGIN {exit !(c > max)}'; then
            hot="$hot $name($cpu)"
        fi
    done < <(docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}')
    log "PROGRESS neighbours hot='${hot:-none}'"
    if [ -n "$hot" ] && [ "$ALLOW_NEIGHBOURS" != 1 ]; then
        fail "unpinned foreign containers are burning CPU:$hot — pin or stop them," \
            "or set ALLOW_NEIGHBOURS=1 to measure anyway (recorded in the report)"
    fi
}

up_egernia() {
    log "PROGRESS phase=$PHASE server=egernia step=up"
    compose_egernia up -d --no-build --force-recreate db tap-api tap-executor
    wait_tap $EGERNIA_URL
    expect "egernia rows" "$(pg_egernia 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
    # PR #160: ivoa.obscore is a table kept current by triggers, not a view
    expect "egernia ivoa.obscore relkind" \
        "$(pg_egernia "select relkind from pg_class where oid = 'ivoa.obscore'::regclass")" r
    expect "egernia foreign keys" "$(pg_egernia "select count(*) from pg_constraint \
        where contype = 'f' and connamespace = 'srcnet'::regnamespace")" $EXPECTED_FKS
    # one database: a replica URL would make this a different experiment
    [ -z "$(docker inspect egernia-tap-api-1 --format '{{join .Config.Env "\n"}}' \
        | grep '^TAP_QUERY_DATABASE_URL=' || true)" ] \
        || fail "egernia has TAP_QUERY_DATABASE_URL set; this protocol measures one database"
    for setting in shared_buffers effective_cache_size max_parallel_workers \
        max_worker_processes; do
        expect "egernia $setting" "$(pg_egernia "show $setting")" \
            "$(promised "$EGERNIA_SETTINGS" $setting)"
    done
    expect "egernia pins promise TAP_API_WORKERS" "$(promised_workers "$EGERNIA_PINS")" "$WORKERS"
    expect "egernia container TAP_API_WORKERS" \
        "$(docker inspect egernia-tap-api-1 --format '{{join .Config.Env "\n"}}' \
            | sed -n 's/^TAP_API_WORKERS=//p')" "$WORKERS"
    # one process for a single worker; a supervisor plus one per worker above that
    local processes minimum
    processes=$(docker top egernia-tap-api-1 -o pid,args | grep -c '/srv/.venv/bin/python')
    minimum=$([ "$WORKERS" = 1 ] && echo 1 || echo $((WORKERS + 1)))
    [ "$processes" -ge "$minimum" ] || fail "egernia api processes: $processes < $minimum"
    check_cpuset $EGERNIA_CPUSET $EGERNIA_CONTAINERS
}

up_dachs() {
    log "PROGRESS phase=$PHASE server=dachs step=up"
    compose_dachs up -d --no-build --force-recreate
    wait_tap $DACHS_URL
    expect "dachs rows" "$(pg_dachs 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
    for setting in shared_buffers effective_cache_size max_parallel_workers \
        max_worker_processes; do
        expect "dachs $setting" "$(pg_dachs "show $setting")" \
            "$(awk -v s=$setting '$1 == s {print $3}' "$HERE/pins/dachs-postgres.conf")"
    done
    check_cpuset $DACHS_CPUSET $DACHS_CONTAINERS
}

up_argus() {
    log "PROGRESS phase=$PHASE server=argus step=up"
    compose_argus up -d --no-build --force-recreate
    wait_tap $ARGUS_URL
    expect "argus rows" "$(pg_argus "select count(*) from caom2.\"ObsCore\"")" $EXPECTED_ROWS
    expect "argus caom2.ObsCore relkind" "$(pg_argus "select c.relkind from pg_class c \
        join pg_namespace n on n.oid = c.relnamespace \
        where n.nspname = 'caom2' and c.relname = 'ObsCore'")" r
    for setting in shared_buffers effective_cache_size max_parallel_workers \
        max_worker_processes; do
        expect "argus $setting" "$(pg_argus "show $setting")" \
            "$(promised "$SUITE/docker-compose.argus.yml" $setting)"
    done
    # argus persists one UWS job per sync request and slows down with its own
    # history (argus-equal-cpu/PROTOCOL.md, amendment 1): each phase starts fresh
    pg_argus "truncate uws.jobdetail, uws.job" > /dev/null
    expect "argus job store" "$(pg_argus 'select count(*) from uws.job')" 0
    check_cpuset $ARGUS_CPUSET $ARGUS_CONTAINERS
}

# The pins as applied, per stack, into the run directory.
record() {
    local server=$1 containers=$2 dir="$SUITE/results/$RUN_NAME/pins"
    mkdir -p "$dir"
    # shellcheck disable=SC2086
    docker inspect $containers --format '{{json .HostConfig}}' | python3 -c '
import json, sys
print(json.dumps([{k: h[k] for k in ("CpusetCpus", "NanoCpus", "Memory")}
                  for h in map(json.loads, sys.stdin)], indent=2))' > "$dir/$PHASE-$server.json"
    {
        echo "# $(date -u +%FT%TZ) phase $PHASE, $server"
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
    } > "$dir/$PHASE-$server.txt"
}

log "PROGRESS start phase=$PHASE scenario=$SCENARIO targets='$TARGETS' generator_cpus=$GEN_CPUS"
expect "corpus sha256" "$(sha256sum "$SUITE/corpus/obscore.csv" | cut -d' ' -f1)" \
    "$EXPECTED_CORPUS_SHA"
check_neighbours
up_egernia
up_dachs
up_argus

log "PROGRESS phase=$PHASE step=gates"
if [ -z "$RUN_NAME" ]; then
    tap compare --targets $TARGETS --scenario "$SCENARIO" --gates-only
    RUN_NAME=$(basename "$(ls -td "$SUITE"/results/*-tap-compare | head -1)")
    log "PROGRESS run=$RUN_NAME"
else
    tap compare --targets $TARGETS --scenario "$SCENARIO" --gates-only --resume "$RUN_NAME"
fi
record egernia "$EGERNIA_CONTAINERS"
record dachs "$DACHS_CONTAINERS"
record argus "$ARGUS_CONTAINERS"

# resource telemetry from the first rung (scaling/PROTOCOL.md, amendment 1)
SAMPLES="$SUITE/results/$RUN_NAME/resources.jsonl"
if ! pgrep -f "sample_resources.sh $SAMPLES" > /dev/null; then
    nohup setsid taskset -c "$GEN_CPUS" "$SUITE/scaling/sample_resources.sh" "$SAMPLES" \
        > /dev/null 2>&1 &
    log "PROGRESS sampler -> $SAMPLES"
fi

# an untimed pass per server, so no first repetition pays for a cold cache
for target in $TARGETS; do
    log "PROGRESS phase=$PHASE step=warm target=$target"
    tap run --target "$target" --scenario warm
done

log "PROGRESS phase=$PHASE step=measure run=$RUN_NAME"
tap compare --targets $TARGETS --scenario "$SCENARIO" --resume "$RUN_NAME"

if [ "$RESTORE" != 1 ]; then
    log "PROGRESS phase=$PHASE step=stop"
    compose_egernia stop db tap-api tap-executor
    compose_dachs stop
    compose_argus stop
fi
log "PROGRESS complete phase=$PHASE run=$RUN_NAME"
log "publish with: uv run --group tap-compare python benchmarks/tap-compare publish --run $RUN_NAME"

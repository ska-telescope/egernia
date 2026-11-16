#!/usr/bin/env bash
# The backend A/B (PROTOCOL.md, "Experiment 1"): the same egernia build twice,
# on skycell (cpuset 0-7, project `egernia`) and on pg_sphere (cpuset 8-15,
# project `egernia-pgs`), both in phase A's shape, measured interleaved over
# the geometry classes, two control classes and the mix, into one run
# directory. final/run.sh's checks, interlock, records, sampler and warm pass,
# for two egernia stacks instead of three servers.
#
#   nohup setsid benchmarks/tap-compare/final-skycell/ab.sh > ab.log 2>&1 &
#   grep PROGRESS ab.log
#
# Environment: SCENARIO (backend-ab | backend-ab-smoke), GEN_CPUS ("24-29"),
# RUN_NAME (an existing run directory to resume), ALLOW_NEIGHBOURS,
# ALLOW_CONCURRENT.
#
# Requires both seeded egernia volumes (PROTOCOL.md, "Bring-up") and the
# exported corpus at ../corpus/obscore.csv.
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SUITE=$(dirname "$HERE")
REPO=$(cd "$SUITE/../.." && pwd)
SCENARIO=${SCENARIO:-backend-ab}
GEN_CPUS=${GEN_CPUS:-24-29}
RUN_NAME=${RUN_NAME:-}
ALLOW_NEIGHBOURS=${ALLOW_NEIGHBOURS:-0}
# the registered seven; the smoke scenario runs the mix only, and --classes
# may not name a class a scenario does not run
CLASSES="Q03 Q05 Q06 Q07 Q12 Q13 mix"
if [ "$SCENARIO" = backend-ab-smoke ]; then CLASSES=mix; fi
TARGETS="egernia-ab-skycell egernia-ab-pgsphere"
SKY_CONTAINERS="egernia-db-1 egernia-tap-api-1 egernia-tap-executor-1"
PGS_CONTAINERS="egernia-pgs-db-1 egernia-pgs-tap-api-1 egernia-pgs-tap-executor-1"
SKY_CPUSET=0-7
PGS_CPUSET=8-15
EXPECTED_ROWS=500096
EXPECTED_FKS=16
EXPECTED_CORPUS_SHA=bc4110500860dfdf09377bf1c1442220c424a8edd58217e21d78734b009f6007
NEIGHBOUR_CPU_PERCENT_MAX=50
SAMPLER_PID=""
stop_sampler() {
    [ -n "$SAMPLER_PID" ] || return 0
    kill "$SAMPLER_PID" 2>/dev/null || true
    SAMPLER_PID=""
}
trap stop_sampler EXIT INT TERM

log() { echo "$(date -u +%FT%TZ) $*"; }
fail() { log "FAIL $*"; exit 1; }
expect() { [ "$2" = "$3" ] || fail "$1: got '$2', expected '$3'"; }
# shellcheck source=backend.sh
. "$HERE/backend.sh"

# the generator never on a measured stack's cores (final/run.sh)
python3 -c '
import sys
def cores(spec):
    out = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return out
generator, servers = cores(sys.argv[1]), cores(sys.argv[2]) | cores(sys.argv[3])
sys.exit(1 if not generator or (generator & servers) else 0)
' "$GEN_CPUS" "$SKY_CPUSET" "$PGS_CPUSET" \
    || fail "GEN_CPUS='$GEN_CPUS' is empty, malformed, or overlaps $SKY_CPUSET/$PGS_CPUSET"

tap() {
    (cd "$REPO" && taskset -c "$GEN_CPUS" uv run --group tap-compare \
        python benchmarks/tap-compare --config-dir "$HERE" "$@")
}
compose_sky() {
    docker compose -p egernia -f "$REPO/docker-compose.yml" \
        -f "$HERE/pins/egernia-w1.yml" -f "$HERE/pins/skycell.yml" "$@"
}
compose_pgs() {
    docker compose -p egernia-pgs -f "$REPO/docker-compose.yml" \
        -f "$HERE/pins/egernia-ab-pgsphere.yml" "$@"
}
promised() { grep -o "$2=[^ \"]*" "$1" | head -1 | cut -d= -f2; }

wait_tap() {
    for _ in $(seq 1 120); do
        curl -fsS -o /dev/null "$1/capabilities" && return 0
        sleep 5
    done
    fail "$1 did not answer within 10 minutes"
}

# verify <db> <api> <executor> <cpuset> <backend>: every promise of phase A's
# shape (final/run.sh's up_egernia), plus the backend
verify() {
    local db=$1 api=$2 executor=$3 cpuset=$4 backend=$5 c setting
    local psql=(docker exec "$db" psql -U tap -d tap -Atc)
    expect "$db rows" "$("${psql[@]}" 'select count(*) from ivoa.obscore')" $EXPECTED_ROWS
    expect "$db ivoa.obscore relkind" \
        "$("${psql[@]}" "select relkind from pg_class where oid = 'ivoa.obscore'::regclass")" r
    expect "$db foreign keys" "$("${psql[@]}" "select count(*) from pg_constraint \
        where contype = 'f' and connamespace = 'srcnet'::regnamespace")" $EXPECTED_FKS
    for c in "$api" "$executor"; do
        [ -z "$(docker inspect "$c" --format '{{join .Config.Env "\n"}}' \
            | grep '^TAP_QUERY_DATABASE_URL=' || true)" ] \
            || fail "$c has TAP_QUERY_DATABASE_URL set; this protocol measures one database"
    done
    for setting in shared_buffers effective_cache_size work_mem \
        max_parallel_workers max_worker_processes; do
        expect "$db $setting" "$("${psql[@]}" "show $setting")" \
            "$(promised "$REPO/docker-compose.yml" $setting)"
    done
    expect "$api TAP_API_WORKERS" "$(docker inspect "$api" \
        --format '{{join .Config.Env "\n"}}' | sed -n 's/^TAP_API_WORKERS=//p')" 1
    for c in "$db" "$api" "$executor"; do
        expect "$c cpuset" "$(docker inspect "$c" --format '{{.HostConfig.CpusetCpus}}')" "$cpuset"
    done
    check_backend "$db" "$api" "$executor" "$backend"
}

check_neighbours() {
    local ours=" $SKY_CONTAINERS $PGS_CONTAINERS " hot="" name cpu
    while read -r name cpu; do
        case $ours in *" $name "*) continue ;; esac
        if awk -v c="${cpu%\%}" -v max="$NEIGHBOUR_CPU_PERCENT_MAX" 'BEGIN {exit !(c > max)}'; then
            hot="$hot $name($cpu)"
        fi
    done < <(docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}')
    log "PROGRESS neighbours hot='${hot:-none}'"
    [ -z "$hot" ] || [ "$ALLOW_NEIGHBOURS" = 1 ] \
        || fail "foreign containers are burning CPU:$hot (ALLOW_NEIGHBOURS=1 to measure anyway)"
}

record() {
    local name=$1 containers=$2 db=${2%% *} dir="$SUITE/results/$RUN_NAME/pins" c
    mkdir -p "$dir"
    {
        echo "# $(date -u +%FT%TZ) backend A/B, $name"
        for c in $containers; do
            echo "## $c"
            docker inspect "$c" --format 'cpuset={{.HostConfig.CpusetCpus}} nanocpus={{.HostConfig.NanoCpus}} memory={{.HostConfig.Memory}}'
            docker inspect "$c" --format '{{join .Config.Cmd " "}}'
            docker inspect "$c" --format '{{join .Config.Env "\n"}}' \
                | grep -E '^(TAP_API_WORKERS|TAP_GEOMETRY_BACKEND)=' || true
            docker top "$c" -o pid,args | sed 's/^/  /'
        done
        echo "## SHOW"
        docker exec "$db" psql -U tap -d tap -Atc "select name || ' = ' || current_setting(name) \
            from pg_settings where name in ('shared_buffers', 'effective_cache_size', 'work_mem', \
            'max_parallel_workers', 'max_worker_processes', 'max_connections')"
        echo "## extensions"
        docker exec "$db" psql -U tap -d tap -Atc \
            "select extname || ' ' || extversion from pg_extension order by 1"
    } > "$dir/ab-$name.txt"
}

# The interlock, final/run.sh's: refuse while another tap-compare measurement
# holds the box, excluding our own ancestors and session by identity.
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
        [ "$(ps -o sid= -p "$p" 2>/dev/null | tr -d ' ')" = "$mysid" ] && continue
        echo "$p $args"
      done)
if [ -n "$others" ] && [ "${ALLOW_CONCURRENT:-0}" != 1 ]; then
    log "$others"
    fail "another tap-compare measurement is running (above); ALLOW_CONCURRENT=1 to override"
fi

log "PROGRESS start backend-ab scenario=$SCENARIO targets='$TARGETS' classes='$CLASSES'"
expect "corpus sha256" "$(sha256sum "$SUITE/corpus/obscore.csv" | cut -d' ' -f1)" \
    "$EXPECTED_CORPUS_SHA"
check_neighbours
# The pg_sphere stack takes cores 8-15, which are argus's in experiment 2:
# argus may be stopped during the A/B, never left running beside it.
for c in tap-compare-argus-1 tap-compare-argus-db-1; do
    [ "$(docker inspect "$c" --format '{{.State.Running}}' 2>/dev/null)" != true ] \
        || fail "$c is running on the A/B's cores 8-15; stop the argus stack first"
done
log "PROGRESS step=up stack=skycell"
compose_sky up -d --no-build --force-recreate db tap-api tap-executor
log "PROGRESS step=up stack=pgsphere"
compose_pgs up -d --no-build --force-recreate db tap-api tap-executor
wait_tap http://localhost:8080/tap
wait_tap http://localhost:18080/tap
# shellcheck disable=SC2086
verify $SKY_CONTAINERS $SKY_CPUSET skycell
# shellcheck disable=SC2086
verify $PGS_CONTAINERS $PGS_CPUSET pgsphere

log "PROGRESS step=gates"
if [ -z "$RUN_NAME" ]; then
    tap compare --targets $TARGETS --scenario "$SCENARIO" --gates-only
    RUN_NAME=$(basename "$(ls -td "$SUITE"/results/*-tap-compare | head -1)")
    log "PROGRESS run=$RUN_NAME"
else
    tap compare --targets $TARGETS --scenario "$SCENARIO" --gates-only --resume "$RUN_NAME"
fi
refuse_cone_disagreement "$SUITE/results/$RUN_NAME/gates.json"
record skycell "$SKY_CONTAINERS"
record pgsphere "$PGS_CONTAINERS"

SAMPLES="$SUITE/results/$RUN_NAME/resources.jsonl"
if ! pgrep -f "sample_resources.sh $SAMPLES" > /dev/null; then
    taskset -c "$GEN_CPUS" "$SUITE/scaling/sample_resources.sh" "$SAMPLES" > /dev/null 2>&1 &
    SAMPLER_PID=$!
    log "PROGRESS sampler pid=$SAMPLER_PID -> $SAMPLES"
fi

for target in $TARGETS; do
    log "PROGRESS step=warm target=$target"
    tap run --target "$target" --scenario warm
done

log "PROGRESS step=measure run=$RUN_NAME"
# shellcheck disable=SC2086
tap compare --targets $TARGETS --scenario "$SCENARIO" --classes $CLASSES --resume "$RUN_NAME"
stop_sampler
log "PROGRESS complete backend-ab run=$RUN_NAME"
log "publish with: uv run --group tap-compare python benchmarks/tap-compare publish --run $RUN_NAME"

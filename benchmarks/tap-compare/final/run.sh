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
SAMPLER_PID=""
stop_sampler() {
    [ -n "$SAMPLER_PID" ] || return 0
    kill "$SAMPLER_PID" 2>/dev/null || true
    echo "$(date -u +%FT%TZ) PROGRESS sampler stopped pid=$SAMPLER_PID"
    SAMPLER_PID=""
}
trap stop_sampler EXIT INT TERM

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
fail_early() { echo "FAIL $*" >&2; exit 1; }
# The generator's cores must be disjoint from all three server cpusets: a
# generator sharing a measured stack's cores reports its own contention as
# the server's. An override is validated here, never trusted.
GEN_CORES=$(python3 -c '
import sys

def cores(spec):
    out = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        out.update(range(int(lo), int(hi or lo) + 1))
    return out

generator, servers = cores(sys.argv[1]), set().union(*map(cores, sys.argv[2:]))
print(" ".join(str(c) for c in sorted(generator)))
sys.exit(1 if not generator or (generator & servers) else 0)
' "$GEN_CPUS" "$EGERNIA_CPUSET" "$ARGUS_CPUSET" "$DACHS_CPUSET") \
    || fail_early "GEN_CPUS='$GEN_CPUS' is empty, malformed, or overlaps a server" \
        "cpuset ($EGERNIA_CPUSET, $ARGUS_CPUSET, $DACHS_CPUSET)"

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

# Every one of the host's 30 cores belongs to a server stack or to the
# generator, so a *pinned* foreign container is no safer than an unpinned one
# — it is pinned onto somebody's cores. Any busy container that is not ours
# is therefore a measurement hazard, whatever its cpuset says. HOT is kept
# for the record (record_host), so a run measured over a hot neighbour is
# never indistinguishable from a clean one.
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
            "benchmark's cores or stop them, or set ALLOW_NEIGHBOURS=1 to measure" \
            "anyway (the override and the neighbours are then recorded in the report)"
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
    # One database: a replica URL would make this a different experiment.
    # PR #161 routes query execution in *both* query-serving containers, so
    # both are checked — an override on the executor alone would send async
    # queries to a standby while the API still looked innocent.
    for container in egernia-tap-api-1 egernia-tap-executor-1; do
        [ -z "$(docker inspect "$container" --format '{{join .Config.Env "\n"}}' \
            | grep '^TAP_QUERY_DATABASE_URL=' || true)" ] \
            || fail "$container has TAP_QUERY_DATABASE_URL set;" \
                "this protocol measures one database"
    done
    # work_mem included: the pins promise it, so the driver checks it
    for setting in shared_buffers effective_cache_size work_mem \
        max_parallel_workers max_worker_processes; do
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
    # argus's own DDL folds the identifier: the relation is caom2.obscore
    expect "argus rows" "$(pg_argus 'select count(*) from caom2.obscore')" $EXPECTED_ROWS
    expect "argus caom2.obscore relkind" "$(pg_argus "select c.relkind::text from pg_class c \
        join pg_namespace n on n.oid = c.relnamespace \
        where n.nspname = 'caom2' and c.relname = 'obscore'")" r
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

# The host as the driver found it: the generator's validated affinity, the
# neighbour verdict, whether it was overridden, and every container's CPU.
# `publish` copies pins/ into the report, so a run measured over a hot
# neighbour, or with a non-default generator affinity, says so in the report.
record_host() {
    local dir="$SUITE/results/$RUN_NAME/pins"
    mkdir -p "$dir"
    {
        echo "# $(date -u +%FT%TZ) phase $PHASE, host"
        echo "generator_cpus=$GEN_CPUS"
        echo "generator_cores=$GEN_CORES"
        echo "generator_processes=$(awk -v s="  $SCENARIO:" '$0 == s {f = 1} \
            f && /generator_processes:/ {print $2; exit}' "$HERE/scenarios.yaml")"
        echo "egernia_cpuset=$EGERNIA_CPUSET argus_cpuset=$ARGUS_CPUSET dachs_cpuset=$DACHS_CPUSET"
        echo "neighbour_cpu_percent_max=$NEIGHBOUR_CPU_PERCENT_MAX"
        echo "allow_neighbours=$ALLOW_NEIGHBOURS"
        echo "neighbours_hot=${HOT:-none}"
        echo "## docker stats (all containers, name / cpu / mem / cpuset)"
        docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}' \
            | while read -r n rest; do
                printf '%s %s cpuset=%s\n' "$n" "$rest" \
                    "$(docker inspect "$n" --format '{{.HostConfig.CpusetCpus}}' 2>/dev/null)"
              done
    } > "$dir/$PHASE-host.txt"
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

# The interlock. This driver's first act is to recreate three stacks, which
# rewrites the pins of whatever is running on them; another measurement in
# flight would be silently contaminated (it happened on 2026-09-10, to the
# read-replica tier's run). So: refuse while any other tap-compare
# measurement holds the box, and let ALLOW_CONCURRENT=1 override for a
# deliberate resume.
# Excluding by string would be wrong in both directions: the shell that
# launched this script has the script's path on its own command line (a false
# refusal), and phase B's own scenario name appears in phase A's command line
# (a false pass). So exclude by identity — our ancestors, and, since the
# driver is launched under setsid, everything in our own session.
mine=" $$ "
walk=$$
while [ -n "$walk" ] && [ "$walk" != 0 ] && [ "$walk" != 1 ]; do
    walk=$(ps -o ppid= -p "$walk" 2>/dev/null | tr -d ' ')
    [ -n "$walk" ] && mine="$mine$walk "
done
mysid=$(ps -o sid= -p $$ | tr -d ' ')
# The pattern is the *invocation* form — the harness entry point followed by
# one of its arguments — not the bare path, which any shell that merely
# mentions this directory would carry on its command line.
# `|| true`: pgrep exits 1 when nothing matches, which is the *good* case —
# without it `set -o pipefail` would kill the driver silently on a clean box.
others=$({ pgrep -af 'benchmarks/tap-compare +(--config-dir|compare|run|publish|gates)' \
    || true; } | while read -r p args; do
        case $mine in *" $p "*) continue ;; esac
        if [ "$(ps -o sid= -p "$p" 2>/dev/null | tr -d ' ')" = "$mysid" ]; then
            continue  # our own child (the generator, the gates) under setsid
        fi
        echo "$p $args"
      done)
if [ -n "$others" ] && [ "${ALLOW_CONCURRENT:-0}" != 1 ]; then
    log "$others"
    fail_early "another tap-compare measurement is running (above): recreating the" \
        "stacks now would rewrite its pins mid-rung. Wait for it, or set" \
        "ALLOW_CONCURRENT=1 if you know it is finished."
fi

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
record_host
record egernia "$EGERNIA_CONTAINERS"
record dachs "$DACHS_CONTAINERS"
record argus "$ARGUS_CONTAINERS"

# Resource telemetry from the first rung (scaling/PROTOCOL.md, amendment 1).
# The sampler loops forever, so this phase owns the one it starts and stops it
# on every exit path: two phases would otherwise leave two samplers appending
# to their old files and burning the generator's cores.
SAMPLES="$SUITE/results/$RUN_NAME/resources.jsonl"
if pgrep -f "sample_resources.sh $SAMPLES" > /dev/null; then
    log "PROGRESS sampler already running for $SAMPLES (not ours; left alone)"
else
    taskset -c "$GEN_CPUS" "$SUITE/scaling/sample_resources.sh" "$SAMPLES" \
        > /dev/null 2>&1 &
    SAMPLER_PID=$!
    log "PROGRESS sampler pid=$SAMPLER_PID -> $SAMPLES"
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
stop_sampler
log "PROGRESS complete phase=$PHASE run=$RUN_NAME"
log "publish with: uv run --group tap-compare python benchmarks/tap-compare publish --run $RUN_NAME"

# egernia vs CADC argus, equal-CPU parity: pre-registered protocol

Frozen before any measurement at tag `tap-compare-argus-equalcpu-prereg-v1`.
It is `argus/PROTOCOL.md` (tag `tap-compare-argus-prereg-v1` and its
amendments) with **one change to one target**: egernia's API runs eight
uvicorn workers instead of one. Corpus, query classes, mix, formats, grid,
windows, repetitions, gates, statistics and tie rule are identical —
`argus-equal-cpu/scenarios.yaml` is `config/scenarios.yaml` byte for byte,
`argus-local` is `argus/targets.yaml`'s entry byte for byte
(`tests/test_argus_equal_cpu.py` asserts both).

## Why a second variant

The parity protocol pins every stack to 8 CPUs / 8 GiB and runs each
server as its own documentation deploys it: DaCHS as one `dachs serve`
process, argus as one Tomcat, egernia as one API worker + one executor +
PostgreSQL. That rule is even-handed between egernia and DaCHS — both are
Python, and a single process of either holds the GIL for its own share of
a request — but not between egernia and argus: Tomcat runs one Java thread
per request, so on CPU-bound classes argus's own process uses all eight
pinned cores while egernia's single uvicorn worker is capped at one
(`docs/deployment.md`, "Serving concurrent queries": half of a request's
CPU holds the GIL; one worker ≈ one core). PostgreSQL uses the rest of the
cpuset on both sides, so the gap is on the classes where the *server*
process, not the database, is the bottleneck — the metadata query Q01, the
indexed filters Q03 and Q04, the large results Q10 and Q11, and the
aggregation Q13, whose VOTable/CSV rendering and result streaming are API
work. The first egernia-vs-argus run (`argus/PROTOCOL.md`'s) states this
in its run notes from the resource sampler's cores-used figures.

This variant asks: **with the same eight cores actually available to both
server processes, how do they compare?** It is not a replacement for the
parity run — a deployment that leaves seven cores idle is a real
deployment, and the parity result stands for it — it is the second row of
the same table.

## What changes, and by which documented rule

`egernia-equalcpu.yml` is `docker-compose.egernia-pins.yml` (cpuset 0–7;
8 GiB as 4 db / 2 api / 2 executor, **memory split unchanged**) plus:

- **`TAP_API_WORKERS=8`** — one worker per pinned core, the documented
  rule ("set `tapApi.workers` to the pod's CPU limit"). Memory floor per
  the same page: ~140 MiB × 8 + 8 × 8 × 2.5 MiB ≈ 1.28 GiB, inside the
  API's 2 GiB.
- **Pool size unchanged (`TAP_DB_POOL_MAX` 8 per worker).** The grid's top
  rung offers 32 clients; uvicorn distributes keep-alive connections across
  workers unevenly, so a worker may hold more than 32/8 = 4 of them. A pool
  of 4 would then queue requests on that worker's pool (5 s timeout, then
  HTTP 503 — the mechanism behind the parity run's Q11 c=32 forfeit), which
  would measure the pool, not the server. At 8 per worker no distribution of
  32 clients waits: 8 × 8 = 64 ≥ 32. The connection ceiling is
  8 × 8 + executor 8 = 72, under PostgreSQL's default `max_connections`
  100 (`docs/deployment.md`, "Mind the connections").
- **PostgreSQL's parallel budget by `docs/postgres-performance.md`'s
  rule, applied to the new pool total:** `max_parallel_workers` ≥
  (64 + 8) × `max_parallel_workers_per_gather` 2 = **144**,
  `max_worker_processes` = 144 + 8 = **152**. This is the rule's letter;
  its spirit — every pooled query gets the workers its plan assumed — is
  met with room to spare, since at most 32 queries are ever in flight and
  would claim at most 64 workers. Memory within the db's 4 GiB: 1 GiB
  `shared_buffers` + up to 72 backends and, in practice, ≤ 64 parallel
  workers (~10 MiB each idle; `work_mem` 64 MB is per sort/hash node and
  this workload's largest hash is 1.4 MB, `docs/postgres-performance.md`)
  ≈ 2.4 GiB at the grid's worst case, and 144 worker *slots* cost only
  shared-memory bookkeeping. `shared_buffers=1GB`,
  `effective_cache_size=3GB`, `work_mem=64MB` stay `docker-compose.yml`'s.
- argus: **unchanged** in every respect — `docker-compose.argus.yml`,
  `targets/argus/`, port 80, pools of 8, the ¼-rule PostgreSQL.

The executor keeps its 2 GiB share and single process (idle in this grid).

## Hypotheses, stated in advance

- **H1 — CPU-bound classes scale with the workers.** egernia's CPU per
  request on the mix was ~22 ms in the parity and scaling runs (API ≈ half,
  PostgreSQL ≈ half). With eight workers the API is no longer the ceiling,
  so on Q01, Q03, Q04, Q10, Q11 and Q13 at c ≥ 8 egernia's throughput
  should rise toward the cpuset's limit of roughly 8 cores / 22 ms ≈
  360 requests/s on the mix, and the per-class figures should land near
  the scaling run's egernia figures at the same worker-to-core ratio
  (`docs/performance/`, `tap-compare-scaling` family), with non-overlapping
  95% intervals against the parity run's c ≥ 8 cells. If CPU per request
  grows instead — the eight processes contending for PostgreSQL's share of
  the same eight cores — that is the finding.
- **H2 — the cone classes do not move.** Q05, Q06, Q07 and Q12 are bounded
  by PostgreSQL on both servers (argus by a sequential scan, egernia by its
  index and rendering); egernia's cells there should tie with the parity
  run's within the tie rule at c = 1 and 4, and gain only where the single
  worker was the cap.
- **H3 — argus reproduces.** argus's cells should tie with its cells in the
  first run (same stack, same pins, untouched); any drift is host noise
  and bounds what the egernia deltas can claim.
- **H4 — no 503s at c=32.** With 64 pooled connections for 32 clients,
  egernia's error fraction is 0 in every cell; a non-zero cell is a finding
  about the API, not the pool.

## Threats to validity

Those of `argus/PROTOCOL.md`, plus:

- **Two egernia runs, one argus stack.** argus is measured twice (here and
  in the first run) and egernia's two shapes once each; host drift between
  the two runs is bounded by H3, not removed.
- **The API's memory share is not re-sized.** Eight workers fit the 2 GiB
  by the documented arithmetic (1.28 GiB) but leave less headroom than one
  did; an OOM-killed worker would show as a container restart in the
  sampler's process counts and in `docker inspect`, and would be reported.
- **The parallel budget is generous by construction.** 144 slots for at
  most 64 concurrently useful workers costs nothing measurable, but a
  reader comparing PostgreSQL settings across the two runs must read the
  rule, not the number.
- **This is egernia's documented scaling knob, applied by us.** argus got
  no equivalent attention beyond its README; its own knobs (Tomcat thread
  pool, JVM heap) stay at vendor defaults in both runs, which is the
  fairness rule — but it means the variant is "egernia as documented for
  8 cores vs argus as documented", not "both tuned".

## Amendment 1 — disjoint cores, a fresh argus job store, telemetry from the first rung

Registered 2026-09-08 before the measurement that stands, after a first
attempt (run `20260907T215005Z-2ee1ab59-tap-compare`, stopped at rung
197/720 and kept unpublished) showed the shared cpuset to be unsound for
this pairing:

- **Disjoint cpusets.** The parity pins put both stacks on one shared
  8-core cpuset on the assumption that the server not being measured is
  idle. argus is not: after the generator closes its connections at the
  end of a rung, Tomcat keeps executing the requests still queued behind
  its eight pool slots, and its PostgreSQL ran at ~4.5 cores for 47 of the
  120 measured seconds of the following egernia rung (06:11:45 rung
  boundary; argus quiet only at 06:13:02; egernia's throughput doubled at
  that instant). The variant therefore runs argus on cores 8–15
  (`argus-disjoint.yml`) and egernia on 0–7: each server still has exactly
  eight cores and 8 GiB. This also removes the smaller, opposite
  interference (autovacuum of argus's job store during egernia rungs).
  The first one-process run (`20260906T145338Z`) was measured on the
  shared cpuset; egernia used ~3.2 of the 8 cores there, so the
  contamination bounded its cells by a few percent at most — its notes
  are amended accordingly.
- **A fresh argus job store.** argus persists a UWS job (and its
  parameters) for every synchronous request — 6.4 M jobs and 77 M detail
  rows, 8.4 GiB, after the first run plus the stopped attempt. Every
  further request pays the inserts and index maintenance on those
  tables, so argus's own throughput degrades with its history (mix c=8:
  23.3 rps at the first run's start, 12.7 rps in the stopped attempt).
  Before the measurement `uws.job` and `uws.jobdetail` are truncated, so
  argus starts in the state the first run started in.
- **Resource telemetry** (`scaling/sample_resources.sh`) starts with the
  run and covers every rung.

Hypotheses, grid, statistics and tie rule are unchanged; the pins of
egernia are unchanged.

## Grid and wall-clock

Unchanged: 720 rungs, interleaved A,B,A,B, ≈ 31 h. Generator: four
processes on cores 24–29.

## Reproduce with

```bash
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
docker compose -f docker-compose.yml \
    -f benchmarks/tap-compare/argus-equal-cpu/egernia-equalcpu.yml up -d
docker compose -f benchmarks/tap-compare/docker-compose.argus.yml \
    -f benchmarks/tap-compare/argus-equal-cpu/argus-disjoint.yml up -d --build
docker exec tap-compare-argus-db-1 psql -U tap -d argus \
    -c "TRUNCATE uws.jobdetail, uws.job"   # a fresh job store (Amendment 1)
uv run --group tap-compare python benchmarks/tap-compare \
    --config-dir benchmarks/tap-compare/argus-equal-cpu \
    compare --targets egernia-local-equalcpu argus-local --scenario compare
```

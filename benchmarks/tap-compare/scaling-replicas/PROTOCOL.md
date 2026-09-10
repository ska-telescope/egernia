# The read-replica tier of the resource-scaling comparison: pre-registered protocol

Frozen before any measurement at tag `tap-compare-scaling-replicas-prereg-v1`.
It extends the resource-scaling protocol (`../scaling/PROTOCOL.md`, tag
`tap-compare-scaling-prereg-v1`), whose corpus, query classes, mix, formats,
windows, gates, statistics, tie rule and generator pinning it reuses
unchanged — it even runs from that directory's `scenarios.yaml` and
`targets.yaml` (`--config-dir ../scaling`), so nothing about the workload is
re-specified here. Only what is stated below differs.

## The question

The published scaling run
(`docs/performance/20260905T073915Z-5f145831-tap-compare-scaling/`) gave the
egernia stack 8, 16 and 24 CPUs. At tier 24 — 4 API workers over one 24-core
PostgreSQL — the mixed workload reached 477.7 requests/s at c=64 while using
**11.0 of its 24 cores**. Throughput grew with the tier, but the stack never
ran out of CPU: what it ran out of was one database instance. Every query
class competes for one server's `max_parallel_workers`, one `shared_buffers`,
and one set of backends.

This tier asks what changes when the query path is spread over PostgreSQL
streaming-replication standbys (`TAP_QUERY_DATABASE_URL`, PR "perf: route TAP
queries to PostgreSQL read replicas"). Two things change together, and both
are the treatment:

1. the database becomes one primary plus three standbys, each with its own
   parallel-worker budget and buffer cache;
2. the API goes from 4 workers to 8, because at 4 workers the API is the next
   ceiling and a database that is no longer the bottleneck would not show.

A third rung separates them.

### Hypotheses, stated in advance

- **H1 (the aggregate class scales with standbys × their parallel workers).**
  Q13 (`aggregation and grouping`, a full-table `GROUP BY` that the planner
  parallelises) is the class one instance's parallel budget bounds. Its
  throughput at tier 24r exceeds tier 24b at c=32 **and** c=64, with
  non-overlapping 95% intervals, in both formats.
- **H2 (Q13's gain is the replicas, not the workers).** Q13's tier-24w
  throughput (8 workers, one database) is a *tie* with tier 24b by the
  pre-registered tie rule at c=64.
- **H3 (CPU-bound classes scale with API workers, not with replicas).** Q01
  (`TAP_SCHEMA metadata`, 640 requests/s at tier 24, almost pure API cost:
  parse, translate, render) gains at 24w over 24b, and 24r is a tie with 24w
  at c=64.
- **H4 (the mixed workload gains).** Mixed-workload throughput at c=64 at
  tier 24r exceeds tier 24b with non-overlapping 95% intervals.
- **H5 (the split costs nothing per request).** At c=8 — where no server is
  saturated — every measured class's p95 at tier 24r is a tie with tier 24b.
  A standby holds 3 GiB where the single database held 12, so this is where a
  smaller `shared_buffers` would show. If H5 fails, the report states the
  per-request cost of the split as prominently as the throughput gain.

Any hypothesis that fails is reported with the same prominence as one that
holds. H2 and H3 are the ones that can attribute the effect; if they both
fail, the report claims only that the *shape* is faster, not why.

## Why the published tier 24 is not the baseline

`ivoa.obscore` on this host's seeded volume is no longer the view the
published run measured. PR #160 (branch `perf/obscore-denormalised`) turned it
into a denormalised table maintained by triggers, dropped
`data_products_obscore_did_trgm` with it, and the live stack runs that image;
the volume cannot be put back without disturbing that work. Every class in
this grid reads `ivoa.obscore`, so a comparison against the published
tier-24 numbers would confound read replicas with denormalisation.

**The baseline is re-measured because the relation changed under the volume;
the published tier 24 measured the view.** Tier 24b therefore runs here on the
same volume, under the published tier-24 pins
(`../scaling/pins/egernia-24.yml`, unmodified). All three rungs see the same
`ivoa.obscore` — a table, `relkind = 'r'`, checked at every `up` and recorded
per tier in the run's pins records — and the only comparison this protocol
makes is between its own three rungs. The published tier-24 numbers stay in
their own report as the view-era result, and appear here for context only,
labelled as such.

## What is measured, and what it predates

The measured stack is built from a **local merge of PR #161 (`perf: route TAP
queries to PostgreSQL read replicas`, the `TAP_QUERY_DATABASE_URL` routing)
and PR #160 (`perf: serve ivoa.obscore from a materialised table kept current
by triggers`)**, because the volume already carries #160's relation and the
tier needs #161's routing.

#160 landed on `main` two minutes before the run started (main `b9801a6`,
merged 2026-09-10T07:45Z; the run's first rung at 07:48Z), and `main` was
merged into #161's branch, so what is measured is **#161's own head plus
`main`** — the local merge commit's tree is byte-identical to PR #161's head
(`acca37b`) across `libs/`, `services/`, `db/`, `charts/` and `docs/`; only
this bench suite and the harness's `--classes` differ, and those drive the
grid rather than serve a query. #161 itself is not merged, so the measurement
still predates that one. The merge commit's sha is recorded in the run's
`environment.json` (the harness records the checkout's git state), the report
names both PRs, and the merge branch is local to the measurement rather than
proposed for review on its own.

## The three rungs

| tier | shape | pins | API workers | database |
| --- | --- | --- | ---: | --- |
| 24b | the published tier-24 shape, re-measured | `../scaling/pins/egernia-24.yml` | 4 | one, 12 GiB, cpuset 0–23 |
| 24w | worker control | `pins/egernia-24w.yml` | 8 | one, 12 GiB, cpuset 0–23 |
| 24r | read replicas | `pins/egernia-24r.yml` | 8 | primary 3 GiB + 3 standbys 3 GiB each, all cpuset 0–23 |

Every rung holds the tier-24 budget exactly: 24 CPUs (cpuset 0–23, shared by
all containers as the tier-24 pins share theirs), 24 GiB, and the load
generator on cores 24–29. `tap-api` keeps 6 GiB and `tap-executor` 6 GiB in
all three; what differs is how the database's 12 GiB is divided.

**Why 3 GiB per standby and 3 GiB for the primary.** The database side keeps
its 12 GiB, split four ways. Nothing else is defensible under a fixed budget:
giving the standbys more would take memory from the API and executor, which
are held identical so the comparison is about the database. Each server is
then sized to *its* container by the rule in
`docs/postgres-performance.md` ("Sizing the server to its container"):
`shared_buffers` 768MB, `effective_cache_size` 2304MB, `work_mem` 64MB.
The corpus is 2.1 GiB on disk (`ivoa.obscore` 730 MiB of it), so a standby's
768MB `shared_buffers` holds a large part of the hot set and the host's 120
GiB page cache holds the rest — the reason H5 is a hypothesis and not an
assumption.

**Parallel budgets.** Each standby is sized for the whole query pool, not its
share: libpq balances at random, and two standbys may be down.
`max_parallel_workers` ≥ (8 API workers × 8 + executor 8) × 2 = 144,
`max_worker_processes` = 152. The primary keeps the server's default 8/8: no
user query executes there — `TAP_QUERY_DATABASE_URL` names only the standbys,
and this grid uploads nothing — so it serves `TAP_SCHEMA` reads, `uws.jobs`
and three WAL senders. (A standby refuses to start with a lower
`max_worker_processes` or `max_connections` than the primary; 152 ≥ 8 and 100
= 100 respect that.) Tier 24w re-derives the same 144/152 for its single
server, so 24w and 24r differ in topology alone.

**Connection budget.** Per API worker: up to 8 to the primary and up to 8
spread over the standbys. Fleet peak: 8 workers × 8 + executor 8 = 72 on the
primary, and 72 spread over three standbys (~24 each) — every server under
`max_connections` 100.

## Workload: the same grid, restricted to the classes that can gain

Formats (VOTable, CSV), concurrencies (8, 32, 64), 3 repetitions, 20 s
warm-up, 60 s windows, `MAXREC=100000`, 6 generator processes on cores
24–29, the 60% single-core generator guard, the 1% error ceiling, the tie
rule: all from `../scaling/scenarios.yaml`, scenario `scaling`.

Classes are restricted with the harness's `--classes` option to those whose
cost is where this tier changes something:

| class | what it is | tier-24 throughput | why it is in |
| --- | --- | ---: | --- |
| Q01 | TAP_SCHEMA metadata | 640 | almost pure API cost: the worker-count control (H3) |
| Q03 | indexed categorical filter, TOP 100 | — | small result, index scan: does a 3 GiB standby cost anything (H5) |
| Q04 | temporal range, TOP 200 | — | range scan over `ivoa.obscore`, same question |
| Q10 | thousand-row result | — | serialisation-heavy, done server-side since PR #145 |
| Q11 | ten-thousand-row result (stress) | 38.2 | the largest result in the portable corpus |
| Q13 | aggregation and grouping (stress) | 32.0 | the parallel-worker-bound class: H1 |
| mix | the pre-registered class mix | 477.7 | the headline (H4) |

Left out and why: Q05–Q07 and Q12 are cone searches whose cost is a GiST
index probe of a few hundred rows — bounded by one index lookup, not by a
server's parallel budget or an API worker; Q02 is the DID `LIKE` scan whose
supporting trigram index PR #160 dropped, so its cost on this volume is not
the cost the published run measured and it would measure PR #160 rather than
this change; Q08 and Q09 are `srcnet` joins that PR #160's denormalisation
bypasses for ObsCore queries. Excluding them is a claim restriction, not a
result: the report says nothing about them.

## The grid and its wall-clock

    24b: formats 2 x classes 7 (6 + mix) x concurrency {8,32,64} x 3 reps = 126 rungs
    24r: the same                                                        = 126 rungs
    24w: formats 2 x mix only      x concurrency {8,32,64} x 3 reps       =  18 rungs
    270 rungs x (20 s + 60 s + ~3 s) = 270 x 83 s ~ 6.2 h

Plus three gate passes (~1.5 min each), three warm passes (45 s each), the
stack transitions, and the standbys' first `pg_basebackup` (~2 min each,
concurrent, once) — **expected ≈ 6.5 h**.

Tier 24w runs the mix only: it exists to attribute the effect at the headline
cell, and a full per-class control would add 2.9 h to answer a question the
mix already answers.

## Procedure (`run.sh`)

Everything lands in one run directory
(`results/<stamp>-<sha>-tap-compare-scaling`), resumable with
`RUN_NAME=<dir> TIERS="<remaining>" run.sh`, exactly as the scaling driver
works. Only `egernia-local` is measured; there is no DaCHS or argus rung,
because this is a per-server question about one server's deployment shape.

For each tier, in order **24b, 24r, 24w**:

1. `up` under the tier's pins (`docker compose up -d --no-build
   --force-recreate` on the existing volumes; nothing is re-seeded or
   re-ingested, and the standbys clone the seeded volume with
   `pg_basebackup`). Then verify, and abort on a mismatch:
   - `ivoa.obscore` holds 500,096 rows and is `relkind = 'r'` (the same
     denormalised table for all three tiers);
   - the 16 `srcnet` foreign keys are present;
   - every PostgreSQL setting the pins promise, by `SHOW`, on the primary and
     on each standby;
   - the API's process count for its worker count;
   - for 24r only: three standbys `streaming` in `pg_stat_replication`,
     `pg_is_in_recovery()` true on each, and the API's
     `TAP_QUERY_DATABASE_URL` naming all three.
2. Record the pins as applied — `docker inspect` cpuset/quota/memory,
   container command lines, `docker top`, `SHOW`, `pg_stat_replication` — into
   `pins/t<tier>-egernia-local.{json,txt}` in the run directory. The
   `toolkit-*` containers' presence and CPU use are recorded with them (see
   threats).
3. **Replication lag probe (24r only, untimed, outside the grid.)** Ten small
   writes to a scratch table on the primary, each followed by every standby's
   reported `write_lag`, `flush_lag` and `replay_lag`, into `lag-probe.json`.
   Read from `pg_stat_replication` rather than timed from the shell: a
   `docker exec` plus `psql` start-up is ~200 ms and would swamp a lag of a
   few milliseconds. This is the consistency window `docs/deployment.md`
   describes, measured rather than asserted. It is telemetry, not a
   hypothesis: this grid writes nothing, so no measured rung depends on it.
4. Warm pass (`run --scenario warm`, discarded), then the measured rungs
   (`compare --tier <tier> --only egernia-local --classes …`).
5. Stop the stack; go to the next tier.

`sample_resources.sh` (the scaling protocol's Amendment 1) runs alongside for
the whole run, so every rung has CPU-seconds and memory per container — for
tier 24r that is six containers, and the per-server CPU split is what shows
whether the standbys were the ones working.

At the end the stack returns to the pins it was found under
(`RESTORE=1`, the argus-equal-cpu pins as of this writing) so a neighbouring
experiment is handed back its shape.

## Claims policy

Per rung, the scaling protocol's policy: relative behaviour of this version,
on this hardware, on this corpus, under the recorded pins; ties as ties; a
rung erroring beyond 1% cannot win a cell; a tripped generator guard voids the
cell. Across rungs, the claim is about **one server's deployment shape**: how
egernia's throughput and p95 in a cell change between 24b, 24w and 24r. The
report may not claim anything about other corpus sizes, other hosts, more or
fewer standbys, a replicated deployment under write load (this grid writes
nothing), the classes the restriction excluded, or how any other TAP server
would behave — no other server is measured.

`ivoa.obscore` is PR #160's table in all three rungs, so no claim here is
about the view the published scaling run measured.

## Threats to validity (in addition to the scaling protocol's)

- **Two changes at once.** 24r changes the database topology *and* the API
  worker count. 24w attributes them at the mix and at every class through
  H2/H3's cells only; a per-class attribution outside the mix is not
  available.
- **Sequential blocks.** The three rungs are measured one after another over
  ~6.5 h, so host drift lands per rung rather than decorrelating. The
  repetitions of a cell are spread over the block (the grid loops classes and
  concurrencies outside repetitions), and the order is recorded.
- **The `toolkit-*` neighbours.** `toolkit-4` and `toolkit-6` are unpinned and
  have been observed burning 1–2 cores, floating onto cores 0–23 and 24–29 and
  widening the spread on the fast classes by 10–20%. Measurement does not
  start while they exist; if they appear mid-run, the run notes say from which
  rung. Their state is recorded per tier.
- **A standby is not a second copy of the primary's cache.** Three 3 GiB
  standbys hold three copies of the hot set in three smaller buffer pools,
  backed by one host page cache. H5 is where that shows; the same split on a
  host with less free memory would look worse.
- **No replication slots.** The standbys stream without slots on purpose (a
  forgotten slot would make the primary retain WAL against the shared seeded
  volume). A standby that fell far behind would have to be re-cloned rather
  than catching up; with no writes in the grid there is no WAL to fall behind
  on.
- **One primary, three standbys, one host.** Every server shares the host's
  memory bandwidth and one NVMe device. On separate machines the same shape
  would have more aggregate bandwidth, so the gain measured here is a floor
  for the topology and not a ceiling.

## Amendment 1 — WAL retention on the primary (before any measurement)

Added while preparing the stacks, before a single rung ran, so it is part of
the pre-registration rather than a deviation. Two failures on this box, both
from the primary's default `wal_keep_size = 0` and the deliberate absence of
replication slots:

- three concurrent `pg_basebackup` clones raced the primary's WAL recycling
  and one died with "requested WAL segment … has already been removed";
- standbys restarted after a single-server tier hit the same error, kept no
  WAL receiver, and went on answering `pg_isready` while serving stale data
  from a stalled recovery.

The primary therefore runs with `wal_keep_size = 2GB` in the 24r pins
(verified by `SHOW` at every `up`), each standby retries its clone up to three
times, and `run.sh` drops the standbys' data directories before 24r so
`pg_basebackup` always runs against the primary as it is. None of this touches
a measured quantity: it is WAL kept on disk and a clone that is allowed to
fail once, in a tier whose grid writes nothing. A slot would have retained WAL
indefinitely on the shared seeded volume, which is why the bounded setting is
the one taken.

## Deviations from this document

None are allowed silently. Anything that has to change once measurement has
started is recorded in the run's `environment.json` (`resumed` entries carry
the git state) and in the published report's run notes.

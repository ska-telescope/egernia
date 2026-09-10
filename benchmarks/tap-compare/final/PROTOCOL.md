# The final three-way comparison: pre-registered protocol

Frozen before any measurement at tag `tap-compare-final-prereg-v1`. It is
the parity protocol (`config/`, tag `tap-compare-prereg-v1`) — corpus,
query classes, mix, formats, gates, statistics, tie rule, error ceiling and
generator guard unchanged — run **once against all three servers at the same
time**, in two phases. Its two tables replace every performance table the
earlier runs produced; only what is stated here differs from `config/`.

## The question, and why one experiment replaces four

Four runs are published, and each answers a narrower question than the paper
needs:

| run | what it compared | what it could not say |
| --- | --- | --- |
| `20260901T054529Z` / `20260903T160103Z` | egernia vs DaCHS, 8 CPU / 8 GiB, one process each | nothing about argus; DaCHS's PostgreSQL left at Debian's stock 128 MB |
| `20260905T073915Z` | both at 8 → 16 → 24 CPUs | servers measured one at a time, so no interleaving |
| `20260906T145338Z` | egernia vs argus, one process each | egernia's one uvicorn worker vs Tomcat's eight-core thread pool |
| the equal-CPU variant | egernia at 8 workers vs argus | DaCHS absent; a shared cpuset in the first attempt |

None of them holds all three servers at once, and two of them had to give up
the interleaving the parity protocol relies on. This experiment does both:

- **Table A — one-process parity.** egernia with one uvicorn worker, GAVO
  DaCHS, and CADC argus, each on 8 CPUs and 8 GiB, each deployed as its own
  documentation deploys it. The fair table for the deployment most operators
  will actually run.
- **Table B — equal CPU.** egernia with eight uvicorn workers (one per pinned
  core), against **the same** DaCHS and the same argus, unchanged in every
  respect. The fair table for "the same eight cores are available to every
  server process".

Because DaCHS and argus are byte-identical between the phases, their two
measurements are also a **reproducibility check** on them and a measurement
of host drift over the run; the check is reported in the run notes (H2).

Both phases measure `main` with the denormalised `ivoa.obscore` relation of
PR #160 (a real table kept current by statement-level triggers, not the view
over the product and access tables that every published run measured) and
with **no** `TAP_QUERY_DATABASE_URL` set, so the read-replica routing of
PR #161 is inert and every query goes to the one database. The driver
refuses to start if that variable is present.

## Cores and shapes

The host has 30 vCPUs and 120 GiB. All three stacks stay up for the whole of
a phase on **disjoint cpusets**, so the rungs interleave A,B,C,A,B,C per cell
as the parity protocol requires, and the six cores the generator holds are
touched by no server:

| stack | containers | cpuset | CPU budget | memory | phase A | phase B |
| --- | --- | --- | --- | --- | --- | --- |
| egernia | db, tap-api, tap-executor | 0–7 | 8 shared cores | 8 GiB = 4 db / 2 api / 2 executor | `TAP_API_WORKERS=1` | `TAP_API_WORKERS=8`, PostgreSQL 144/152 |
| argus | Tomcat, PostgreSQL | 8–15 | 8 shared cores | 8 GiB = 3 Tomcat / 5 PostgreSQL | unchanged | unchanged |
| DaCHS | one container (DaCHS + its PostgreSQL) | 16–23 | `cpus: 8` on 8 cores | 8 GiB | unchanged | unchanged |
| generator | — | 24–29 | 6 cores | — | 6 processes | 6 processes |

Disjoint rather than shared, which is what the parity and first argus runs
used: the server that is *not* being measured is not idle. Tomcat keeps
executing the requests still queued behind its pool after the generator has
closed its connections, and argus's PostgreSQL was measured at ~4.5 cores
for up to ~75 s into the following egernia rung on a shared cpuset
(`argus-equal-cpu/PROTOCOL.md`, amendment 1). Three stacks on one cpuset
would make that worse, not better; `argus-equal-cpu`'s amendment is
therefore the rule here from the start, extended to DaCHS.

24 server cores + 6 generator cores = the host exactly. Nothing is left over
for a fourth stack, which is why the two phases are two runs rather than one.

### egernia (`pins/egernia-w1.yml`, `pins/egernia-w8.yml`)

Phase A is `docker-compose.egernia-pins.yml` — the pins of both published
parity runs — with the single uvicorn worker written down explicitly instead
of left to the image default, so the driver can check it. Everything else,
including the `db` command (`shared_buffers=1GB` = ¼ of the db's 4 GiB,
`effective_cache_size=3GB` = ¾, `work_mem=64MB`,
`max_parallel_workers=32`, `max_worker_processes=40`), is
`docker-compose.yml`'s.

Phase B applies `argus-equal-cpu/egernia-equalcpu.yml`'s rule unchanged:

- **`TAP_API_WORKERS=8`** — one worker per pinned core, the documented rule
  (`docs/deployment.md`, "Serving concurrent queries": half of a request's
  CPU holds the GIL, so one worker saturates at ~one core; set the worker
  count to the pod's CPU limit). Memory floor per the same page:
  ~140 MiB × 8 + 8 × 8 × 2.5 MiB ≈ 1.28 GiB, inside the API's 2 GiB, so the
  **memory split does not change** between the phases.
- **Pool size unchanged** at 8 per process (`TAP_DB_POOL_MAX`). The grid's
  top rung offers 32 clients and uvicorn spreads keep-alive connections
  across workers unevenly; 8 × 8 = 64 ≥ 32 means no distribution of the
  clients queues on a worker's pool (a pool of 4 would, and its 5 s timeout
  returning HTTP 503 is what forfeited a cell in the first parity run).
- **PostgreSQL's parallel budget re-derived by `docs/postgres-performance.md`'s
  rule for the new pool total:** (8 workers × 8 + executor 8) = 72
  connections, under the default `max_connections` 100;
  `max_parallel_workers` ≥ 72 × `max_parallel_workers_per_gather` 2 = **144**,
  `max_worker_processes` = 144 + 8 = **152**. `shared_buffers`,
  `effective_cache_size` and `work_mem` stay `docker-compose.yml`'s: the ¼/¾
  rule is applied to the db container's 4 GiB, which does not change.

The executor keeps its 2 GiB share and single process in both phases (idle
in this grid — every rung is synchronous), so the stack's shape stays the
deployable one.

### argus (`docker-compose.argus.yml` + `pins/argus.yml`)

Exactly `argus/PROTOCOL.md`'s deployment, both amendments included: the
vendor image `images.opencadc.org/caom2/argus:1.0.27` (digest pinned) with
its capabilities template pointed at `http://localhost`, host port **80**,
the corpus as a plain `caom2.ObsCore` table with CADC's own indexes
translated onto it, three connection pools of 8, the vendor JVM defaults,
PostgreSQL 17 + pgsphere sized by the ¼ rule (`shared_buffers=1280MB`,
`effective_cache_size=3840MB`, `max_parallel_workers=32`,
`max_worker_processes=40`), and the runner following its sync `303`. The
only addition is the cpuset, 8–15.

**Its UWS job store is truncated before each phase.** argus persists one UWS
job plus its parameters for every synchronous request, and its own
throughput decays with that history — 23.3 rps on the mix at c=8 at the
start of the first argus run, 12.7 rps in a later attempt over 6.4 M
accumulated jobs (`argus-equal-cpu/PROTOCOL.md`, amendment 1). Truncating
`uws.jobdetail, uws.job` before each phase is what makes the two phases
comparable *for argus*, which is the point of H2; the per-request cost of
the inserts themselves is not removed and is still counted against argus, as
it would be in production. The driver truncates and then verifies zero rows.

### DaCHS (`docker-compose.dachs.yml` + `pins/dachs.yml`)

Exactly the compose file both published DaCHS runs used — the Debian
`gavodachs2-server` package in its out-of-the-box layout, DaCHS and its own
PostgreSQL in one container, the corpus published through
`//obscore#publishObscoreLike`, `cpus: 8`, `mem_limit: 8g` — plus two
additions, both of them the scaling protocol's, applied identically in both
phases:

- **a cpuset** (16–23), so DaCHS stays off argus's, egernia's and the
  generator's cores. Same core budget, a determined placement.
- **its PostgreSQL sized to its container by the same ¼ rule** every other
  database here follows: a `conf.d` drop-in (Debian's standard mechanism)
  setting `shared_buffers = 2GB` (¼ of 8 GiB),
  `effective_cache_size = 6GB` (¾), and the parallel budget egernia's and
  argus's databases get at this budget (`max_parallel_workers = 32`,
  `max_worker_processes = 40`). The package leaves 128 MB / 4 GB whatever
  the container's memory; DaCHS's own documentation says nothing about
  PostgreSQL tuning and DaCHS exposes no memory tunable of its own, so left
  stock this measures a stale default rather than the server. DaCHS's
  `[db] poolSize = 2` is *not* touched — raising it would be tuning DaCHS
  beyond its documentation, which the fairness rules forbid — but it is a
  per-pool figure, not a ceiling: DaCHS held eight active connections under
  eight clients, so Debian's stock cap of 8 parallel workers would starve
  its parallel plans exactly as PR #146 found for egernia.

DaCHS's cells here are therefore **not** a replication of the two published
DaCHS runs' database conditions; they are the scaling run's, which the
project adopted after them.

**Corpus state.** The DaCHS container has been stopped since
2026-09-06T14:42Z. Its last start logged `Site starting on 8080` with no
`dachs imp` line, which means the ingest markers in the persistent state
volume (`/var/gavo/state/imported-bench`, `obscore-ready`) were present and
the corpus survived in the `tap-compare_dachs-pg` volume; it then shut down
on SIGTERM with exit 0. The driver verifies
`select count(*) from ivoa.obscore` = 500,096 after the container answers
and **refuses to measure** on any other number. If the volume has in fact
lost the data, a re-ingest is `docker compose … up -d` on an empty state
volume and costs ~55 min under the 8-CPU pin (measured; the README's ~15 min
is for smaller hardware assumptions), plus the `dachs imp //obscore` and
`dachs limits` passes — budget ~80 min and add it to the phase's wall clock.

## The grid and its wall-clock

Two per-rung costs are known from the published runs, both of them
end-to-end (they include the gates, the warm passes and the stack
transitions of their own runs):

| rung shape | published run | rungs | wall clock | per rung |
| --- | --- | ---: | ---: | ---: |
| 30 s warm-up + 120 s window | `20260906T145338Z` (parity grid) | 720 | 30.57 h | **152.8 s** |
| 20 s warm-up + 60 s window | `20260905T073915Z` (scaling grid) | 1,296 | 30.85 h | **85.7 s** |

The parity grid over three servers would be

    3 targets x 12 classes (11 portable + mix) x 2 formats
      x 5 concurrencies {1, 4, 8, 16, 32} x 3 repetitions
      = 1,080 rungs per phase x 152.8 s = 45.8 h per phase = 91.7 h in all

against a budget of about 50 hours. Two cuts, in this order:

1. **The windows: 30 + 120 s → 20 + 60 s.** ×0.56 (152.8 → 85.7 s per rung).
   This is not a new shape: it is `scaling/scenarios.yaml`'s, pre-registered
   at `tap-compare-scaling-prereg-v1` and used for all 1,296 rungs of the
   scaling run, whose egernia tier-8 cells reproduced the parity run's c=8
   cells within their 95% intervals (its H3, asserted by
   `tests/test_scaling.py`). The 60 s window is thus *shown* to give the
   same answer as the 120 s one at the same load.
2. **The concurrency ladder: 5 points → 4, dropping c=16.** ×0.8.

       3 x 12 x 2 x 4 {1, 4, 8, 32} x 3 = 864 rungs per phase
         x 85.7 s = 20.6 h per phase = 41.1 h in all

   plus, per phase, the three-way gates (~5 min: three `taplint` runs and
   165 agreement probes), three warm passes (2.25 min) and three stack
   recreations with their verification (~6 min) ≈ 0.25 h. **Expected ≈ 42 h**
   for both phases, inside the ~50 h budget with ~8 h for overruns (a rung
   whose last streaming response drips past its window; DaCHS's Q11 at c=32
   has a p95 near 25 s).

Rejected alternatives, for the record: five concurrencies at 60 s windows is
51.4 h + overhead ≈ 52 h — over budget with no slack for an overrun; the
120 s windows with three concurrencies is 55 h — worse, and it would drop
two ladder points instead of one.

### What the reduction costs

- **Fewer requests per cell.** The slowest cells of any published run are
  DaCHS's cone classes at c=1, ~1.7–1.8 rps: a 60 s window holds ~105
  requests where 120 s held ~210. Their published 95% half-widths at c=1
  were ±0.008 on 1.73 rps (0.5%), so the interval survives comfortably; but
  a cell's p95 is now the 95th percentile of ~105 samples — resolved to
  about five samples — so a rare tail event (a checkpoint, an autovacuum
  pass) moves the reported p95 more than it did at 120 s. Throughput, which
  the tie rule and every verdict are computed from, is a mean over the whole
  window and is not affected in that way. The scaling run's 60 s windows
  were never used below c=8; c=1 and c=4 at 60 s are new here.
- **The 8 → 32 segment of the ladder is unresolved.** A server whose
  throughput peaks at c=16 shows only its c=8 and c=32 values, so a curve
  plotted from these tables has a 4× gap on its last segment. What that
  cannot cost: **no verdict.** Across the 240 (target, class, format) curves
  of the two published five-point runs, *not one* c=16 cell differs from
  both its c=8 and its c=32 neighbour by more than the 10% tie floor; 29 of
  them are interior peaks at c=16, every one of them within the floor (the
  largest, argus's Q01, 555.9 ±14.2 rps at 16 against 544.1 ±14.7 at 32, is
  a 2% difference and a tie by the rule). A four-point ladder therefore
  reports the same winners; it draws a coarser curve.
- **Not reduced:** three repetitions, the tie rule, the 1% error ceiling,
  the 60% generator guard, both cross-server formats, all 11 portable
  classes plus the mix, `MAXREC=100000` on every request, the corpus, the
  interleaving, and the gates.

### The generator

Six processes (`generator_processes: 6`), `taskset`-pinned to cores 24–29,
which no server stack uses. Six rather than the parity protocol's four
because the guard has to hold at phase B's throughput, and the guard is the
busiest single generator process against one core:

| run | generator processes | fastest cell | guard peak | implied ceiling at 0.6 |
| --- | ---: | ---: | ---: | ---: |
| `20260906T145338Z` (argus) | 4 | 559 rps | 0.50 | ≈ 670 rps |
| `20260905T073915Z` (scaling) | 6 | 712 rps | 0.35 | ≈ 1,220 rps |

Phase B is expected above 670 rps on the light classes (egernia at four
workers over 24 cores already reached 712 rps on Q01 in the scaling run), so
four processes would report the *generator's* ceiling as the server's and
void exactly the cells the paper turns on. Six leaves a ceiling of about
1,220 rps; a cell above it is voided by the guard, and the report says so
rather than believing it. The runner shards the held concurrency across at
most `min(processes, concurrency)` processes, so at c=1 and c=4 the generator
is byte-for-byte the parity protocol's one and four processes; only c=8 and
c=32 are sharded six ways instead of four — the same seeded query stream,
differently split.

An untimed 45 s mixed-workload pass (`warm`) runs against each server after
the stacks come up, so no first repetition pays for a cold `shared_buffers`;
its run directory is a discard.

## Gates

Unchanged in kind, extended to three servers, and run once per phase with
all three stacks up (`compare --gates-only`, then the same run directory is
resumed for the measurement):

- **VOSI capture** per server into `capabilities/`.
- **`stilts taplint`** per server; an ERROR in CAP, TMV, TMS, TMC, QGE or UWS
  refuses the phase. Every server's total error count is reported whatever
  the stages (argus reported 2 in its published run, DaCHS and egernia 0).
- **Cross-server agreement over all three servers at once.** The existing
  gate is already N-way rather than pairwise: it runs five probe queries per
  class against *every* target — each made order-deterministic with an
  `ORDER BY obs_publisher_did` so a `TOP N` cannot pick different, equally
  correct rows on different servers — takes the row count and an
  order-independent sha256 of the `obs_publisher_did` column from each, and a
  class agrees only when the set of (rows, checksum) pairs across all targets
  has exactly one member and no target errored. Three targets therefore
  require unanimity, not agreement with a reference; there is no reference
  server and no privileged pair. Q01 lists each server's own TAP_SCHEMA,
  whose content legitimately differs, so it is checked for a successful
  non-empty answer only. A disagreeing class is **excluded from the phase**
  and named in the report (`tests/test_final.py` covers the three-target
  case, including that one dissenter out of three fails the class).
- **The corpus.** `sha256(corpus/obscore.csv)` must be
  `bc4110500860dfdf09377bf1c1442220c424a8edd58217e21d78734b009f6007` and the
  row count 500,096 in all three servers — `ivoa.obscore` on egernia (a
  table, `relkind = 'r'`, PR #160) and on DaCHS (its obscore view), and
  `caom2."ObsCore"` on argus (a table). The driver checks all of it, plus
  every cpuset, every promised PostgreSQL setting via `SHOW`, the API's
  worker count in both the container's environment and its process count,
  egernia's 16 `srcnet` foreign keys, argus's emptied job store, and the
  absence of `TAP_QUERY_DATABASE_URL`; a mismatch aborts before anything is
  timed. It also samples every container it does not own and refuses to
  start when an unpinned foreign container is burning more than half a core
  (`ALLOW_NEIGHBOURS=1` overrides, and the reason is then recorded).

## Hypotheses, stated in advance

**H1 — egernia's per-request CPU is flat, so workers buy throughput (the one
the paper turns on).** egernia's CPU per request on the mix was 22–24 ms at
every tier of the scaling run while its throughput went 130 → 259 → 478 rps
at c=64, i.e. capacity is workers × cores and not a per-request tax that
grows with them. Prediction: in Table B, for the classes whose ceiling is
API work — Q01 (metadata), Q03 and Q04 (indexed filters), Q10 and Q11 (large
results), Q13 (aggregation) — at c ≥ 8, egernia's throughput exceeds its
Table A value with non-overlapping 95% intervals, while its CPU-seconds per
request from the resource sampler stays within ±25% of the Table A value.
The gain is bounded by the eight cores the API shares with its own
PostgreSQL, so the expected factor is ~3–6×, not 8×. If CPU per request
grows instead — eight worker processes contending with PostgreSQL for one
cpuset — that is the finding, and it is reported as prominently.

**H2 — the two opponents do not move between the phases.** DaCHS is one
`dachs serve` Python process; argus's Tomcat already ran one thread per
request across all eight of its cores in both phases. Neither stack changes
at all. Prediction: every DaCHS cell and every argus cell in Table B is a
**tie** with its Table A cell by the pre-registered tie rule. This doubles as
the reproducibility check on both servers and as a measurement of host drift
over ~42 h; a cell that is not a tie bounds what the egernia deltas between
the two tables may claim, and is reported in the run notes with the number.

**H3 — after PR #160 the scan-heavy classes are close.** The published
parity tables split cleanly: egernia won the cone and filter classes by an
order of magnitude (Q05 CSV at c=8: 175.0 rps against DaCHS's 8.0 and
argus's 13.7 — argus's schema has no index serving a centre-coordinate
predicate, so it scans), while argus won the classes whose cost is
API-side rendering and streaming (at c=8: Q10 141.7 against 87.5, Q11 26.0
against 15.6, Q13 16.3 against 9.7 — 1.6–1.7×). PR #160 removes the joins
egernia's `ivoa.obscore` view imposed on exactly those scan-heavy classes.
Prediction, in two parts: (a) in Table A, egernia's Q10, Q11, Q12 and Q13
cells are **no worse** than the published parity run's, and the two places an
opponent was level there — DaCHS's single winning cell (CSV Q11 at c=32,
where one egernia repetition shed 4% 503s) and the Q13 c ≥ 8 ties — resolve
as an egernia win or a tie, never as a loss; (b) in Table B, with H1's
workers on top of #160, Q10, Q11 and Q13 against argus are ties or egernia
wins rather than argus wins. Neither phase is a replication of any published
egernia cell (its `ivoa.obscore` was a view then, and the windows were
120 s), which is why the continuity check in this experiment is H2's, on the
two servers that did not change.

**H4 — no shed load at c=32 in either phase.** With 64 pooled connections
for at most 32 clients in phase B and 8 for phase A's single worker,
egernia's error fraction is 0 in every cell of both tables. A non-zero cell
is a finding about the API (or about `work_mem` under eight workers), not
about the pool, and cannot win its cell under the 1% ceiling.

**H5 — DaCHS is flat and argus is not.** From the published runs: DaCHS's
throughput is within the tie rule from c=4 upward in every class (one
process), while argus climbs to a knee near its pool of 8. Prediction: in
both tables, DaCHS's c=8 and c=32 cells tie in every class, and argus's c=32
cell beats its c=1 cell with non-overlapping intervals in at least eight of
the twelve classes.

Any hypothesis that fails is reported with the same prominence as one that
holds, and none of them changes what is measured.

## Procedure (`run.sh`)

Per phase (`PHASE=a`, then `PHASE=b`), one run directory each:

1. Verify the corpus sha and sample the host's foreign containers; refuse on
   either.
2. Bring all three stacks up under the phase's pins
   (`up -d --no-build --force-recreate`, so a changed bind-mounted conf file
   is actually applied; nothing is re-seeded or re-ingested), each one
   verified as above the moment it answers `/capabilities`. A mismatch
   aborts.
3. The three-way gates with all three up, then the pins as applied —
   `docker inspect` cpuset/quota/memory, container command lines,
   `docker top`, `SHOW`, argus's job-store count — into
   `pins/<phase>-<server>.{json,txt}` in the run directory.
4. Start the resource sampler (`scaling/sample_resources.sh`, unchanged: pure
   cgroup-v2 reads every 5 s on the generator's cores) so telemetry covers
   the run from its first rung.
5. A warm pass against each server, then the measurement: one
   `compare --targets <egernia> dachs-final argus-final --scenario final`,
   which interleaves the three targets inside every (format, class,
   concurrency, repetition) cell.

Everything lands in one run directory per phase
(`results/<stamp>-<sha>-tap-compare`), resumable with
`RUN_NAME=<dir> PHASE=<phase> run.sh`. `publish --run <dir>` renders that
phase's report; the two reports are the paper's two tables.

## Claims policy

Exactly the parity policy, per table: the relative behaviour *of these
versions, on this hardware, on this corpus, as deployed by their own
documentation, under the recorded resource pins* — with 95% confidence
intervals, per query class, ties reported as ties (overlapping intervals, or
under 10% apart in throughput). With three targets the tie rule is applied
as unanimity: the fastest clean target wins a cell only if it beats *every*
other clean target by the rule, and an indistinguishable leading group is a
tie. A target erroring beyond 1% cannot win a cell (its error responses
return fast and inflate its throughput; the rate is printed beside the
number); a tripped generator guard, or every target erroring, voids the
cell's verdict. Between the two tables the claim is **per server**: how that
server's cell changed when egernia's worker count did.

The tables may not claim anything about other corpus sizes, other hardware,
other versions, concurrencies between 8 and 32, DaCHS or argus under a
configuration their documentation does not describe, or classes a gate
excluded. Classes where egernia loses are reported with the same prominence
as classes where it wins.

## Threats to validity

Those of `config/`'s protocol (the corpus is egernia's own seeder's, so its
distributions may flatter egernia's index choices; the query classes descend
from egernia's performance history; the team operates egernia expertly and
DaCHS and argus from their documentation and source; one host, one window),
those of `argus/PROTOCOL.md` (the flat `caom2.ObsCore` table is not CADC's
join-and-view layout, and on balance flatters argus; the pool of 8 is our
value where the README gives none; argus persists a UWS job per request; its
PostgreSQL build is ours), and:

- **Three cpusets are not three identical machines.** Cores 0–7, 8–15 and
  16–23 sit differently on the host's L3 and memory-bandwidth topology, and
  each phase assigns the same server to the same cpuset, so any placement
  advantage is constant within a server across both phases (which protects
  H1 and H2) but is *not* removed from a cross-server cell. Swapping the
  cpusets between the phases would have removed it and destroyed H2 instead;
  H2 is worth more. Numerically the effect is bounded by the scaling run's
  observation that Q13 moves 10–20% with a *loaded* neighbour on the same
  cpuset — here no neighbour shares a cpuset.
- **Shared memory bandwidth, and only that, is shared.** Three stacks under
  load at different moments still contend for the host's memory controllers
  and page cache, which the parity protocol's "one target at a time" rule
  cannot prevent when all three are resident. The interleaving spreads that
  contention over every cell instead of concentrating it.
- **Unpinned foreign containers.** The host's `toolkit-*` containers have no
  cpuset and were observed burning 1–2 cores on 2026-09-09, floating onto
  cores 0–7 and 24–29 and widening the per-repetition spread of the fast
  classes by 10–20%. The driver refuses to start while one is above half a
  core, and the sampler records every container's CPU throughout, but they
  are not ours to stop and a mid-run wake-up is possible; it would show as
  widened intervals, not as a shifted mean.
- **The generator's ceiling.** ≈ 1,220 rps under the 60% guard. Phase B's
  light classes may reach it; such a cell is voided by the guard, not
  measured, and the report names it.
- **The shorter window's p95.** ~105 requests in the slowest cells (above).
- **c=16 is not measured** (above): no verdict is affected, curves are
  coarser.
- **argus's job store is truncated between the phases** — a deliberate
  intervention on the opponent's state, in argus's favour, so that H2 tests
  the server rather than its accumulated history.
- **DaCHS's ceiling is a design choice** (one Python process) the protocol
  does not alter, and its `poolSize` stays at the package default; a DaCHS
  operator might tune both differently.
- **Both egernia shapes are ours.** Eight workers is egernia's documented
  scaling knob applied by us; argus's and DaCHS's own knobs (Tomcat's thread
  pool, the JVM heap, `poolSize`) stay at vendor defaults in both phases,
  which is the fairness rule — but it means Table B is "egernia as documented
  for eight cores vs DaCHS and argus as documented", not "all three tuned".

## Deviations from this document

None are allowed silently. Anything that has to change once measurement has
started is recorded in the run's `environment.json` (`resumed` entries carry
the git state) and in the published report's run notes.

## Reproduce with

```bash
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
PHASE=a nohup setsid benchmarks/tap-compare/final/run.sh > final-a.log 2>&1 &
uv run --group tap-compare python benchmarks/tap-compare publish --run <run-a>
PHASE=b nohup setsid benchmarks/tap-compare/final/run.sh > final-b.log 2>&1 &
uv run --group tap-compare python benchmarks/tap-compare publish --run <run-b>
```

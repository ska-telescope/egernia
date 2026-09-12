# The three-server resource-scaling comparison: pre-registered protocol

Frozen before any measurement at tag `tap-compare-scaling-threeway-prereg-v1`.
It is the parity protocol (`config/`, tag `tap-compare-prereg-v1`) — corpus,
query classes, mix, formats, gates, statistics, tie rule, error ceiling and
generator guard unchanged — measured at **three resource tiers** against
**all three servers**. Its output is the data behind the paper's
vertical-scaling **figure**; only what is stated here differs from `config/`.

## The question, and why the published scaling run cannot answer it

`docs/performance/20260905T073915Z-5f145831-tap-compare-scaling` raised
egernia and DaCHS from 8 to 16 to 24 CPUs and GiB and measured what each did
with them. It is a good result and it cannot serve the paper's figure:

- **it has no argus**, and the figure must compare all three servers; and
- **it predates PR #160**, so its egernia points were measured on the
  `ivoa.obscore` *view*, not the denormalised relation `main` now serves.
  The final three-way comparison measured ~10 ms of CPU per request on the
  mix where that run measured ~22–24 ms.

So the experiment is run again, with argus added and on current `main`. The
question is unchanged: **given more cores and memory, what does each server
do with them?** The figure plots, per server and per tier, throughput and
the two quantities that explain it — cores actually used and CPU per
request.

## Tiers, cores and the host's limit

| tier | per server | egernia | argus | DaCHS | generator |
| ---: | --- | --- | --- | --- | --- |
| 8 | 8 CPUs, 8 GiB | 0–7 | 8–15 | 16–23 | 24–29 |
| 16 | 16 CPUs, 16 GiB | 0–15 | 0–15 | 0–15 | 24–29 |
| 24 | 24 CPUs, 24 GiB | 0–23 | 0–23 | 0–23 | 24–29 |

The host has 30 vCPUs and 120 GiB.

**Tier 8 is measured with all three servers up at once**, on disjoint
cpusets, interleaved A,B,C inside every cell — the arrangement the final
three-way comparison used (8 + 8 + 8 server cores + 6 generator cores = 30
exactly).

**Tiers 16 and 24 cannot hold three pinned stacks**, so within those tiers
the servers are measured **one at a time**: the two that are not being
measured are **stopped**, not merely idle. Stopped rather than idle is not
fussiness — argus's Tomcat keeps executing the requests its queue still
holds after the generator has closed its connections, and its PostgreSQL was
measured at ~4.5 cores for up to ~75 s into a neighbouring rung
(`argus-equal-cpu/PROTOCOL.md`, amendment 1). **No target ever shares a
cpuset with another**, at any tier.

The order of the servers alternates between tiers — tier 16: egernia, DaCHS,
argus; tier 24: argus, DaCHS, egernia — so host drift over a tier's hours
does not always land on the same server. The loss of interleaving at tiers
16 and 24 is a threat to validity, listed below and repeated in the
published report.

## Per-tier shapes

Every server is sized at every tier **by its own documented rule**, which is
the same rule the published scaling run used, so the two runs' egernia and
DaCHS points remain comparable.

### egernia (`pins/egernia-{8,16,24}.yml`)

`scaling/pins/egernia-<tier>.yml` **byte for byte** (asserted by
`tests/test_scaling_three_way.py`): the three serving containers share the
tier's cpuset; memory splits ½ database, ¼ API, ¼ executor; and

| tier | db | api | executor | API workers | `shared_buffers` | `effective_cache_size` | `max_parallel_workers` | `max_worker_processes` |
| ---: | --- | --- | --- | ---: | --- | --- | ---: | ---: |
| 8 | 4g | 2g | 2g | 1 | 1GB | 3GB | 32 | 40 |
| 16 | 8g | 4g | 4g | 2 | 2GB | 6GB | 48 | 56 |
| 24 | 12g | 6g | 6g | 4 | 3GB | 9GB | 80 | 88 |

**API workers 1 / 2 / 4**, the published scaling run's rule: one worker per
core the API may use, giving the API one of eight cores, two of sixteen and
four of twenty-four, and leaving the database — where the scans and the
VOTable rendering run — the large majority of the cpuset. Three reasons to
keep it rather than raise it:

1. **It is what the paper's existing vertical-scaling result used.** The
   figure replaces that result; keeping the sizing rule keeps the two
   comparable, and the new run's tier-8 and tier-24 points can be read
   against the old run's directly.
2. **The connection budget stays inside the documented default.**
   (workers + 1 executor) × pool 8 = 16 / 24 / 40 connections, all under
   PostgreSQL's `max_connections` 100, with the pool itself unchanged at its
   documented 8. "One worker per *pinned core*" — the rule the final
   comparison's Table B applies at 8 cores — would need 16 and 24 workers
   here, i.e. 136 and 200 connections, so it cannot be applied at these
   tiers without also changing `max_connections` or the pool. Changing two
   things at once is what a scaling figure must not do.
3. **The equal-CPU question is already answered elsewhere.** The final
   comparison's Table B measures egernia with one worker per pinned core
   against the same DaCHS and argus. This protocol asks a different
   question — what a server does with *more* hardware — and answers it for
   all three servers under one sizing discipline.

Consequently **tier 8 here is the final comparison's Table A shape exactly**,
which makes the cross-run check in S4 possible at no cost.

### DaCHS (`pins/dachs-{8,16,24}.yml`, `pins/dachs-postgres-{8,16,24}.conf`)

`docker-compose.dachs.yml` with `cpus` and `mem_limit` raised to the tier, a
cpuset, and its Debian PostgreSQL sized to the container by the ¼ and ¾ rule
through a `conf.d` drop-in — `shared_buffers` 2GB / 4GB / 6GB,
`effective_cache_size` 6GB / 12GB / 18GB, and the parallel budget egernia's
database gets at the same tier (32/40, 48/56, 80/88). The drop-ins are
`scaling/pins/dachs-postgres-<tier>.conf` byte for byte; only the cpuset
differs from `scaling/pins/dachs-<tier>.yml`, because this protocol puts
three servers side by side at tier 8. `[db] poolSize` is **not** touched:
raising it would be tuning DaCHS beyond its documentation, which the
fairness rules forbid.

### argus (`pins/argus-{8,16,24}.yml`)

`docker-compose.argus.yml` — the vendor image, port 80, the corpus as a
plain `caom2.obscore` table with CADC's indexes, three pools of 8 — with the
tier's cpuset and memory:

| tier | Tomcat | PostgreSQL | `shared_buffers` | `effective_cache_size` | parallel budget |
| ---: | --- | --- | --- | --- | --- |
| 8 | 3g | 5g | 1280MB | 3840MB | 32 / 40 |
| 16 | 6g | 10g | 2560MB | 7680MB | 48 / 56 |
| 24 | 9g | 15g | 3840MB | 11520MB | 80 / 88 |

The memory split holds the tier-8 proportion (⅜ Tomcat, ⅝ PostgreSQL) so
argus keeps one shape across tiers; PostgreSQL takes ¼ and ¾ of its own
share and egernia's parallel budget for the tier.

**Two argus knobs deliberately stay at their vendor defaults, and both are
predictions rather than oversights.** The JVM keeps `-Xms512m -Xmx2048m` at
every tier, so above tier 8 the Tomcat container's extra memory is simply
unused — that is what deploying the vendor image as documented does, and the
report says so. The three connection pools stay at **8** at every tier, the
value `argus/PROTOCOL.md` registered and the only argus knob this project
ever set; since sync queries run on the request thread but draw from that
pool, argus's database concurrency does not grow with the tier. S3 states
what that should cost.

**argus's UWS job store is truncated immediately before every measured
block**, after the gates and after the warm pass. argus persists one UWS job
per synchronous request and its own throughput decays with that history
(23.3 → 12.7 rps on the mix at c=8 across accumulated runs). Truncating only
when the stack comes up would not be enough: the agreement gate's 165 probes
and the 45 s warm pass are synchronous requests too, and argus persists every
one of them — and there are *more* of them at tier 8, which warms three
servers, than above it, where one is warmed. That would leave a different
history on each tier's blocks, i.e. history on the tier axis, which is the
one thing this experiment must keep off it. The truncation is a no-op when
argus is stopped, which is every non-argus block above tier 8.

## The grid and its wall-clock

A figure needs fewer cells than a table, and different ones: enough classes
to show that the scaling behaviour is not an artefact of one cost structure,
at enough load to saturate the largest tier.

    per server per tier:
      5 entries (mix + Q01 + Q05 + Q11 + Q13)
        x 2 formats x 2 concurrencies {8, 32} x 3 repetitions = 60 rungs
      9 server-tier blocks x 60 = 540 rungs
      540 x 85.7 s = 12.85 h of rungs

plus, per tier, the gates (~4 min for three servers), three warm passes
(2.25 min) and the stack transitions (~6 min) ≈ 0.4 h in all. **Expected
≈ 13.4 h.** The 85.7 s per rung is measured, not nominal: the published
scaling run did 1,296 rungs of this exact shape (20 s warm-up + 60 s window)
in 30.85 h, gates, warm passes and transitions included. Against the ≈12 h
the run was scoped for, that is 12% over — the difference between the
nominal 83 s rung and the measured 85.7 s — and it is spent on keeping Q13.

**The classes, and why these four.** They span the cost structures the
comparison has found to behave differently, so the figure shows scaling
*per kind of work* rather than one blended number:

- **Q01** — metadata listing, almost no database work: the API's own
  ceiling, and the class argus wins most decisively at parity.
- **Q05** — indexed cone search: geometry, where egernia's index and argus's
  sequential scan diverge by an order of magnitude.
- **Q11** — 10,000-row result: rendering and streaming, the class whose cost
  is dominated by getting bytes out.
- **Q13** — aggregate: the one `GROUP BY` in the workload, PostgreSQL-bound,
  and the class where egernia was historically weakest.
- **mix** — the headline series of the figure, at the pre-registered weights.

**The ladder stops at 32 on evidence, not for budget.** In the published
scaling run c=64 was *below* c=32 at every tier for both servers — egernia
tier 24: 497.7 rps at c=32 against 477.7 at c=64; tier 16: 274.5 against
259.0; DaCHS within 2% at every tier — so 32 already saturates a 24-core
stack and 64 only deepens the queue. A third concurrency would have cost
6.4 h and bought a point below the one beside it.

**What the reduction costs.** Seven of the eleven portable classes are not
measured at these tiers, so the figure may not be read as a claim about them;
the final three-way comparison's two tables cover all twelve at the parity
budget. Concurrency between 8 and 32 is not resolved, and neither is any
load above 32.

Generator: six processes on cores 24–29, which no tier's servers use. The
guard (60% of one core for the busiest process) holds to roughly 1,220
requests/s on this host; the fastest cell any server has produced is 545 rps.

An untimed 45 s mixed-workload pass precedes each block, so no first
repetition pays for a cold `shared_buffers` after a container restart.

## Gates

Per tier, with the tier's stacks up, exactly as the final comparison ran
them: VOSI capture, `stilts taplint` per server (an ERROR in CAP, TMV, TMS,
TMC, QGE or UWS refuses the tier), and the **agreement gate across every
server up at that tier** — five order-deterministic probes per class, and a
class agrees only when the set of (row count, order-independent
`obs_publisher_did` checksum) pairs across all targets has exactly one
member and nobody errored. At tiers 16 and 24 the gate runs with all three
stacks up *before* the measurement blocks begin, then the two that are not
being measured are stopped.

The corpus `obscore.csv` must hash to
`bc4110500860dfdf09377bf1c1442220c424a8edd58217e21d78734b009f6007` and every
server must hold 500,096 rows — `ivoa.obscore` on egernia (a table,
`relkind = 'r'`, PR #160) and on DaCHS, `caom2.obscore` on argus. The driver
checks all of it plus every cpuset, every promised PostgreSQL setting via
`SHOW`, egernia's API worker count in both the container environment and its
process count, the absence of `TAP_QUERY_DATABASE_URL` in both query-serving
containers, and argus's emptied job store — and refuses to measure on any
mismatch.

## Hypotheses, stated in advance

- **S1 — DaCHS does not scale.** One `dachs serve` process cannot use more
  cores. For every entry and format, DaCHS's tier-16 and tier-24 throughput
  is a **tie** with its tier-8 throughput by the pre-registered rule. (The
  published run found exactly this: 8.8 → 10.1 → 10.8 rps on the mix, using
  4.8–5.3 cores at every tier.)
- **S2 — egernia scales with the tier.** Its mixed-workload throughput at
  c=32 rises from tier 8 to 16 to 24 with non-overlapping 95% intervals, as
  the published run found (138 → 275 → 498 rps at c=32), and at least as
  high at each tier now that PR #160 has removed the view's joins.
- **S3 — argus scales, then stops at its pool.** argus is the new point and
  the interesting one. Its Tomcat has 1,024 request threads but its query
  pool is 8 at every tier, and sync queries execute on the request thread
  drawing from that pool. So argus should gain from tier 8 to tier 16 where
  the extra cores relieve contention among those 8 connections, and gain
  **little or nothing** from 16 to 24: the prediction is that argus's
  tier-24 throughput ties with its tier-16 throughput on Q05, Q11 and Q13
  (database-bound through the pool), while Q01 — which barely touches the
  database — keeps climbing. If argus scales all the way, the pool is not
  the binding constraint and that is the finding.
- **S4 — tier 8 reproduces the final three-way comparison.** Tier 8's pins,
  corpus, code, windows, repetitions and concurrencies are phase A's of the
  final comparison exactly, measured days apart. Every tier-8 cell of all
  three servers should tie with its counterpart in
  `20260911T065452Z-41bfc513-tap-compare` by the tie rule. This is a free
  cross-run reproducibility check and it bounds what the tier axis can
  claim; a failure means the host, not the tier, moved the numbers.
- **S5 — CPU per request is flat in the tier for egernia.** The published
  run measured 22–24 ms on the mix at every tier; with #160 the level should
  be lower (~10 ms was measured at the parity budget) but still flat, which
  is what makes "throughput ∝ cores" a mechanism rather than a coincidence.
  A rising CPU per request would mean the cores are being spent on
  contention, and the figure would have to say so.

Any hypothesis that fails is reported with the same prominence as one that
holds, and none of them changes what is measured.

## Procedure (`run.sh`)

For each tier in 8, 16, 24:

1. Refuse to start if another tap-compare measurement is alive on the host,
   if the corpus hash is wrong, or if a foreign container is burning CPU.
2. Bring up the tier's stacks, each verified the moment it answers
   `/capabilities`; a mismatch aborts before anything is timed.
3. The gates with all three up, then the pins as applied — `docker inspect`,
   `docker top`, `SHOW`, argus's job-store count — into
   `pins/t<tier>-<server>.{json,txt}`, plus the host's own state.
4. Start the resource sampler so telemetry covers the tier from its first
   rung.
5. Tier 8: warm all three, then one interleaved `compare` over all three.
   Tiers 16 and 24: for each server in the tier's order, stop the others,
   truncate argus's job store, warm it, measure it alone
   (`compare --tier <tier> --only <target>`).

Everything lands in one run directory
(`results/<stamp>-<sha>-tap-compare-scaling`), resumable with
`RUN_NAME=<dir> TIERS="<remaining>" run.sh`. `publish --run <dir>` renders
one section per tier, each with its gates, tables and — the figure's raw
material — its per-server cores-used and CPU-per-request tables.

## Claims policy

Per tier, exactly the parity policy: the relative behaviour *of these
versions, on this hardware, on this corpus, as deployed by their own
documentation, under the recorded pins*, with 95% intervals and the tie rule
(overlapping intervals, or under 10% apart in throughput), applied across
three targets as unanimity — the fastest clean target wins a cell only if it
beats every other clean target by the rule. A target erroring beyond 1%
cannot win a cell; a tripped generator guard, or every target erroring,
voids it. **Across tiers the claim is per server**: how that server's
throughput, cores used and CPU per request change from 8 to 16 to 24 cores,
judged by the same tie rule between tiers.

The figure and the report may not claim anything about other corpus sizes,
other hosts, a 32-core tier this host cannot run, concurrencies other than 8
and 32, the seven classes this grid does not measure, or any server under a
configuration its documentation does not describe.

## Threats to validity

Those of `config/`'s protocol, of `argus/PROTOCOL.md` (the flat
`caom2.obscore` table is not CADC's join-and-view layout and on balance
flatters argus; the pool of 8 is our value; argus persists a UWS job per
request), and:

- **No interleaving above tier 8.** At tiers 16 and 24 each server is
  measured alone in a block of roughly 1.4 h, so host drift over a tier
  lands on whichever server was running. Mitigations: the order alternates
  between tiers and is recorded; the three repetitions of a cell are spread
  across the block because the grid loops classes and concurrencies outside
  repetitions; nothing else runs on the pinned cores; and S4 bounds the
  drift by checking tier 8 against a run made days earlier. Tier 8 itself is
  fully interleaved.
- **Neighbour quiescence.** The servers not being measured are stopped, not
  idle, at tiers 16 and 24, because an idle-looking argus is not idle. At
  tier 8 all three are up but on disjoint cpusets, which is the arrangement
  the final comparison measured and reported.
- **Stopping and restarting a stack** costs it its page cache; the warm pass
  and the per-rung warm-up mitigate it, and every block pays the same cost.
- **Tier 8 is three servers sharing memory bandwidth**; tiers 16 and 24 are
  one server with the host to itself. Part of any tier-8-to-16 gain is
  therefore the neighbours leaving, not the cores arriving. This is the one
  asymmetry the host's size forces, it cannot be removed without giving up
  either the interleaving at tier 8 or the larger tiers, and S4 quantifies
  the tier-8 half of it by comparing against a run with the same neighbours.
- **argus's JVM heap and pool do not grow with the tier** (above); both are
  vendor defaults and S3 is the prediction.
- **Larger cpusets span more of the host's NUMA and L3 topology**, which is
  not controlled.
- **Seven classes and all loads above c=32 are unmeasured** (above).

## Deviations from this document

None are allowed silently. Anything that has to change once measurement has
started is recorded in the run's `environment.json` (`resumed` entries carry
the git state) and in the published report's run notes.

## Reproduce with

```bash
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
nohup setsid benchmarks/tap-compare/scaling-three-way/run.sh > scaling3.log 2>&1 &
uv run --group tap-compare python benchmarks/tap-compare publish --run <run>
```

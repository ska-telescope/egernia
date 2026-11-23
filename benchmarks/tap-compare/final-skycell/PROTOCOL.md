# The skycell rerun: pre-registered protocol

Frozen before any measurement at tag `tap-compare-final-skycell-prereg-v1`,
amended once before measurement (Amendment 1, tag
`tap-compare-final-skycell-prereg-v2`) and once after DaCHS failed during
phase B (Amendment 2, tag `tap-compare-final-skycell-prereg-v3`) and once
when its cause was found (Amendment 3, tag `tap-compare-final-skycell-prereg-v4`).
Three experiments, one directory. Two of them are existing protocols run
again with **one** change to egernia; the third is new and isolates that
change. Everything not stated here is the base protocol's, unchanged:
[`final/PROTOCOL.md`](../final/PROTOCOL.md) (tag
`tap-compare-final-prereg-v1`) and
[`scaling-three-way/PROTOCOL.md`](../scaling-three-way/PROTOCOL.md) (tag
`tap-compare-scaling-threeway-prereg-v1`), and through them the parity
protocol (`config/`, tag `tap-compare-prereg-v1`).

## Why

egernia gained a second geometry backend: with `TAP_GEOMETRY_BACKEND=skycell`
ADQL geometry is translated for [skycell](https://github.com/jesusjuansalgado/skycell)
instead of pg_sphere, footprints are stored as `skyregion` with a GiST index,
and positions are indexed by a B-tree on their HEALPix cell that includes
`(s_ra, s_dec)`, so a cone is tested on the index entry
(`docs/deployment.md`, "Geometry backend: pg_sphere or skycell"). Every
published egernia number was measured on pg_sphere, at `1845521` (the
three-way tables) or earlier.

The published runs cannot simply be topped up with an egernia-only run:

- **No opponent survives.** Every egernia, DaCHS and argus image and volume
  on the host was gone on 2026-11-16, so DaCHS and argus must be rebuilt and
  re-ingested, and a rebuilt container is not the published one. DaCHS's
  Debian base is digest-pinned but `apt-get install gavodachs2-server` is
  not, so its version is recorded, not assumed.
- **Interleaving.** Every cross-server verdict rests on the targets being
  measured round-robin within each cell. New egernia cells against old
  opponent cells give that up.
- **Two changes at once.** `main` is 165 commits past `1845521`. An
  egernia-only delta against the published cells would mix the backend with
  everything else that changed.

## The one change, and how it is applied

`final-skycell/pins/skycell.yml` sets `TAP_GEOMETRY_BACKEND: skycell` on
`tap-api` and `tap-executor`, layered on top of every egernia pins file by
every driver here. The db image is built with skycell **release v0.58,
commit `0d998bd928e026da05631e6f0e9b3b6dbab7570d`**:

    SKYCELL_REF=0d998bd928e026da05631e6f0e9b3b6dbab7570d \
        docker compose -p egernia build db tap-api tap-executor

On this host Docker's build network resets the clone from GitHub; the db
image is then built on the host network under the same tag
(`docker build --network=host --build-arg SKYCELL_REF=… -t egernia-db db/`),
which changes nothing in the image.

Release v0.58 installs SQL extension version **0.50**: the extension version
is not the release tag and several releases may share it. The build is
therefore identified by the commit `db/Dockerfile` records in the image
(`/usr/share/skycell/COMMIT`), and the extension version is checked beside
it.

Every pins file here other than `skycell.yml` and `egernia-ab-pgsphere.yml`
is a **byte copy** of `final/pins/` or `scaling-three-way/pins/`, and the
scenarios are the base protocols' verbatim (the scaling ones renamed to
`scaling3-skycell*` so the publisher points at this document);
`tests/test_final_skycell.py` asserts both. The egernia targets are renamed
`egernia-skycell-*` because the publisher describes a stack by its target
name; DaCHS and argus keep their names.

### What is verified before anything is timed

`backend.sh`'s `check_backend`, called by every driver after its base
protocol's own checks, refuses unless:

- `TAP_GEOMETRY_BACKEND` is the expected backend in **both** the API and the
  executor container;
- on skycell, the image's recorded skycell commit is the pinned one and
  `pg_extension` reports version 0.50;
- `ivoa.obscore.s_region_geom` is a `skyregion` (skycell) or `spoly`
  (pg_sphere);
- `ivoa.obscore` carries that backend's cone index: an index on
  `skycell_ang2cell(…)`, or a GiST on `spoint(…)`.

The pin records (`pins/*.txt`) add the backend variable and every installed
extension with its version.

## Order, cores and wall clock

| # | experiment | driver | scenario | cores | rungs | expected |
| --- | --- | --- | --- | --- | ---: | ---: |
| 1 | backend A/B | `ab.sh` | `backend-ab` | skycell 0–7, pg_sphere 8–15, generator 24–29 | 336 | ≈ 8 h |
| 2a | three-way, phase A | `run.sh`, `PHASE=a` | `final` | final/'s | 864 | ≈ 21 h |
| 2b | three-way, phase B | `run.sh`, `PHASE=b` | `final` | final/'s | 864 | ≈ 21 h |
| 3 | three-way scaling tiers | `scaling.sh` | `scaling3-skycell` | scaling-three-way/'s | 540 | ≈ 14 h |

Run in that order, one at a time; every driver keeps the base protocols'
interlock and refuses while another tap-compare measurement is alive.
Experiment 1's pg_sphere stack takes cores 8–15, which are argus's in
experiments 2 and 3: `ab.sh` refuses while argus is running, and `run.sh`
and `scaling.sh` refuse while the pg_sphere stack is running. Per rung,
85.7 s end to end (`final/PROTOCOL.md`, "The grid and its wall-clock").

## Bring-up (not measured)

1. Build the images as above, and `docker compose build` DaCHS's and argus's
   from their unchanged Dockerfiles (argus from its digest-pinned vendor
   image).
2. Seed egernia: bring the stack up under `egernia-w1.yml` + `skycell.yml`,
   let the API's bootstrap create the skycell schema, then
   `PYTHONPATH=dataset uv run --group dataset python -m egernia_dataset.seed`
   against it. The seeder writes the footprint type the schema declares.
   Seed the A/B's pg_sphere stack (project `egernia-pgs`,
   `egernia-ab-pgsphere.yml`, its own volume) the same way.
3. DaCHS and argus ingest the corpus on first start, under their pins.

### Pre-flight, before experiment 1 (a go/no-go)

- **Same corpus.** `scripts/export_obscore_snapshot.sh` against the skycell
  stack must reproduce `corpus/obscore.csv` byte for byte (sha256
  `bc4110…6007`): the seeder is deterministic and the backend must not
  change a published row.
- **Index use.** `EXPLAIN` of a Q05, Q06, Q07 and Q12 query as the
  translator emits it, on the skycell stack, shows the cell index, not a
  sequential scan. The plans go into the run notes.
- **Agreement.** The drivers' `--gates-only` pass: taplint and the
  unanimous agreement gate. A cone class on which skycell disagrees with
  pg_sphere (experiment 1) or with DaCHS and argus (experiment 2) is a
  correctness finding about skycell's boundary handling. The experiment
  stops, the finding is reported, and nothing is measured until it is
  understood. The base protocols' rule (exclude the class and measure the
  rest) is **not** applied to the four cone classes here, because they are
  the classes this rerun exists to measure.

## Experiment 1: the backend A/B

The same images twice, in phase A's shape (`egernia-w1.yml`: 8 cores, 8 GiB
as 4 db / 2 api / 2 executor, one API worker, `docker-compose.yml`'s
PostgreSQL settings): skycell on cores 0–7 (project `egernia`, port 8080),
pg_sphere on cores 8–15 (project `egernia-pgs`, port 18080, its own seeded
volume). The two stacks differ in the backend variable, the cpuset, the
host ports and the advertised base URL, and in nothing else.

- **Classes:** the four geometry classes Q05, Q06, Q07 and Q12, two
  geometry-free controls, Q03 (an indexed filter) and Q13 (a parallel
  aggregate), and the mix (9 of its 19 weight units are Q05–Q07).
- **Grid:** `final`'s rung shape and ladder: 20 s warm-up, 60 s window,
  concurrency 1, 4, 8, 32, three repetitions, both formats. 2 targets × 7 ×
  2 × 4 × 3 = 336 rungs.
- **Gates:** taplint on both, agreement between the two on all eleven
  portable classes (not only the measured seven: it is the cheapest
  correctness check skycell will get), the corpus checks, and both stacks'
  `check_backend`.
- **Resources:** the sampler covers both stacks; the publisher attributes
  the pg_sphere stack's containers (`egernia-pgs-*`) to its own target.

Cores 0–7 and 8–15 sit differently on the host's cache and memory topology
(`final/PROTOCOL.md`, threats), so the two stacks are not on identical
hardware. The two controls measure that placement effect directly, and
their hypothesis is what licenses reading the geometry classes as a backend
effect.

## Experiment 2: the three-way phases

`final/PROTOCOL.md` in full: three stacks on disjoint cpusets (egernia 0–7,
argus 8–15, DaCHS 16–23, generator 24–29), interleaved, phase A with one
egernia worker and phase B with eight, argus's UWS job store truncated
before each phase, the same 864-rung grid, gates, statistics, tie rule,
error ceiling and generator guard. egernia runs on skycell.

## Experiment 3: the scaling tiers

`scaling-three-way/PROTOCOL.md` in full: tiers of 8, 16 and 24 cores; at
tier 8 the three servers are interleaved, above it each is measured alone in
alternating order; five classes and the mix, both formats, at 8 and 32
clients, 540 rungs. egernia runs on skycell.

## Hypotheses, stated in advance

**Experiment 1.**

- **K1: the controls tie.** Every Q03 and Q13 cell, in both formats and at
  every concurrency, is a tie between the two backends by the tie rule.
  Neither query touches geometry, so a non-tie measures the cpuset
  placement or the host, and bounds what K2 may claim; it is reported with
  the number.
- **K2: skycell is no worse on geometry.** Every Q05, Q06, Q07 and Q12
  cell, and every mix cell, is a tie or a skycell win. No size of gain is
  predicted. A pg_sphere win in any cell is reported with the same
  prominence as the wins.

**Experiment 2.** H1, H2, H4 and H5 of `final/PROTOCOL.md`, verbatim. H3
referred to the effect of PR #160 against the published parity run and does
not apply to a run whose egernia differs from the published one in two
ways. It is replaced by:

- **H3′: the cone classes stay egernia's.** In both tables egernia wins
  every cell of Q05, Q06, Q07 and Q12 and of the mix, as it did on pg_sphere
  in both published tables.

**Experiment 3.** S1, S2, S3 and S5 of `scaling-three-way/PROTOCOL.md`,
verbatim. S4 (tier 8 reproduces configuration A) is now checked against
**this** protocol's phase A, not the published one: tier 8 ties with
experiment 2's phase-A cell in every cell both grids hold, for each of the
three servers.

Any hypothesis that fails is reported with the same prominence as one that
holds, and none of them changes what is measured.

## Claims policy

The base protocols', per experiment. A claim about what skycell does, as
against pg_sphere, comes from experiment 1 only. Experiments 2 and 3 say
how egernia on skycell compares with DaCHS and argus as rebuilt here; they
do not say which part of a difference from the published tables is the
backend and which is the other 165 commits.

## Threats to validity

Those of both base protocols, and:

- **The geometry extension now differs between the servers.** DaCHS and
  argus run pg_sphere. A cone-class verdict in experiment 2 is egernia's
  design *and* its choice of extension; experiment 1 measures the second
  alone.
- **Rebuilt opponents.** DaCHS's and argus's containers are rebuilt from the
  same Dockerfiles, but they are not the published containers. DaCHS's
  installed version is whatever the Debian archive holds at build time and
  is recorded in the run notes.
- **The A/B's cpusets differ.** Mitigated by K1, not removed.
- **One skycell build.** v0.58 at one commit. No other skycell version is
  measured or claimed.

## Deviations from this document

None are allowed silently. Anything that has to change once measurement has
started is recorded in the run's `environment.json` and in the published
report's run notes.

## Reproduce with

```bash
nohup setsid benchmarks/tap-compare/final-skycell/ab.sh > ab.log 2>&1 &
PHASE=a nohup setsid benchmarks/tap-compare/final-skycell/run.sh > final-a.log 2>&1 &
PHASE=b nohup setsid benchmarks/tap-compare/final-skycell/run.sh > final-b.log 2>&1 &
nohup setsid benchmarks/tap-compare/final-skycell/scaling.sh > s3.log 2>&1 &
uv run --group tap-compare python benchmarks/tap-compare publish --run <run>   # each
```

## Amendment 1: enforcing the cone-class stop, and the smoke runs (before measurement)

Registered after review of the pre-registration (PR #220), before any rung of
this protocol was measured. The `v1` tag stays where it is; this amendment is
tagged `tap-compare-final-skycell-prereg-v2`.

- **The cone-class stop is now enforced, not just stated.** "Pre-flight" says
  a disagreement on Q05, Q06, Q07 or Q12 stops the experiment. The drivers
  did not do it: `compare --gates-only` fails only on taplint, and the
  harness then excludes a disagreeing class and measures the rest, the base
  protocols' rule. Every driver now reads the gate record it just wrote
  (`gates.json`, or `t<tier>-gates.json` per scaling tier) and refuses,
  before the warm pass, if any cone class disagrees (`backend.sh`,
  `refuse_cone_disagreement`). That covers classes outside a grid too: the
  agreement gate runs over all eleven portable classes even where the
  scaling grid measures five. Disagreements on other classes keep the base
  protocols' exclusion.
- **The smoke scenarios run the mix only.** `backend-ab-smoke` and
  `scaling3-skycell-smoke` are not per-class, and the harness refuses a
  `--classes` list that names classes a scenario does not run. With
  `SCENARIO` set to either, the drivers now pass `--classes mix`. The
  registered class lists for the measured scenarios are unchanged.
- **The pg_sphere stack's reproduction command** in the published report
  names `db tap-api tap-executor`, as `ab.sh` does. A bare `up -d` would also
  start a second Prometheus on host port 9090, beside the skycell project's.

Nothing about the workload, grids, gates, statistics, hypotheses or pins
changes. `tests/test_final_skycell.py` covers each point; the refusal is
tested by sourcing the function alone against gate records, never by
running a driver.

## Amendment 2: DaCHS stopped answering during phase B (after measurement began)

Registered after experiment 1 and phase A were complete, before anything
here was re-measured. A deviation, recorded in full; the `v2` tag stays where
it is, and this amendment is tagged `tap-compare-final-skycell-prereg-v3`.

**What happened.**

- Experiment 1 (`20261117T003742Z-d360fb1e-tap-compare`) and phase A
  (`20261117T203446Z-d360fb1e-tap-compare`) completed cleanly. Phase A has
  one rung over the 1% error ceiling (egernia, Q11 VOTable, c=32, r2: nine
  503s), handled by the base protocol's rule. Both stand as measured.
- Phase B (`20261118T163043Z-d360fb1e-tap-compare`) completed all 864 rungs,
  but at 2026-11-19T00:37:30Z, during the warm-up of DaCHS's Q11 VOTable
  c=8 r3 rung, DaCHS began answering every sync request with HTTP 500 in
  about 3 ms (998-byte bodies) and kept doing so until the phase ended at
  12:28Z: 172 of DaCHS's 288 rungs carry 100% errors. Seven of that rung's
  eight requests stayed `EXECUTING` in DaCHS's job table (DaCHS records
  sync requests as UWS jobs). egernia's and argus's rungs are clean apart
  from egernia's Q13 c=32 r1 (6% 500s). The harness does not stop on
  errors, so nothing stopped.
- The scaling run (`20261119T122908Z-d360fb1e-tap-compare-scaling`) then
  measured nothing. DaCHS's job table is on a volume, so the seven stale
  `EXECUTING` rows survived the tier-8 `--force-recreate` and filled
  DaCHS's async run slots (`maxTAPRunning` 2). taplint's async check queued
  forever, the gate timed out after 900 s, and the chain stopped.
- **The cause is not known.** DaCHS's and its postgres's logs died with the
  container on that recreate. Ruled out on the idle box: memory (DaCHS's
  container peaked at 1.5 GiB of 8 GiB; the kernel log is not readable
  without privileges on this host, so an OOM kill inside the container is
  unlikely but not excluded),
  dropped database connections (DaCHS recovers from
  `pg_terminate_backend` at once), and a simple repeat (Q11 VOTable at c=8
  for 300 s: 1,395 requests, all 200).

**Changes (experiments 2 and 3 only; `ab.sh` is untouched).**

- **Each DaCHS bring-up starts from an empty job table** (`clear_dachs_jobs`
  at the end of `up_dachs`), as argus's already does.
- **A server that stops answering stops the run.** Every measuring
  `compare` passes `--abort-error-fraction 0.5`. A rung over half errors is
  a server failure, not a measurement: the harness writes the rung's summary
  and one probe request's status and body to `aborted/<rung>.json`, does
  not mark the rung done, and exits. This is a stop condition, not a
  statistic: the 1% error ceiling and the verdict rule are unchanged, and a
  rung between 1% and 50% is measured and judged exactly as before. How a
  stopped run continues is decided and recorded as a further amendment.
- **A stopped run keeps its evidence.** On any non-zero exit after the gates
  begin, the drivers save every server's `docker logs`, DaCHS's log files,
  its postgres log and its job table to `results/<run>/logs/`.

**What is re-measured, and what is reported.**

- Phase B is measured again in full, as a new run under this tag: same
  grid, gates, interleaving and pins. Re-measuring only DaCHS's failed rungs
  would break the interleaving the base protocol's comparison rests on, so
  none of the first attempt's rungs are carried over, egernia's and argus's
  included.
- Then experiment 3, in full, as a new run.
- The first phase B attempt and the stopped scaling attempt stay on disk,
  unpublished, and both are named in the published reports' run notes with
  the account above. Experiment 1 and phase A are published as measured.

Nothing about the workload, grids, gates, statistics, hypotheses or pins
changes. `tests/test_final_skycell.py` covers each point: the abort helper is
tested against a stubbed HTTP call, and the drivers by reading them.

## Amendment 3: DaCHS serves as `gavo`, and phase B is resumed (after measurement began)

Registered after amendment 2's guard stopped the second phase B attempt, and
before anything here was measured again. Tagged
`tap-compare-final-skycell-prereg-v4`.

**What happened.** The second phase B attempt
(`20261119T203938Z-19e19fcb-tap-compare`) measured 358 rungs with no errors
on any server. At 2026-11-20T04:59:08Z, in DaCHS's Q11 VOTable c=32 r3
rung, DaCHS failed exactly as before. The guard stopped the run at that
rung (error fraction 0.995) and kept the evidence (`aborted/`, `logs/`). The
probe's body read "Cannot connect to the database server".

**The cause, from those logs and DaCHS 2.11's source.**

1. A sync TAP query runs as a UWS job that DaCHS marks `EXECUTING` with
   `pid=-1` (`gavo/protocols/taprunner.py`, `runSyncTAPJob`, whose
   docstring says a sync job must never carry a real pid).
2. Under load, the job-table update that ends such a job hit PostgreSQL's
   statement timeout. The postgres log shows two such timeouts at
   04:59:08.764, both on `UPDATE tap_schema.tapjobs`. The job therefore
   stays `EXECUTING`.
3. The sync path's `finally` destroys the job. `TAPJob.prepareForDestruction`
   (`gavo/protocols/tap.py`) then calls `os.kill(self.pid, SIGTERM)` for an
   `EXECUTING` job. Unlike `killJob`, it has no `pid<2` guard, so this is
   `kill(-1, SIGTERM)`.
4. In this image DaCHS ran as root, as PID 1. `kill(-1)` from root signals
   every other process in the container. PostgreSQL logged "received smart
   shutdown request" at 04:59:08.807, and every backend "terminating
   connection due to administrator command".
5. DaCHS survives (the kernel never delivers `kill(-1)` to PID 1), so the
   container never restarts. Every later request fails to reach the
   database, and the jobs in flight stay `EXECUTING`. The first failure
   (00:37Z on 2026-11-19) matches this in every detail that survived.

This is a DaCHS defect on a failure path, made fatal by how this
benchmark's container ran DaCHS. It is not a property of the workload.

**The change.** DaCHS serves as the unprivileged `gavo` user, as the
Debian package runs it in production.

- `pins/dachs-as-gavo.yml` is layered onto every DaCHS compose call of
  experiments 2 and 3. It runs `pins/dachs-as-gavo.sh`: the image's own
  `/entrypoint.sh` with only its last line changed, to
  `exec setpriv --reuid=gavo --regid=gavo --init-groups dachs serve debug`.
  The script refuses to start if that line is not found.
- PostgreSQL is started as before. The image, DaCHS's version, its
  configuration and its database are unchanged.
- The drivers check that PID 1 is `dachs serve debug` running as `gavo`
  (`check_dachs_user`) before clearing the job table.
- Verified on the idle box: DaCHS serves sync (a 1.9 MB VOTable) and async
  (COMPLETED in 3 s). After `os.kill(-1, SIGTERM)` is called as `gavo`,
  PostgreSQL's nine processes are still up and DaCHS still answers.
- The original trigger, a job-table update timing out, can still happen.
  It now costs that one request an error rather than the server. Such
  errors are counted and judged by the 1% ceiling like any other.

**Phase B is resumed, not restarted.** Decided by the project lead and recorded here.

- The stopped run continues under its own name with `RUN_NAME` set. The
  harness skips the 358 rungs marked done, and re-measures the aborted rung
  (never marked done) and everything after it, in the registered order.
- The gates recorded at the start of the run are reused. The change
  affects which user DaCHS runs as, not what it returns.
- The pin records of the first segment are kept under `pins/segment-1/`
  before the resumed driver writes its own.
- What this trades away: rungs before and after 04:59Z ran DaCHS under
  different users and on two container lifetimes. Nothing in a measured
  request's path differs between them; only the failure path does. The
  published report states the split, the rung it falls at, and both
  segments' pin records.
- Experiment 3 then runs in full, with DaCHS as `gavo` throughout.
- Phase A (DaCHS as root, no failure) stands as measured. Its report
  carries the same note.

`tests/test_final_skycell.py` covers the overlay on every DaCHS compose
call, the user check's place in `up_dachs`, and that the wrapper changes
exactly one line of the image's entrypoint.

## Amendment 4: two egernia faults fixed, and egernia measured again alone (after measurement ended)

Registered after all three experiments were measured and published, and
before anything here was measured again. Tagged
`tap-compare-final-skycell-prereg-v5`.

**What the published runs found.** Two faults in egernia itself
(`docs/postgres-performance.md`, "Shared memory for parallel queries" and
"The sync spool and the dirty-page limit"):

1. With more than one API worker, Q13 returned HTTP 500 at 32 clients (3
   to 8% of requests in phase B, up to 6% at the larger tiers). PostgreSQL
   allocates what a parallel query shares with its workers in `/dev/shm`,
   and the db container had the runtime's default of 64 MiB.
2. With eight workers, Q11 at one client fell from 13.1 to 4.7 rps (CSV).
   Sync results above 1 MiB were written to a temporary file, and under
   the API container's memory limit the kernel throttled those writes.

Both are fixed in PR #230: the in-memory spool threshold is 16 MiB, and
`/dev/shm` is a quarter of the db container's memory limit. The published
runs stand as measured, on the revisions they name.

**What is measured again.** egernia alone, on the fixed revision, over the
grids of experiments 2 and 3 unchanged: phase A, phase B and the three
scaling tiers. DaCHS and argus are not measured again. Decided by the
project lead and recorded here.

- `ONLY=egernia` on `run.sh` and `scaling.sh` passes the harness's `--only`
  for egernia's target. The grid, rung shape, repetitions, warm-up, order
  of cells, generator and its cores are the registered ones.
- The gates still run against all three servers, so taplint and the
  agreement on every portable class are checked for the fixed revision
  before anything is timed.
- In phases A and B and at tier 8, DaCHS and argus stay up and idle on
  their own cores, as they were during egernia's rungs in the interleaved
  runs. At tiers 16 and 24 egernia runs alone, as registered.
- The drivers check that the db container's `/dev/shm` is a quarter of its
  memory limit (`check_shm`), and the pin records carry `ShmSize`.
  `docker-compose.yml` gives 1 GiB for the 4 GiB container of phases A
  and B. `scaling.sh` layers `pins/shm-<tier>.yml`: 1, 2 and 3 GiB at tiers
  8, 16 and 24. The borrowed pin files are unchanged.
- 288 rungs per phase and 180 for the tiers: about 19 hours.

**How the results are read.** A cell's verdict is computed by the
unchanged tie rule from egernia's three repetitions in the new run and
DaCHS's and argus's three repetitions in the published run of the same
experiment (`20261117T203446Z-d360fb1e-tap-compare`,
`20261119T203938Z-19e19fcb-tap-compare`,
`20261120T184934Z-61542dc1-tap-compare-scaling`). The error ceiling and the
generator guard apply to each rung where it was measured.

**What this trades away.** egernia's rungs and its opponents' are no longer
interleaved inside a cell, and they are days apart. Interleaving is what
kept a drift of the host out of the verdicts. The evidence that the
opponents' columns would not move is that they reproduced before: against
the pg_sphere-era runs DaCHS tied in 96 of 96 cells in both tables and
argus in 95 of 96 in phase A. It is evidence about the past, not a
measurement. Hypothesis E3 below is the check this run can make itself.

**Hypotheses, stated in advance.**

- **E1.** No egernia rung exceeds the 1% error ceiling, in either phase or
  at any tier (H4 and S5, on the fixed revision).
- **E2.** In phase B, Q11 at one client is not slower than in phase A, in
  either format.
- **E3 (control).** For the classes whose results are far below 1 MiB and
  do not use a parallel bitmap scan (Q01 to Q07, Q10 and Q12), egernia's cells
  tie its own cells in the published run of the same experiment. A class
  that does not tie means the host has drifted between the two runs, and
  that class's verdicts against DaCHS and argus are reported with that
  caveat.
- Q11, Q13 and the mix are expected to move; by how much is not predicted.

`tests/test_final_skycell.py` covers the `--only` wiring of both drivers,
the shared-memory check's place in both `up_egernia`, and the tier pins'
`shm_size`.

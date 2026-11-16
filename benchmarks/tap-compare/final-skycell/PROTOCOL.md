# The skycell rerun: pre-registered protocol

Frozen before any measurement at tag `tap-compare-final-skycell-prereg-v1`.
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

# egernia vs CADC argus: pre-registered protocol

Frozen before any measurement at tag `tap-compare-argus-prereg-v1`. It is
the parity protocol (`config/`, tag `tap-compare-prereg-v1`) run against a
third server: corpus, query classes, mix, formats, grid, windows,
repetitions, gates, statistics and tie rule are **identical** —
`argus/scenarios.yaml` is `config/scenarios.yaml` byte for byte
(`tests/test_argus.py` asserts it) — and only the opponent changes. What is
stated here is what had to be decided to put argus in DaCHS's seat.

## The question

The parity run (`docs/performance/20260903T160103Z-8fec0e75-tap-compare/`)
compared egernia with GAVO DaCHS, one Python process over PostgreSQL, at
8 CPUs / 8 GiB each. **argus** is the OpenCADC CAOM2 TAP service
(github.com/opencadc/caom2, `argus/`; the `cadc-tap` server libraries under
github.com/opencadc/tap): Java on Tomcat 9, a threaded server over
PostgreSQL + pgsphere, the production TAP service of the Canadian Astronomy
Data Centre. Same hardware, same corpus, same protocol: how does egernia
compare with a mature threaded JVM TAP server?

Expectations stated in advance, from reading argus's source, not from
measuring it:

- **E1 — cone searches.** argus translates `CONTAINS(POINT('ICRS', s_ra,
  s_dec), CIRCLE(...))` into `spoint(radians(s_ra), radians(s_dec)) <@
  scircle(...)` (`cadc-tap-server-pg` PgsphereRegionConverter). No index
  in CADC's schema serves that predicate — the CAOM2 layout indexes
  `Plane.position_bounds_spoly`, the region column, not the centre
  coordinates the ObsCore view derives — so Q05, Q06, Q07 and Q12 are
  sequential scans of the 500,096 rows on argus. egernia should win these
  at every concurrency.
- **E2 — per-request overhead.** Every sync request on argus persists a
  UWS job in PostgreSQL (`PostgresJobPersistence`) and validates the query
  against a freshly read TAP_SCHEMA; egernia does neither. The identifier
  lookup Q02 and the small categorical filter Q03, where the query itself
  is cheap, should show it.
- **E3 — concurrency.** argus runs sync queries on Tomcat's request threads
  (1024) over a query pool of 8 connections (below); DaCHS was flat at
  ~10 rps from c=4 up. argus's throughput should rise with concurrency to
  a knee near the pool size, i.e. behave more like egernia than DaCHS did.

Any expectation that fails is reported with the same prominence as one that
holds; none of them changes what is measured.

## Targets

| target | shape | pins |
| --- | --- | --- |
| egernia-local | the repository's `docker-compose.yml` at the commit recorded in `environment.json`, under `docker-compose.egernia-pins.yml` | shared `cpuset` 0–7; 8 GiB as 4 db / 2 api / 2 executor; PostgreSQL `shared_buffers=1GB`, `effective_cache_size=3GB`, `max_parallel_workers=32`, `max_worker_processes=40` |
| argus-local | `docker-compose.argus.yml`: vendor image `images.opencadc.org/caom2/argus:1.0.27` (digest pinned) + PostgreSQL 17 with pgsphere 1.5.1 (`targets/argus/db`) | shared `cpuset` 0–7; 8 GiB as 3 Tomcat / 5 PostgreSQL; PostgreSQL `shared_buffers=1280MB`, `effective_cache_size=3840MB`, `max_parallel_workers=32`, `max_worker_processes=40` |

egernia's shape is the parity run's, unchanged. The parity run pinned DaCHS
by CFS quota alone (`cpus: 8`, floating over all 30 cores); argus, like
egernia, is pinned to cores 0–7, which keeps it off the generator's cores
24–29 — the same core budget, the placement the scaling protocol adopted.

## What was configured on argus, and why

argus is deployed the way its README deploys it — the vendor image, run as
`tomcat:tomcat` with a read-only `/config` — and pointed at a database that
satisfies what the README requires (PostgreSQL, `citext`, `pgsphere`, a
schema named `caom2`). Everything in `targets/argus/` is either a value the
README leaves to the deployer or the corpus in argus's shape; nothing in the
image or its code is altered.

**The corpus as a plain `caom2.ObsCore` table — route (a).** argus rewrites
every reference to `ivoa.ObsCore` into `caom2.ObsCore` (`CaomAdqlQuery`),
which at CADC is a view over `caom2.Observation JOIN caom2.Plane`. Here
`caom2.ObsCore` is a table with the view's exact column list — names,
types, order, including the columns the view keeps out of TAP_SCHEMA
(`position_bounds_spoly`, `metaRelease`, ...) — loaded from the exported
corpus (`corpus/obscore.csv`, sha256 `bc411050…`, 500,096 rows) by
`targets/argus/db/init/02-obscore.sql`. The alternative, route (b), would
populate `Observation` and `Plane` so the vendor view yields the rows: it
was not taken because the view derives columns the corpus cannot reproduce
(`access_url` is the plane's publisher ID for DataLink resolution,
`access_format` a constant, `s_ra`/`s_dec` recomputed from a pgsphere
centre), so the rows would not be the corpus's rows, and because the joins
would be an artefact of the mapping rather than of either server. Route (a)
gives argus the logical rows every other target has, in the physical shape
argus's own code expects. Three consequences of argus's code are honoured:
`s_region` is `double precision[]` (`[ra, dec, r]` from the corpus's
`CIRCLE ra dec r`), which argus renders as an STC-S circle; `metaRelease`
is a date in the past, because argus appends `metaRelease < now()` to every
`caom2.ObsCore` query for anonymous callers — the corpus is entirely
public; `position_bounds_center` is the pgsphere point CENTROID() reads.
Two columns the corpus does not carry stay NULL: `position_bounds_spoly`
(pgsphere has no circle-to-polygon cast; `CONTAINS(s_region, ...)` is not
in the workload) and `dataRelease`/`obs_release_date`.

**TAP_SCHEMA.** argus writes it itself at startup
(`InitCaomTapSchemaContent`: the CAOM2 tables and `ivoa.ObsCore` with the
ObsCore 1.1 utypes, UCDs, units and xtypes). So that what it describes
exists, `01-caom2.sh` creates the CAOM2 tables empty from CADC's own DDL,
vendored at a pinned commit with checksums; argus's availability check also
selects from `caom2.Observation`.

**Indexes.** The fairness rule keeps each server's native layout and
indexes. argus has no native flat layout, so the table receives CADC's
indexes on the columns the view draws from, one for one
(`caom2.Plane.sql`, `caom2.Observation.sql`, `caom2.extra_indices.sql`):
unique on the publisher DID; b-trees on `t_min`, `t_max`, `em_min`,
`em_max`, `(obs_collection, instrument_name)`, `(facility_name,
instrument_name)`, `instrument_name`, `facility_name`, `lower(obs_id)`,
`lower(target_name)`, the pattern-ops variants, `pol_states`,
`lastModified`. **Nothing is added** — in particular no index on
`(s_ra, s_dec)` or on `spoint(radians(s_ra), radians(s_dec))`: CADC's
schema has none, and E1 states what that costs. Not carried over: the GiST
on `position_bounds_spoly` and the `dataRelease` index (NULL columns) and
the clustering on `obsID` (no such column).

**Connection pools.** The README requires three pools (`uws`, `tapadm`,
`query`) and leaves `maxActive` blank; CADC's sandbox Helm chart falls back
to 2. Each pool gets **8** — one connection per pinned core, and the size
of the pool egernia's API answers sync queries from (`config.dbPoolMax`).
The pool is the only argus knob this deployment sets to a value of its own;
the choice and its consequence (E3) are pre-registered here. Sync queries
run on the request thread (`AbstractExecutor.executeSync`), so the pool,
not argus's async executor of 6 threads, bounds sync concurrency.

**JVM.** The vendor default of the cadc-tomcat base image (`-Xms512m
-Xmx2048m`, G1) is kept; the Tomcat container's 3 GiB limit holds that
heap plus metaspace and thread stacks. The remaining 5 GiB is the
database's, the same database-heavy split as egernia's 4 of 8.

**PostgreSQL sized to its container by the ¼ rule** — as the scaling run
applied it to DaCHS (`scaling/PROTOCOL.md`, "DaCHS"), and as egernia's own
compose file applies it (`docs/postgres-performance.md`): `shared_buffers`
= 1/4 and `effective_cache_size` = 3/4 of the container's 5 GiB (1280MB /
3840MB), and egernia's parallel budget (`max_parallel_workers=32`,
`max_worker_processes=40`) so argus's 24 pooled connections are not starved
of parallel workers the way PR #146 found for egernia. The parity run left
DaCHS's PostgreSQL at Debian's stock 128MB; argus gets the fairer sizing
from the start, so this run is not a strict replication of the DaCHS
protocol's database conditions — it is the scaling protocol's, which the
project adopted after the parity run.

**Standalone.** `cadc-registry.properties` is empty: no registry, no CDP,
GMS or UMS authority. Every lookup argus would make against CADC's
infrastructure — dependent-service availability probes, group membership
for proprietary metadata, DataLink resolution of publisher IDs — reports
"not found" and is skipped (verified in `CaomTapService`, `CredUtil`,
`DataLinkURLFormat`). No `IdentityManager` is configured (cadc-util's
`NoOpIdentityManager`: every caller anonymous). Tomcat's proxy properties
name the mapped host port so capabilities and UWS documents carry URLs
clients and taplint can follow. Async results go to the container's `/tmp`
(`TempStorageManager`).

## Gates

Unchanged: VOSI capture, `stilts taplint` (ERRORs in CAP, TMV, TMS, TMC,
QGE, UWS refuse the comparison; argus's total error count is reported
whatever the stages), and the agreement gate over all 11 portable classes
(row count and order-independent checksum of `obs_publisher_did`, five
probes per class). A disagreeing class is diagnosed in the ingest — column
mapping, NULL handling, number formatting — never in the corpus, and the
fix is committed before the timed run.

## Grid and wall-clock

`compare` in `scenarios.yaml`: 2 formats × 12 classes (11 + mix) ×
{1, 4, 8, 16, 32} × 3 repetitions = 360 rungs per server, 720 in all,
interleaved A,B,A,B per cell, 30 s warm-up + 120 s window each. The parity
run took 30.6 h for 721 rungs; **expected ≈ 31 h**. Generator: four
processes, the parity protocol's, on cores 24–29.

## Threats to validity

Those of the parity protocol (the corpus is egernia's seeder's; the
classes descend from egernia's history; the team operates egernia expertly
and argus from its README and source; one host, one window), and:

- **The flat table is not CADC's layout.** argus in production reads a
  view over two joined tables; here it reads one table with the view's
  columns and CADC's indexes translated onto it. The translation removes
  a join argus would otherwise pay for and cannot add indexes CADC does not
  have; on balance it flatters argus slightly on every class, and E1 is a
  property of CADC's index set, not of the flattening.
- **The query pool is our value.** 8 per pool is argued above, but the
  README gives none and CADC's charts default to 2; argus at 2 would fall
  over at c≥4 (pool wait 20 s, then HTTP 500), at 32 it might climb
  further. One value is measured; the pool is recorded in the report.
- **argus persists every sync job.** Its UWS tables grow by one row per
  request (~1.4 M rows over the run) on the same PostgreSQL; a vendor
  behaviour, counted against it as it would be in production.
- **PostgreSQL for argus is ours.** CADC's own image is PostgreSQL 17 +
  pgsphere 1.5.2 on Fedora; this is the official Debian image + Debian's
  pgsphere 1.5.1 — same majors, different builds.
- **Not a replication of the DaCHS run's database conditions** (see
  "PostgreSQL sized to its container"): argus's database is sized by the
  ¼ rule; the parity run's DaCHS was not.
- **Two containers versus one.** DaCHS held one 8-CPU quota; argus's
  Tomcat and PostgreSQL share one 8-core cpuset (work-conserving, like
  egernia's three containers) with fixed memory shares — a JVM starved of
  memory would show as OOM restarts, which the report would record.

## Reproduce with

```bash
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
docker compose -f docker-compose.yml \
    -f benchmarks/tap-compare/docker-compose.egernia-pins.yml up -d
docker compose -f benchmarks/tap-compare/docker-compose.argus.yml up -d --build
uv run --group tap-compare python benchmarks/tap-compare \
    --config-dir benchmarks/tap-compare/argus \
    compare --targets egernia-local argus-local --scenario compare
```

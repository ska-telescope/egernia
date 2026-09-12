# tap-compare: a same-hardware TAP-server benchmark

A harness for comparing IVOA TAP 1.1 servers — egernia against other open
implementations (GAVO DaCHS next, CADC `opencadc/tap` after) — on **identical
hardware over an identical logical corpus**, each server deployed per its own
project's documentation. It doubles as egernia's own end-to-end capacity
measurement, succeeding the removed cluster harness (recoverable at
`git show f6fbeb3^:benchmarks/egernia-performance/`), from which the corpus,
runner and statistics here descend.

## Running (current scope: egernia only)

```bash
# 1. the target: the repo's compose stack, seeded to the D1 corpus
docker compose up -d
TAP_DATABASE_URL=postgresql://tap:tap@localhost:5432/tap \
  PYTHONPATH=dataset uv run --group dataset python -m egernia_dataset.seed

# 2. a shake-out run (not a measurement)
uv run --group tap-compare python benchmarks/tap-compare run \
    --target egernia-local --scenario smoke

# 3. the capacity ladder
uv run --group tap-compare python benchmarks/tap-compare run \
    --target egernia-local --scenario ladder

# 4. the comparison: DaCHS up, corpus exported, gates + interleaved rungs
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
docker compose -f benchmarks/tap-compare/docker-compose.dachs.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets egernia-local dachs-local --scenario compare

# 5. render the report into docs/performance/<run-name>/
uv run --group tap-compare python benchmarks/tap-compare publish --run <run-name>

# unit tests
uv run --group tap-compare pytest benchmarks/tap-compare/tests -q
```

Scenarios: `compare` is the reference protocol (fixed 1–32 ladder, VOTable +
CSV, 120 s windows, 3 interleaved repetitions); `compare-demo` is the same
protocol shortened for developer hardware; `compare-smoke` proves the
pipeline and measures nothing. The gates (taplint conformance and the
cross-server agreement check) run first and a taplint failure refuses the
comparison. Comparative cells carry 95% confidence intervals and the
pre-registered tie rule: overlapping intervals, or under 10% apart in
throughput, is a tie.

Results land in `benchmarks/tap-compare/results/<UTCstamp>-<sha>-<label>/`
(the label is `<scenario>-<target>` for single-target `run`s and
`tap-compare` for multi-target `compare` runs):
per-rung Parquet samples (every request, with TTFB), per-rung JSON summaries
with bootstrap confidence intervals, `corpus.json`, and `environment.json`
provenance. Runs never overwrite and are resumable (`--resume <run-name>`).

## The resource-scaling protocol (`scaling/`)

A second, separately pre-registered protocol (tag
`tap-compare-scaling-prereg-v1`) raises both servers' pins tier by tier
(8 → 16 → 24 CPUs and GiB) and measures what each does with them; its
design, sizing rules, grid arithmetic and threats to validity are in
[`scaling/PROTOCOL.md`](scaling/PROTOCOL.md). It is another config
directory (`--config-dir benchmarks/tap-compare/scaling`), per-tier compose
overrides under `scaling/pins/`, and a driver (`scaling/run.sh`) that
measures the servers one at a time per tier into one run directory
(`compare --tier <tier> --only <target>`); `publish` renders one section
per tier. The parity protocol under `config/` is untouched.

## The third target: CADC argus (`argus/`)

The parity protocol run against the OpenCADC CAOM2 TAP service instead of
DaCHS (tag `tap-compare-argus-prereg-v1`): the vendor image over a
PostgreSQL 17 + pgsphere that holds the corpus as argus's own
`caom2.ObsCore` (`docker-compose.argus.yml`, `targets/argus/`), and a
config directory whose `scenarios.yaml` is `config/`'s verbatim
(`--config-dir benchmarks/tap-compare/argus`, targets `egernia-local
argus-local`). What was decided to put argus in DaCHS's seat, and why, is
in [`argus/PROTOCOL.md`](argus/PROTOCOL.md).

### The equal-CPU variant (`argus-equal-cpu/`)

The same protocol with egernia's API at one uvicorn worker per pinned core
(`TAP_API_WORKERS=8`, PostgreSQL's parallel budget re-derived by the
documented rule; `argus-equal-cpu/egernia-equalcpu.yml`), because a Tomcat
uses all eight cores for CPU-bound work where one uvicorn worker uses one
(tag `tap-compare-argus-equalcpu-prereg-v1`;
[`argus-equal-cpu/PROTOCOL.md`](argus-equal-cpu/PROTOCOL.md)). Targets
`egernia-local-equalcpu argus-local`, `--config-dir
benchmarks/tap-compare/argus-equal-cpu`.

## The final three-way comparison (`final/`)

The experiment whose **two tables replace every earlier performance table**
(tag `tap-compare-final-prereg-v1`): the parity protocol run against all
three servers at once — egernia, GAVO DaCHS and CADC argus, each on 8 CPUs
and 8 GiB, on **disjoint cpusets** (egernia 0–7, argus 8–15, DaCHS 16–23,
generators 24–29) so the rungs interleave A,B,C per cell — in two phases
that differ in one thing only:

- **Table A**, `PHASE=a`: egernia with one uvicorn worker (the deployment
  most operators run).
- **Table B**, `PHASE=b`: egernia with eight, one per pinned core, against
  *the same* DaCHS and argus, unchanged — which makes their two
  measurements a reproducibility check on them.

The grid is the parity grid with the scaling protocol's 20 s + 60 s windows
and `c=16` dropped: 864 rungs per phase, ≈ 42 h for both. Design, sizing
rules, grid arithmetic, hypotheses and threats to validity are in
[`final/PROTOCOL.md`](final/PROTOCOL.md); `final/run.sh` brings the three
stacks up, verifies every promise the pins make (row counts, `relkind`,
`SHOW` of every setting, worker counts, cpusets, argus's truncated job
store, the corpus sha, foreign containers) and refuses to measure if
anything is off.

```bash
PHASE=a nohup setsid benchmarks/tap-compare/final/run.sh > final-a.log 2>&1 &
uv run --group tap-compare python benchmarks/tap-compare publish --run <run>
```

## The three-server resource-scaling comparison (`scaling-three-way/`)

The data behind the paper's vertical-scaling **figure** (tag
`tap-compare-scaling-threeway-prereg-v1`): the parity workload measured at
**8 / 16 / 24 CPUs and GiB** against **all three** servers, each sized at
each tier by its own documented rule. It replaces the two-server
`scaling/` run, which has no argus and predates PR #160.

At tier 8 all three fit the host (8 + 8 + 8 server cores + 6 for the
generator = 30) and interleave A,B,C; at 16 and 24 they cannot, so each is
measured alone with the others **stopped** — never merely idle, because
argus keeps draining its queue. The grid is narrow because a figure needs
fewer cells than a table: the mix plus Q01, Q05, Q11 and Q13, both formats,
c ∈ {8, 32}, 3 repetitions — 540 rungs, ≈ 13.4 h. The ladder stops at 32 on
evidence: in the published scaling run c=64 came in *below* c=32 at every
tier for both servers.

Design, per-tier sizing, grid arithmetic, hypotheses and threats to validity
are in [`scaling-three-way/PROTOCOL.md`](scaling-three-way/PROTOCOL.md);
`scaling-three-way/run.sh` carries the final comparison's driver discipline
(verification before measuring, the concurrent-measurement interlock,
telemetry from the first rung, the pins recorded as applied).

```bash
nohup setsid benchmarks/tap-compare/scaling-three-way/run.sh > s3.log 2>&1 &
```

## Fairness rules (lane A — the only lane)

This harness is **never pointed at a production service someone else
operates**. Every target is deployed locally by the operator, and:

- identical *logical* rows in every server (the exported `ivoa.obscore` view,
  sha256-pinned), loaded through each server's own documented ingest path —
  each server keeps its native physical layout and indexes, because a server
  *is* its recommended layout;
- identical container CPU/memory limits, one target under load at a time
  (every target stack stays up so repetitions can interleave A,B,A,B);
- TLS off, auth off, HTTP/1.1 keep-alive on, the same client harness for all;
- `RESPONSEFORMAT` pinned to VOTable and CSV for cross-server rungs
  (egernia's parquet/arrow are an egernia-only appendix, never compared);
- `MAXREC` sent explicitly on every request — server defaults differ;
- the generator watches its own CPU and a rung where it ran hot is marked
  invalid, not believed;
- before any timed rung (from the DaCHS phase on): a `stilts taplint`
  conformance gate and a cross-server agreement gate (same query → same row
  count and checksum), so "same data, conformant servers" is verified rather
  than assumed.

## Remaining work (the runbook for the next session)

Phases 1–2 and the phase-4 machinery are done: harness, DaCHS target, gates
(both servers pass taplint; 11/11 classes agree), the `compare` command with
interleaved repetitions, and the `publish` renderer — all live-verified, the
pipeline proven end-to-end with `compare-smoke`. What remains, in order:

1. **Run the comparison on real hardware** (not a laptop). On a dedicated
   Linux box with Docker:
   ```bash
   # egernia stack + corpus
   docker compose up -d --build
   TAP_DATABASE_URL=postgresql://tap:tap@localhost:5432/tap \
     PYTHONPATH=dataset uv run --group dataset python -m egernia_dataset.seed
   scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
   # DaCHS (first start ingests the corpus, ~15 min)
   docker compose -f benchmarks/tap-compare/docker-compose.dachs.yml up -d --build
   # the reference comparison (hours; resumable with --resume <run-name>)
   uv run --group tap-compare python benchmarks/tap-compare compare \
       --targets egernia-local dachs-local --scenario compare
   ```
   Sanity first: `--scenario compare-smoke` end-to-end, then the real one.
   Mind the parity pins: nothing else running on the box; the DaCHS compose
   file pins cpus/mem — pin the egernia stack to the same budget (compose
   override) and record both in the report.
2. **Publish**: `... publish --run <run-name>` renders into
   `docs/performance/<run-name>/`; then add the run to the "Latest by
   family" and "All runs" tables in `docs/performance/index.md` (family:
   `tap-compare`) and check `uv run mkdocs build --strict`.
3. **Pre-registration tag**: before the first run whose numbers will be
   quoted publicly, tag the commit holding the protocol
   (`git tag tap-compare-prereg-v1 && git push --tags`) so the query
   classes, mix, windows and tie rule are provably frozen before the data
   existed. Optionally offer the DaCHS maintainers a look at
   `targets/dachs/` ("correct our deployment") and record the exchange.
4. **Phase 3 — CADC TAP target** (after a working DaCHS comparison): compose
   file + TAP_SCHEMA/obscore init SQL with pgsphere `spoint` columns per
   opencadc docs (Rubin's `lsst-sqre/cadc-tap-postgres` chart is the config
   reference); probe cone-search geometry support before anything else —
   the agreement gate catches wrong answers, not missing capability.
5. **Phase 5 — depth**: async/UWS rung (the runner's `_issue_async` is
   ready), D2 10 GiB tier repeat, egernia-only parquet/arrow appendix,
   open-loop fixed-rate latency rungs at {25,50,70,90}% of each server's
   measured capacity (retires the coordinated-omission critique).

## Claims policy

Results may claim the relative behaviour *of the measured versions, on this
hardware, on this corpus, as deployed by their own documentation, under the
recorded resource pins* — with confidence intervals, per query class, ties
reported as ties (overlapping 95% CIs, or under 10% apart in throughput).
A target whose requests errored beyond 1% cannot win a cell (its error
responses inflate its throughput; the error rate is printed beside the
number); a tripped generator guard, or both targets erroring, voids the
cell's verdict.
They may not claim anything about other corpus sizes, other hardware, other
versions, or classes a gate excluded. Classes where egernia loses are
reported with the same prominence as classes where it wins.

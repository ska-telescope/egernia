# 20261123T213856Z-0809d7b3-tap-compare-scaling

Same-hardware TAP-server resource-scaling comparison: the parity
protocol's corpus, gates, query stream, formats and statistics, with
every server's resource pins raised tier by tier. Where the host
cannot hold every pinned stack of a tier at once, the servers are
measured one at a time under that tier's pins, so repetitions do not
interleave across them; the gates run per tier with the stacks up.
The pins actually applied, as `docker inspect` and `SHOW` saw them, are
under `pins/`. See `benchmarks/tap-compare/final-skycell/PROTOCOL.md` for
the pre-registered design. Where `resources.jsonl` covers a rung, the
resource tables give each server's CPU cores used, CPU time per request
and memory over the rung's window (`resources.csv` has every rung);
rungs measured before the sampler started show `—`.

## Tier 8

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-skycell-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 305.4 ±2.9 | 0.035 ±0.000 | — |
| Q01 | 32 | 285.8 ±6.8 | 0.129 ±0.007 | — |
| Q05 | 8 | 291.1 ±5.7 | 0.037 ±0.001 | — |
| Q05 | 32 | 262.1 ±16.4 | 0.142 ±0.020 | — |
| Q11 | 8 | 30.9 ±0.2 | 0.368 ±0.009 | — |
| Q11 | 32 | 30.9 ±0.1 | 1.281 ±0.030 | — |
| Q13 | 8 | 20.9 ±0.5 | 0.526 ±0.015 | — |
| Q13 | 32 | 20.8 ±0.2 | 1.743 ±0.064 | — |
| mix | 8 | 255.2 ±1.2 | 0.042 ±0.000 | — |
| mix | 32 | 232.2 ±1.7 | 0.159 ±0.002 | — |

### votable

| class | c | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 301.9 ±3.1 | 0.036 ±0.000 | — |
| Q01 | 32 | 282.7 ±1.4 | 0.130 ±0.002 | — |
| Q05 | 8 | 286.9 ±6.8 | 0.037 ±0.002 | — |
| Q05 | 32 | 260.0 ±1.9 | 0.141 ±0.002 | — |
| Q11 | 8 | 28.0 ±0.4 | 0.411 ±0.016 | — |
| Q11 | 32 | 28.1 ±0.2 | 1.402 ±0.010 | — |
| Q13 | 8 | 20.9 ±0.2 | 0.522 ±0.003 | — |
| Q13 | 32 | 20.8 ±0.1 | 1.741 ±0.038 | — |
| mix | 8 | 247.3 ±8.4 | 0.044 ±0.002 | — |
| mix | 32 | 224.7 ±4.3 | 0.167 ±0.010 | — |

### resources, csv

| class | c | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 1.44 | 4.7 ms | 0.88 | 0.89 |
| Q01 | 32 | 1.43 | 5.0 ms | 0.87 | 0.88 |
| Q05 | 8 | 1.63 | 5.6 ms | 0.86 | 0.87 |
| Q05 | 32 | 1.58 | 6.0 ms | 0.86 | 0.86 |
| Q11 | 8 | 2.52 | 81.5 ms | 0.93 | 0.94 |
| Q11 | 32 | 2.50 | 81.2 ms | 1.06 | 1.08 |
| Q13 | 8 | 7.97 | 382.4 ms | 1.08 | 1.11 |
| Q13 | 32 | 7.98 | 386.0 ms | 1.07 | 1.09 |
| mix | 8 | 1.92 | 7.5 ms | 0.87 | 0.88 |
| mix | 32 | 1.85 | 8.0 ms | 0.88 | 0.89 |

### resources, votable

| class | c | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 1.45 | 4.8 ms | 0.88 | 0.88 |
| Q01 | 32 | 1.44 | 5.1 ms | 0.88 | 0.89 |
| Q05 | 8 | 1.64 | 5.7 ms | 0.87 | 0.89 |
| Q05 | 32 | 1.60 | 6.2 ms | 0.88 | 0.88 |
| Q11 | 8 | 3.01 | 107.7 ms | 0.95 | 0.97 |
| Q11 | 32 | 2.99 | 106.6 ms | 1.13 | 1.14 |
| Q13 | 8 | 7.98 | 382.3 ms | 0.98 | 1.01 |
| Q13 | 32 | 7.97 | 384.9 ms | 0.96 | 0.99 |
| mix | 8 | 1.99 | 8.0 ms | 0.83 | 0.84 |
| mix | 32 | 1.92 | 8.5 ms | 0.87 | 0.88 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | egernia-skycell-scaling3 | 1 | 255.2 | 1.92 | 132.9 | 7.5 |
| csv | 32 | egernia-skycell-scaling3 | 1 | 232.2 | 1.85 | 125.2 | 8.0 |
| votable | 8 | egernia-skycell-scaling3 | 1 | 247.3 | 1.99 | 124.3 | 8.0 |
| votable | 32 | egernia-skycell-scaling3 | 1 | 224.7 | 1.92 | 117.1 | 8.5 |

## Tier 16

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-skycell-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 602.3 ±9.7 | 0.021 ±0.001 | — |
| Q01 | 32 | 553.3 ±12.4 | 0.077 ±0.016 | — |
| Q05 | 8 | 550.8 ±48.5 | 0.023 ±0.010 | — |
| Q05 | 32 | 519.8 ±3.1 | 0.081 ±0.004 | — |
| Q11 | 8 | 59.1 ±0.2 | 0.216 ±0.013 | — |
| Q11 | 32 | 60.1 ±0.4 | 0.847 ±0.231 | — |
| Q13 | 8 | 38.1 ±0.1 | 0.273 ±0.003 | — |
| Q13 | 32 | 39.9 ±0.3 | 1.023 ±0.071 | — |
| mix | 8 | 485.8 ±13.7 | 0.025 ±0.005 | — |
| mix | 32 | 456.8 ±6.0 | 0.094 ±0.022 | — |

### votable

| class | c | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 597.1 ±10.4 | 0.020 ±0.005 | — |
| Q01 | 32 | 545.7 ±13.2 | 0.082 ±0.017 | — |
| Q05 | 8 | 554.7 ±2.6 | 0.022 ±0.000 | — |
| Q05 | 32 | 508.8 ±3.7 | 0.084 ±0.018 | — |
| Q11 | 8 | 53.6 ±0.2 | 0.250 ±0.035 | — |
| Q11 | 32 | 54.8 ±0.4 | 0.946 ±0.308 | — |
| Q13 | 8 | 38.2 ±0.2 | 0.274 ±0.003 | — |
| Q13 | 32 | 40.0 ±0.3 | 1.059 ±0.392 | — |
| mix | 8 | 466.7 ±41.5 | 0.027 ±0.010 | — |
| mix | 32 | 444.2 ±2.0 | 0.095 ±0.014 | — |

### resources, csv

| class | c | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 2.71 | 4.5 ms | 1.10 | 1.11 |
| Q01 | 32 | 2.84 | 5.1 ms | 1.09 | 1.10 |
| Q05 | 8 | 2.94 | 5.3 ms | 1.07 | 1.08 |
| Q05 | 32 | 3.16 | 6.1 ms | 1.06 | 1.07 |
| Q11 | 8 | 4.91 | 83.2 ms | 1.12 | 1.13 |
| Q11 | 32 | 5.01 | 83.6 ms | 1.27 | 1.30 |
| Q13 | 8 | 15.17 | 399.1 ms | 1.33 | 1.35 |
| Q13 | 32 | 15.96 | 400.5 ms | 1.38 | 1.41 |
| mix | 8 | 3.58 | 7.4 ms | 1.09 | 1.09 |
| mix | 32 | 3.74 | 8.2 ms | 1.11 | 1.11 |

### resources, votable

| class | c | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 2.75 | 4.6 ms | 0.65 | 0.66 |
| Q01 | 32 | 2.86 | 5.2 ms | 0.66 | 0.66 |
| Q05 | 8 | 3.06 | 5.5 ms | 0.66 | 0.66 |
| Q05 | 32 | 3.20 | 6.3 ms | 0.66 | 0.67 |
| Q11 | 8 | 5.80 | 108.4 ms | 0.75 | 0.77 |
| Q11 | 32 | 5.89 | 108.1 ms | 0.93 | 0.96 |
| Q13 | 8 | 15.17 | 397.4 ms | 1.18 | 1.20 |
| Q13 | 32 | 15.96 | 400.0 ms | 1.21 | 1.25 |
| mix | 8 | 3.65 | 7.8 ms | 0.59 | 0.60 |
| mix | 32 | 3.87 | 8.7 ms | 0.65 | 0.66 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | egernia-skycell-scaling3 | 2 | 485.8 | 3.58 | 135.6 | 7.4 |
| csv | 32 | egernia-skycell-scaling3 | 2 | 456.8 | 3.74 | 122.2 | 8.2 |
| votable | 8 | egernia-skycell-scaling3 | 2 | 466.7 | 3.65 | 127.9 | 7.8 |
| votable | 32 | egernia-skycell-scaling3 | 2 | 444.2 | 3.87 | 114.8 | 8.7 |

## Tier 24

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-skycell-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 785.2 ±203.4 | 0.018 ±0.002 | — |
| Q01 | 32 | 960.0 ±47.5 | 0.056 ±0.029 | — |
| Q05 | 8 | 710.7 ±109.3 | 0.017 ±0.006 | — |
| Q05 | 32 | 901.5 ±57.9 | 0.055 ±0.010 | — |
| Q11 | 8 | 79.5 ±18.6 | 0.166 ±0.032 | — |
| Q11 | 32 | 107.0 ±2.8 | 0.549 ±0.186 | — |
| Q13 | 8 | 50.4 ±0.6 | 0.196 ±0.001 | — |
| Q13 | 32 | 58.0 ±1.1 | 0.832 ±0.142 | — |
| mix | 8 | 495.2 ±14.3 | 0.028 ±0.003 | — |
| mix | 32 | 739.7 ±93.8 | 0.072 ±0.036 | — |

### votable

| class | c | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 937.4 ±238.4 | 0.015 ±0.006 | — |
| Q01 | 32 | 1004.8 ±36.6 | 0.050 ±0.014 | — |
| Q05 | 8 | 764.2 ±205.2 | 0.016 ±0.006 | — |
| Q05 | 32 | 920.0 ±10.2 | 0.052 ±0.014 | — |
| Q11 | 8 | 63.2 ±23.4 | 0.222 ±0.150 | — |
| Q11 | 32 | 96.7 ±0.6 | 0.530 ±0.100 | — |
| Q13 | 8 | 46.9 ±6.8 | 0.216 ±0.039 | — |
| Q13 | 32 | 51.0 ±11.2 | 0.978 ±0.334 | — |
| mix | 8 | 669.5 ±158.6 | 0.019 ±0.005 | — |
| mix | 32 | 814.9 ±1.4 | 0.067 ±0.024 | — |

### resources, csv

| class | c | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.58 | 4.6 ms | 1.52 | 1.52 |
| Q01 | 32 | 5.35 | 5.6 ms | 1.48 | 1.51 |
| Q05 | 8 | 4.00 | 5.6 ms | 1.44 | 1.46 |
| Q05 | 32 | 5.99 | 6.6 ms | 1.43 | 1.45 |
| Q11 | 8 | 6.76 | 85.0 ms | 1.49 | 1.51 |
| Q11 | 32 | 9.50 | 88.9 ms | 1.67 | 1.72 |
| Q13 | 8 | 20.07 | 398.9 ms | 1.78 | 1.80 |
| Q13 | 32 | 23.93 | 414.1 ms | 1.88 | 1.91 |
| mix | 8 | 4.08 | 8.2 ms | 1.50 | 1.51 |
| mix | 32 | 6.66 | 9.0 ms | 1.52 | 1.52 |

### resources, votable

| class | c | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.97 | 4.2 ms | 1.01 | 1.01 |
| Q01 | 32 | 5.52 | 5.5 ms | 1.01 | 1.01 |
| Q05 | 8 | 4.11 | 5.4 ms | 1.01 | 1.02 |
| Q05 | 32 | 6.13 | 6.7 ms | 1.01 | 1.03 |
| Q11 | 8 | 6.79 | 107.4 ms | 1.10 | 1.12 |
| Q11 | 32 | 10.85 | 112.4 ms | 1.28 | 1.31 |
| Q13 | 8 | 18.99 | 405.6 ms | 1.59 | 1.63 |
| Q13 | 32 | 21.41 | 420.2 ms | 1.69 | 1.73 |
| mix | 8 | 5.08 | 7.6 ms | 0.87 | 0.88 |
| mix | 32 | 7.36 | 9.0 ms | 0.99 | 1.01 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | egernia-skycell-scaling3 | 4 | 495.2 | 4.08 | 121.3 | 8.2 |
| csv | 32 | egernia-skycell-scaling3 | 4 | 739.7 | 6.66 | 111.0 | 9.0 |
| votable | 8 | egernia-skycell-scaling3 | 4 | 669.5 | 5.08 | 131.9 | 7.6 |
| votable | 32 | egernia-skycell-scaling3 | 4 | 814.9 | 7.36 | 110.8 | 9.0 |

## Claims

This run may claim the relative behaviour *of these versions, on this
hardware, on this corpus, as deployed by their own documentation,
under the recorded resource pins* — nothing else. A `tie` verdict is
pre-registered: overlapping 95% intervals, or under 10% apart
in throughput. Classes a gate excluded are absent, not hidden.

## Threats to validity

- The corpus is generated by egernia's own seeder; its distributions
  may flatter egernia's index choices.
- The query classes descend from egernia's own performance history.
- The team operates egernia expertly and the other servers from their
  documentation.
- Single hardware, single run window; versions frozen at the recorded
  digests.
- Within a tier the servers were measured one after the other, not
  interleaved: host drift over a tier's hours lands on one server.
  The order alternates between tiers (recorded in `pins/`).

## Reproduce with

```bash
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
benchmarks/tap-compare/scaling/run.sh
```

Environment: see `environment.json` (git 0809d7b3, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Experiment 3 (the scaling tiers) of the pre-registered skycell rerun, egernia measured again alone at `0809d7b3`. Its opponents' columns are those of `20261120T184934Z-61542dc1-tap-compare-scaling`. **Tier 24 of this run is disturbed and is superseded by `20261124T020908Z-fb71a9ae-tap-compare-scaling`**; tiers 8 and 16 stand.
- **Why it exists.** The published skycell runs found two faults in egernia itself, fixed in PR #230: HTTP 500 on Q13 at 32 clients with more than one worker (PostgreSQL's `/dev/shm` left at 64 MiB), and Q11 slowed by a spool file whose writes the kernel throttled under the container's memory limit (`docs/postgres-performance.md`). The project lead decided to measure **egernia alone** again on the fixed revision and not to measure DaCHS and argus again (amendment 4, `tap-compare-final-skycell-prereg-v5`).
- **What that means for reading it.** This report has one server. A cell's verdict is computed by the unchanged tie rule from egernia's three repetitions here and DaCHS's and argus's three repetitions in the published run named below. **The servers were not interleaved and were measured days apart**, so nothing inside a cell cancels a drift of the host; amendment 4 states this trade and registers a control for it (E3).
- **Gates.** They ran against all three servers before anything was timed: all three `taplint` PASS and three-way agreement on 11/11 classes, on the fixed revision. DaCHS and argus were up and idle on their own cores while egernia was timed.
- **180 rungs, 3,668,134 requests, no error on any rung** (E1 holds at every tier); generator peak 0.505.
- **Tier 8: egernia 16, argus 4 of 20 cells** (published 12 / 8). Q11 is higher by 1.42-1.52× in all four cells; Q13 and the mix reproduce their published values within 1%; the eight control cells tie. Mix, CSV, c=32: 232.2 rps on 1.85 cores, 8.0 ms of CPU per request.
- **Tier 16: egernia 17, ties 2, argus 1** (published 16 / 2 / 2). Q11 is higher by 1.50-1.68×; Q13 and the mix tie; the eight control cells tie. Mix, CSV, c=32: 456.8 rps on 3.74 cores, 8.2 ms. Q13 at c=32 has no error (one rung at 1.2% in the published run).
- **Tier 24 was measured through a disturbance of the host.** It ran from 00:35Z to 02:05Z on 2026-11-24. The host's `sar` record shows a job that is not this benchmark's from 01:10Z to 01:50Z: 154,725 blocks/s written in the first ten-minute interval, a load average of 53 on 30 cores, 5-7% I/O wait. The same burst is in the record at the same hour on 2026-11-22 and 2026-11-23. **28 of the 60 rungs ended inside it**: the CSV mix at c=8 measured 490-502 rps against 640-663 published, the CSV mix at c=32 740 against 823, Q13 in VOTable at c=32 51 against 61, Q01 and Q05 at c=32 6% lower. The 32 rungs outside the window reproduce the published values or exceed them. Amendment 5 (`tap-compare-final-skycell-prereg-v6`) measures the tier again in full; this block is kept here as measured.

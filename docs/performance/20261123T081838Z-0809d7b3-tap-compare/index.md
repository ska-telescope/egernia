# 20261123T081838Z-0809d7b3-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: egernia on skycell in `benchmarks/tap-compare/final-skycell/pins/egernia-w1.yml` + `skycell.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=1`; `benchmarks/tap-compare/final-skycell/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-skycell-w1 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | egernia-skycell-w1 rps | egernia-skycell-w1 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 1 | 228.4 ±1.1 | 0.005 ±0.000 | — |
| Q01 | 4 | 318.2 ±1.5 | 0.016 ±0.000 | — |
| Q01 | 8 | 305.8 ±2.0 | 0.035 ±0.000 | — |
| Q01 | 32 | 285.2 ±11.0 | 0.129 ±0.007 | — |
| Q02 | 1 | 136.0 ±4.4 | 0.012 ±0.000 | — |
| Q02 | 4 | 259.7 ±3.4 | 0.021 ±0.000 | — |
| Q02 | 8 | 256.9 ±2.2 | 0.042 ±0.001 | — |
| Q02 | 32 | 231.1 ±0.8 | 0.159 ±0.002 | — |
| Q03 | 1 | 162.4 ±3.0 | 0.007 ±0.000 | — |
| Q03 | 4 | 280.4 ±1.6 | 0.018 ±0.000 | — |
| Q03 | 8 | 272.4 ±1.2 | 0.039 ±0.001 | — |
| Q03 | 32 | 244.2 ±1.7 | 0.150 ±0.002 | — |
| Q04 | 1 | 101.9 ±2.3 | 0.011 ±0.000 | — |
| Q04 | 4 | 223.9 ±6.2 | 0.023 ±0.001 | — |
| Q04 | 8 | 229.2 ±2.1 | 0.046 ±0.001 | — |
| Q04 | 32 | 209.8 ±1.4 | 0.174 ±0.001 | — |
| Q05 | 1 | 196.5 ±3.5 | 0.006 ±0.000 | — |
| Q05 | 4 | 303.2 ±1.3 | 0.017 ±0.000 | — |
| Q05 | 8 | 294.8 ±1.2 | 0.036 ±0.000 | — |
| Q05 | 32 | 266.1 ±3.7 | 0.137 ±0.003 | — |
| Q06 | 1 | 161.9 ±3.0 | 0.008 ±0.000 | — |
| Q06 | 4 | 247.1 ±6.4 | 0.021 ±0.001 | — |
| Q06 | 8 | 243.9 ±1.1 | 0.044 ±0.001 | — |
| Q06 | 32 | 221.5 ±2.0 | 0.166 ±0.003 | — |
| Q07 | 1 | 182.6 ±2.0 | 0.006 ±0.000 | — |
| Q07 | 4 | 288.5 ±2.5 | 0.018 ±0.000 | — |
| Q07 | 8 | 279.6 ±2.5 | 0.038 ±0.000 | — |
| Q07 | 32 | 253.0 ±1.1 | 0.145 ±0.001 | — |
| Q10 | 1 | 86.6 ±1.1 | 0.014 ±0.001 | — |
| Q10 | 4 | 151.2 ±0.1 | 0.034 ±0.000 | — |
| Q10 | 8 | 152.2 ±0.9 | 0.070 ±0.001 | — |
| Q10 | 32 | 143.2 ±0.3 | 0.260 ±0.001 | — |
| Q11 | 1 | 18.2 ±0.7 | 0.070 ±0.001 | — |
| Q11 | 4 | 30.4 ±0.0 | 0.187 ±0.003 | — |
| Q11 | 8 | 31.0 ±0.3 | 0.366 ±0.006 | — |
| Q11 | 32 | 30.7 ±0.4 | 1.287 ±0.031 | — |
| Q12 | 1 | 200.8 ±2.3 | 0.006 ±0.000 | — |
| Q12 | 4 | 309.0 ±1.7 | 0.017 ±0.000 | — |
| Q12 | 8 | 299.3 ±5.7 | 0.036 ±0.001 | — |
| Q12 | 32 | 241.7 ±1.8 | 0.162 ±0.001 | — |
| Q13 | 1 | 8.2 ±0.3 | 0.164 ±0.004 | — |
| Q13 | 4 | 19.3 ±0.0 | 0.273 ±0.005 | — |
| Q13 | 8 | 20.2 ±0.5 | 0.544 ±0.002 | — |
| Q13 | 32 | 20.3 ±0.1 | 1.782 ±0.014 | — |
| mix | 1 | 151.4 ±2.6 | 0.011 ±0.000 | — |
| mix | 4 | 262.2 ±1.2 | 0.021 ±0.000 | — |
| mix | 8 | 257.3 ±2.5 | 0.042 ±0.000 | — |
| mix | 32 | 232.4 ±3.2 | 0.160 ±0.004 | — |

## votable

| class | c | egernia-skycell-w1 rps | egernia-skycell-w1 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 1 | 228.4 ±3.1 | 0.005 ±0.000 | — |
| Q01 | 4 | 319.2 ±9.5 | 0.016 ±0.001 | — |
| Q01 | 8 | 304.6 ±3.8 | 0.035 ±0.001 | — |
| Q01 | 32 | 286.6 ±1.1 | 0.128 ±0.000 | — |
| Q02 | 1 | 131.1 ±2.8 | 0.012 ±0.000 | — |
| Q02 | 4 | 253.0 ±3.6 | 0.022 ±0.000 | — |
| Q02 | 8 | 251.9 ±0.5 | 0.043 ±0.000 | — |
| Q02 | 32 | 227.1 ±1.8 | 0.161 ±0.002 | — |
| Q03 | 1 | 156.2 ±0.8 | 0.008 ±0.000 | — |
| Q03 | 4 | 274.1 ±2.5 | 0.019 ±0.000 | — |
| Q03 | 8 | 268.0 ±3.4 | 0.040 ±0.001 | — |
| Q03 | 32 | 240.4 ±2.3 | 0.153 ±0.001 | — |
| Q04 | 1 | 97.5 ±0.9 | 0.012 ±0.000 | — |
| Q04 | 4 | 217.0 ±1.8 | 0.023 ±0.001 | — |
| Q04 | 8 | 219.0 ±8.7 | 0.048 ±0.003 | — |
| Q04 | 32 | 196.5 ±8.3 | 0.191 ±0.027 | — |
| Q05 | 1 | 183.4 ±10.6 | 0.006 ±0.001 | — |
| Q05 | 4 | 297.6 ±1.2 | 0.017 ±0.000 | — |
| Q05 | 8 | 288.3 ±0.6 | 0.037 ±0.000 | — |
| Q05 | 32 | 259.4 ±0.5 | 0.141 ±0.001 | — |
| Q06 | 1 | 148.3 ±1.1 | 0.008 ±0.000 | — |
| Q06 | 4 | 240.5 ±3.7 | 0.021 ±0.000 | — |
| Q06 | 8 | 235.2 ±1.2 | 0.045 ±0.000 | — |
| Q06 | 32 | 213.4 ±0.6 | 0.173 ±0.001 | — |
| Q07 | 1 | 174.5 ±2.1 | 0.007 ±0.000 | — |
| Q07 | 4 | 281.6 ±1.3 | 0.018 ±0.000 | — |
| Q07 | 8 | 273.2 ±0.4 | 0.039 ±0.000 | — |
| Q07 | 32 | 245.3 ±1.4 | 0.149 ±0.002 | — |
| Q10 | 1 | 74.7 ±1.7 | 0.016 ±0.001 | — |
| Q10 | 4 | 142.7 ±2.4 | 0.035 ±0.001 | — |
| Q10 | 8 | 143.0 ±1.0 | 0.074 ±0.001 | — |
| Q10 | 32 | 134.4 ±0.6 | 0.276 ±0.001 | — |
| Q11 | 1 | 13.1 ±0.2 | 0.098 ±0.001 | — |
| Q11 | 4 | 27.9 ±0.1 | 0.230 ±0.004 | — |
| Q11 | 8 | 28.2 ±0.2 | 0.416 ±0.013 | — |
| Q11 | 32 | 28.0 ±0.2 | 1.400 ±0.035 | — |
| Q12 | 1 | 195.8 ±3.4 | 0.006 ±0.000 | — |
| Q12 | 4 | 304.2 ±4.0 | 0.017 ±0.000 | — |
| Q12 | 8 | 295.1 ±3.1 | 0.036 ±0.001 | — |
| Q12 | 32 | 266.5 ±2.1 | 0.137 ±0.002 | — |
| Q13 | 1 | 8.3 ±0.2 | 0.164 ±0.005 | — |
| Q13 | 4 | 19.3 ±0.1 | 0.273 ±0.005 | — |
| Q13 | 8 | 20.4 ±0.2 | 0.535 ±0.010 | — |
| Q13 | 32 | 20.2 ±0.3 | 1.789 ±0.050 | — |
| mix | 1 | 142.6 ±2.8 | 0.012 ±0.000 | — |
| mix | 4 | 255.2 ±1.8 | 0.022 ±0.000 | — |
| mix | 8 | 251.3 ±1.4 | 0.043 ±0.000 | — |
| mix | 32 | 228.4 ±0.5 | 0.162 ±0.002 | — |

## resources, csv

| class | c | egernia-skycell-w1 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.78 | 3.4 ms | 0.90 | 0.90 |
| Q01 | 4 | 1.38 | 4.3 ms | 0.90 | 0.91 |
| Q01 | 8 | 1.44 | 4.7 ms | 0.90 | 0.90 |
| Q01 | 32 | 1.43 | 5.0 ms | 0.90 | 0.90 |
| Q02 | 1 | 0.92 | 6.7 ms | 0.89 | 0.90 |
| Q02 | 4 | 2.01 | 7.8 ms | 0.89 | 0.89 |
| Q02 | 8 | 2.14 | 8.3 ms | 0.89 | 0.90 |
| Q02 | 32 | 2.05 | 8.9 ms | 0.89 | 0.90 |
| Q03 | 1 | 0.88 | 5.4 ms | 0.89 | 0.90 |
| Q03 | 4 | 1.79 | 6.4 ms | 0.89 | 0.90 |
| Q03 | 8 | 1.86 | 6.8 ms | 0.89 | 0.91 |
| Q03 | 32 | 1.79 | 7.3 ms | 0.90 | 0.90 |
| Q04 | 1 | 0.99 | 9.7 ms | 0.89 | 0.91 |
| Q04 | 4 | 2.38 | 10.6 ms | 0.90 | 0.91 |
| Q04 | 8 | 2.56 | 11.2 ms | 0.90 | 0.91 |
| Q04 | 32 | 2.45 | 11.7 ms | 0.90 | 0.91 |
| Q05 | 1 | 0.81 | 4.1 ms | 0.90 | 0.90 |
| Q05 | 4 | 1.56 | 5.1 ms | 0.90 | 0.91 |
| Q05 | 8 | 1.62 | 5.5 ms | 0.89 | 0.90 |
| Q05 | 32 | 1.58 | 5.9 ms | 0.89 | 0.89 |
| Q06 | 1 | 0.93 | 5.7 ms | 0.89 | 0.89 |
| Q06 | 4 | 1.69 | 6.8 ms | 0.89 | 0.90 |
| Q06 | 8 | 1.74 | 7.1 ms | 0.89 | 0.90 |
| Q06 | 32 | 1.69 | 7.6 ms | 0.89 | 0.89 |
| Q07 | 1 | 0.85 | 4.7 ms | 0.89 | 0.90 |
| Q07 | 4 | 1.62 | 5.6 ms | 0.90 | 0.91 |
| Q07 | 8 | 1.69 | 6.1 ms | 0.90 | 0.91 |
| Q07 | 32 | 1.65 | 6.5 ms | 0.90 | 0.90 |
| Q10 | 1 | 1.17 | 13.5 ms | 0.90 | 0.91 |
| Q10 | 4 | 2.21 | 14.6 ms | 0.90 | 0.90 |
| Q10 | 8 | 2.26 | 14.9 ms | 0.91 | 0.92 |
| Q10 | 32 | 2.19 | 15.3 ms | 0.91 | 0.92 |
| Q11 | 1 | 1.50 | 82.5 ms | 0.92 | 0.92 |
| Q11 | 4 | 2.47 | 81.4 ms | 0.94 | 0.96 |
| Q11 | 8 | 2.54 | 82.2 ms | 0.97 | 0.98 |
| Q11 | 32 | 2.52 | 82.5 ms | 1.10 | 1.12 |
| Q12 | 1 | 0.80 | 4.0 ms | 1.07 | 1.08 |
| Q12 | 4 | 1.53 | 5.0 ms | 1.07 | 1.07 |
| Q12 | 8 | 1.60 | 5.3 ms | 1.07 | 1.07 |
| Q12 | 32 | 1.56 | 6.5 ms | 1.07 | 1.08 |
| Q13 | 1 | 2.75 | 335.5 ms | 1.07 | 1.09 |
| Q13 | 4 | 7.53 | 391.4 ms | 1.09 | 1.10 |
| Q13 | 8 | 7.98 | 396.3 ms | 1.11 | 1.13 |
| Q13 | 32 | 7.97 | 394.6 ms | 1.11 | 1.13 |
| mix | 1 | 0.91 | 6.0 ms | 0.88 | 0.89 |
| mix | 4 | 1.86 | 7.1 ms | 0.88 | 0.89 |
| mix | 8 | 1.93 | 7.5 ms | 0.89 | 0.89 |
| mix | 32 | 1.86 | 8.0 ms | 0.90 | 0.92 |

## resources, votable

| class | c | egernia-skycell-w1 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.79 | 3.4 ms | 0.87 | 0.87 |
| Q01 | 4 | 1.40 | 4.4 ms | 0.87 | 0.88 |
| Q01 | 8 | 1.45 | 4.8 ms | 0.87 | 0.87 |
| Q01 | 32 | 1.44 | 5.0 ms | 0.87 | 0.88 |
| Q02 | 1 | 0.94 | 7.2 ms | 0.87 | 0.88 |
| Q02 | 4 | 2.08 | 8.2 ms | 0.87 | 0.88 |
| Q02 | 8 | 2.21 | 8.8 ms | 0.87 | 0.88 |
| Q02 | 32 | 2.12 | 9.3 ms | 0.88 | 0.89 |
| Q03 | 1 | 0.90 | 5.8 ms | 0.88 | 0.89 |
| Q03 | 4 | 1.85 | 6.7 ms | 0.87 | 0.88 |
| Q03 | 8 | 1.90 | 7.1 ms | 0.86 | 0.88 |
| Q03 | 32 | 1.84 | 7.6 ms | 0.86 | 0.86 |
| Q04 | 1 | 0.99 | 10.1 ms | 0.86 | 0.87 |
| Q04 | 4 | 2.45 | 11.3 ms | 0.86 | 0.88 |
| Q04 | 8 | 2.61 | 11.9 ms | 0.86 | 0.86 |
| Q04 | 32 | 2.48 | 12.6 ms | 0.87 | 0.88 |
| Q05 | 1 | 0.82 | 4.5 ms | 0.87 | 0.87 |
| Q05 | 4 | 1.59 | 5.3 ms | 0.87 | 0.88 |
| Q05 | 8 | 1.65 | 5.7 ms | 0.87 | 0.88 |
| Q05 | 32 | 1.62 | 6.2 ms | 0.87 | 0.87 |
| Q06 | 1 | 0.96 | 6.5 ms | 0.87 | 0.88 |
| Q06 | 4 | 1.81 | 7.5 ms | 0.87 | 0.87 |
| Q06 | 8 | 1.86 | 7.9 ms | 0.87 | 0.88 |
| Q06 | 32 | 1.79 | 8.4 ms | 0.88 | 0.89 |
| Q07 | 1 | 0.87 | 5.0 ms | 0.87 | 0.88 |
| Q07 | 4 | 1.67 | 5.9 ms | 0.87 | 0.88 |
| Q07 | 8 | 1.73 | 6.3 ms | 0.87 | 0.87 |
| Q07 | 32 | 1.69 | 6.9 ms | 0.87 | 0.88 |
| Q10 | 1 | 1.18 | 15.7 ms | 0.88 | 0.88 |
| Q10 | 4 | 2.47 | 17.3 ms | 0.88 | 0.89 |
| Q10 | 8 | 2.51 | 17.5 ms | 0.88 | 0.89 |
| Q10 | 32 | 2.42 | 18.0 ms | 0.90 | 0.91 |
| Q11 | 1 | 1.40 | 106.2 ms | 0.91 | 0.92 |
| Q11 | 4 | 3.02 | 108.2 ms | 0.94 | 0.95 |
| Q11 | 8 | 3.03 | 107.7 ms | 0.97 | 0.98 |
| Q11 | 32 | 3.00 | 107.1 ms | 1.13 | 1.15 |
| Q12 | 1 | 0.81 | 4.1 ms | 0.89 | 0.90 |
| Q12 | 4 | 1.56 | 5.1 ms | 0.89 | 0.90 |
| Q12 | 8 | 1.62 | 5.5 ms | 0.89 | 0.89 |
| Q12 | 32 | 1.58 | 5.9 ms | 0.88 | 0.90 |
| Q13 | 1 | 2.75 | 331.1 ms | 0.88 | 0.88 |
| Q13 | 4 | 7.54 | 390.3 ms | 0.90 | 0.91 |
| Q13 | 8 | 7.98 | 392.2 ms | 0.92 | 0.94 |
| Q13 | 32 | 7.98 | 396.1 ms | 0.92 | 0.95 |
| mix | 1 | 0.94 | 6.6 ms | 0.83 | 0.85 |
| mix | 4 | 1.93 | 7.6 ms | 0.83 | 0.83 |
| mix | 8 | 2.00 | 8.0 ms | 0.83 | 0.85 |
| mix | 32 | 1.93 | 8.4 ms | 0.87 | 0.88 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | egernia-skycell-w1 | 1 | 151.4 | 0.91 | 165.5 | 6.0 |
| csv | 4 | egernia-skycell-w1 | 1 | 262.2 | 1.86 | 140.9 | 7.1 |
| csv | 8 | egernia-skycell-w1 | 1 | 257.3 | 1.93 | 133.2 | 7.5 |
| csv | 32 | egernia-skycell-w1 | 1 | 232.4 | 1.86 | 124.7 | 8.0 |
| votable | 1 | egernia-skycell-w1 | 1 | 142.6 | 0.94 | 152.3 | 6.6 |
| votable | 4 | egernia-skycell-w1 | 1 | 255.2 | 1.93 | 132.1 | 7.6 |
| votable | 8 | egernia-skycell-w1 | 1 | 251.3 | 2.00 | 125.4 | 8.0 |
| votable | 32 | egernia-skycell-w1 | 1 | 228.4 | 1.93 | 118.5 | 8.4 |

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

## Reproduce with

```bash
scripts/export_obscore_snapshot.sh benchmarks/tap-compare/corpus
docker compose -f docker-compose.yml \
    -f benchmarks/tap-compare/final-skycell/pins/egernia-w1.yml \
    -f benchmarks/tap-compare/final-skycell/pins/skycell.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets egernia-skycell-w1 --scenario <scenario>
```

Environment: see `environment.json` (git 0809d7b3, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Phase A (**Table A, one-process parity**) of the pre-registered skycell rerun, egernia with one uvicorn worker, measured again alone at `0809d7b3`. Its opponents' columns are those of `20261117T203446Z-d360fb1e-tap-compare`.
- **Why it exists.** The published skycell runs found two faults in egernia itself, fixed in PR #230: HTTP 500 on Q13 at 32 clients with more than one worker (PostgreSQL's `/dev/shm` left at 64 MiB), and Q11 slowed by a spool file whose writes the kernel throttled under the container's memory limit (`docs/postgres-performance.md`). The project lead decided to measure **egernia alone** again on the fixed revision and not to measure DaCHS and argus again (amendment 4, `tap-compare-final-skycell-prereg-v5`).
- **What that means for reading it.** This report has one server. A cell's verdict is computed by the unchanged tie rule from egernia's three repetitions here and DaCHS's and argus's three repetitions in the published run named below. **The servers were not interleaved and were measured days apart**, so nothing inside a cell cancels a drift of the host; amendment 4 states this trade and registers a control for it (E3).
- **Gates.** They ran against all three servers before anything was timed: all three `taplint` PASS and three-way agreement on 11/11 classes, on the fixed revision. DaCHS and argus were up and idle on their own cores while egernia was timed.
- **Verdicts against the published DaCHS and argus rungs: egernia 81, ties 8, argus 7, DaCHS 0, of 96 cells** (the published Table A was 75 / 10 / 11 / 0). 288 rungs, 3,325,110 requests, **no error on any rung**; generator peak 0.34.
- **E1 holds.** No rung has an error. The nine 503 responses that Q11 returned at c=32 in two rungs of the published run did not recur.
- **Q11 is higher in all eight cells**, by 1.27-1.76×: CSV 13.1 → 18.2 rps at c=1 and 19.6 → 30.7 at c=32; VOTable 10.3 → 13.1 and 15.9 → 28.0. The spool file cost this class a third of its throughput with a single worker too. It moves Q11 from egernia 2 / ties 2 / argus 4 to egernia 7 / ties 1. The sixth cell that changes hands is Q01 in one cell, a tie that becomes egernia's although its throughput ties its published value: a verdict at the margin of the rule, not a gain.
- **Q13 and the mix tie their published values in all 16 cells** (0.96-1.03×), as expected with one worker, whose pool admits eight queries.
- **E3 (control): 71 of 72 cells tie.** On Q01-Q07, Q10 and Q12, which the fixes cannot touch, egernia's cells tie its own published cells, with one exception: **Q12 in CSV at c=32 is 11% lower** (270.5 → 241.7 rps). By amendment 4's rule Q12's verdicts carry the caveat that the host may have drifted for that class; egernia takes all eight Q12 cells in both runs, so no verdict depends on it. The cause was not investigated.
- **Where argus still leads**: Q01 at c=8 and c=32 (4 cells), Q04 at c=32 (2) and Q10 in CSV at c=32 (1), the classes where one Python process is the ceiling.

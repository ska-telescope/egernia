# 20261123T145609Z-0809d7b3-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: egernia on skycell in `benchmarks/tap-compare/final-skycell/pins/egernia-w8.yml` + `skycell.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=8`, PostgreSQL parallel budget 144/152; `benchmarks/tap-compare/final-skycell/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-skycell-w8 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | egernia-skycell-w8 rps | egernia-skycell-w8 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 1 | 222.1 ±5.8 | 0.005 ±0.000 | — |
| Q01 | 4 | 594.5 ±199.2 | 0.010 ±0.005 | — |
| Q01 | 8 | 807.8 ±65.1 | 0.018 ±0.006 | — |
| Q01 | 32 | 993.8 ±183.3 | 0.078 ±0.036 | — |
| Q02 | 1 | 131.0 ±10.5 | 0.012 ±0.001 | — |
| Q02 | 4 | 333.6 ±53.0 | 0.018 ±0.003 | — |
| Q02 | 8 | 480.9 ±51.2 | 0.026 ±0.006 | — |
| Q02 | 32 | 638.1 ±34.4 | 0.100 ±0.028 | — |
| Q03 | 1 | 160.6 ±4.5 | 0.007 ±0.000 | — |
| Q03 | 4 | 410.1 ±3.4 | 0.013 ±0.000 | — |
| Q03 | 8 | 533.3 ±96.2 | 0.025 ±0.010 | — |
| Q03 | 32 | 723.3 ±54.5 | 0.087 ±0.030 | — |
| Q04 | 1 | 102.1 ±1.6 | 0.011 ±0.000 | — |
| Q04 | 4 | 266.6 ±32.4 | 0.020 ±0.003 | — |
| Q04 | 8 | 389.8 ±18.0 | 0.029 ±0.001 | — |
| Q04 | 32 | 544.4 ±12.0 | 0.102 ±0.009 | — |
| Q05 | 1 | 193.0 ±4.6 | 0.006 ±0.000 | — |
| Q05 | 4 | 520.3 ±57.1 | 0.010 ±0.002 | — |
| Q05 | 8 | 673.2 ±30.4 | 0.017 ±0.001 | — |
| Q05 | 32 | 841.2 ±91.4 | 0.081 ±0.030 | — |
| Q06 | 1 | 159.8 ±3.4 | 0.008 ±0.000 | — |
| Q06 | 4 | 358.0 ±89.3 | 0.016 ±0.005 | — |
| Q06 | 8 | 517.7 ±155.6 | 0.027 ±0.016 | — |
| Q06 | 32 | 676.9 ±60.6 | 0.085 ±0.023 | — |
| Q07 | 1 | 176.2 ±10.0 | 0.007 ±0.001 | — |
| Q07 | 4 | 475.3 ±43.0 | 0.011 ±0.002 | — |
| Q07 | 8 | 581.9 ±97.5 | 0.022 ±0.006 | — |
| Q07 | 32 | 807.4 ±35.7 | 0.084 ±0.031 | — |
| Q10 | 1 | 85.1 ±4.2 | 0.014 ±0.001 | — |
| Q10 | 4 | 215.5 ±44.9 | 0.025 ±0.008 | — |
| Q10 | 8 | 280.8 ±30.5 | 0.043 ±0.009 | — |
| Q10 | 32 | 381.7 ±20.4 | 0.148 ±0.025 | — |
| Q11 | 1 | 17.5 ±0.4 | 0.072 ±0.001 | — |
| Q11 | 4 | 48.8 ±0.2 | 0.107 ±0.001 | — |
| Q11 | 8 | 58.5 ±2.6 | 0.224 ±0.065 | — |
| Q11 | 32 | 72.8 ±0.4 | 0.995 ±0.556 | — |
| Q12 | 1 | 197.3 ±3.0 | 0.006 ±0.000 | — |
| Q12 | 4 | 488.6 ±395.5 | 0.011 ±0.012 | — |
| Q12 | 8 | 669.5 ±157.1 | 0.018 ±0.005 | — |
| Q12 | 32 | 829.2 ±227.7 | 0.094 ±0.024 | — |
| Q13 | 1 | 8.3 ±0.1 | 0.164 ±0.002 | — |
| Q13 | 4 | 19.1 ±0.2 | 0.279 ±0.004 | — |
| Q13 | 8 | 20.2 ±0.4 | 0.539 ±0.017 | — |
| Q13 | 32 | 20.1 ±0.4 | 2.348 ±0.555 | — |
| mix | 1 | 148.0 ±6.5 | 0.011 ±0.001 | — |
| mix | 4 | 393.8 ±1.9 | 0.016 ±0.000 | — |
| mix | 8 | 499.9 ±112.3 | 0.028 ±0.010 | — |
| mix | 32 | 672.1 ±95.3 | 0.100 ±0.055 | — |

## votable

| class | c | egernia-skycell-w8 rps | egernia-skycell-w8 p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 1 | 226.1 ±1.8 | 0.005 ±0.000 | — |
| Q01 | 4 | 612.5 ±47.0 | 0.009 ±0.001 | — |
| Q01 | 8 | 802.5 ±267.5 | 0.016 ±0.007 | — |
| Q01 | 32 | 1003.3 ±30.3 | 0.065 ±0.013 | — |
| Q02 | 1 | 127.7 ±6.1 | 0.012 ±0.000 | — |
| Q02 | 4 | 343.9 ±11.2 | 0.017 ±0.001 | — |
| Q02 | 8 | 454.9 ±9.7 | 0.026 ±0.001 | — |
| Q02 | 32 | 619.5 ±15.0 | 0.092 ±0.027 | — |
| Q03 | 1 | 150.6 ±7.2 | 0.008 ±0.001 | — |
| Q03 | 4 | 405.6 ±28.9 | 0.013 ±0.001 | — |
| Q03 | 8 | 553.2 ±38.4 | 0.022 ±0.000 | — |
| Q03 | 32 | 712.9 ±29.0 | 0.083 ±0.021 | — |
| Q04 | 1 | 96.3 ±3.3 | 0.012 ±0.001 | — |
| Q04 | 4 | 258.1 ±34.7 | 0.020 ±0.004 | — |
| Q04 | 8 | 373.6 ±20.5 | 0.030 ±0.004 | — |
| Q04 | 32 | 507.1 ±38.1 | 0.122 ±0.054 | — |
| Q05 | 1 | 184.8 ±9.4 | 0.006 ±0.000 | — |
| Q05 | 4 | 451.6 ±105.8 | 0.012 ±0.004 | — |
| Q05 | 8 | 594.4 ±219.5 | 0.021 ±0.005 | — |
| Q05 | 32 | 822.1 ±74.6 | 0.084 ±0.072 | — |
| Q06 | 1 | 145.7 ±1.3 | 0.009 ±0.000 | — |
| Q06 | 4 | 359.9 ±36.7 | 0.015 ±0.000 | — |
| Q06 | 8 | 504.0 ±79.5 | 0.025 ±0.009 | — |
| Q06 | 32 | 639.5 ±42.1 | 0.102 ±0.047 | — |
| Q07 | 1 | 164.2 ±18.3 | 0.007 ±0.001 | — |
| Q07 | 4 | 422.1 ±145.4 | 0.013 ±0.006 | — |
| Q07 | 8 | 569.4 ±85.2 | 0.022 ±0.005 | — |
| Q07 | 32 | 786.5 ±10.9 | 0.072 ±0.010 | — |
| Q10 | 1 | 71.8 ±1.6 | 0.017 ±0.001 | — |
| Q10 | 4 | 185.5 ±22.7 | 0.028 ±0.005 | — |
| Q10 | 8 | 265.6 ±11.6 | 0.041 ±0.003 | — |
| Q10 | 32 | 337.1 ±14.8 | 0.162 ±0.050 | — |
| Q11 | 1 | 13.2 ±0.3 | 0.097 ±0.002 | — |
| Q11 | 4 | 38.6 ±0.6 | 0.124 ±0.001 | — |
| Q11 | 8 | 49.1 ±4.0 | 0.221 ±0.036 | — |
| Q11 | 32 | 56.3 ±0.6 | 1.044 ±0.207 | — |
| Q12 | 1 | 193.9 ±0.4 | 0.006 ±0.000 | — |
| Q12 | 4 | 489.5 ±71.7 | 0.011 ±0.001 | — |
| Q12 | 8 | 663.9 ±101.0 | 0.018 ±0.001 | — |
| Q12 | 32 | 858.5 ±62.8 | 0.066 ±0.010 | — |
| Q13 | 1 | 8.2 ±0.2 | 0.164 ±0.004 | — |
| Q13 | 4 | 19.3 ±0.1 | 0.276 ±0.004 | — |
| Q13 | 8 | 20.1 ±0.4 | 0.545 ±0.004 | — |
| Q13 | 32 | 20.0 ±0.4 | 2.223 ±0.113 | — |
| mix | 1 | 137.6 ±7.3 | 0.013 ±0.001 | — |
| mix | 4 | 334.9 ±65.6 | 0.020 ±0.003 | — |
| mix | 8 | 490.1 ±119.5 | 0.028 ±0.007 | — |
| mix | 32 | 662.8 ±6.9 | 0.088 ±0.015 | — |

## resources, csv

| class | c | egernia-skycell-w8 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.78 | 3.5 ms | 2.12 | 2.13 |
| Q01 | 4 | 2.43 | 4.1 ms | 2.10 | 2.11 |
| Q01 | 8 | 3.91 | 4.8 ms | 2.08 | 2.10 |
| Q01 | 32 | 6.07 | 6.1 ms | 2.04 | 2.05 |
| Q02 | 1 | 0.94 | 7.2 ms | 2.04 | 2.04 |
| Q02 | 4 | 2.71 | 8.1 ms | 2.04 | 2.05 |
| Q02 | 8 | 4.37 | 9.1 ms | 2.04 | 2.05 |
| Q02 | 32 | 6.99 | 11.0 ms | 2.05 | 2.05 |
| Q03 | 1 | 0.90 | 5.6 ms | 2.05 | 2.06 |
| Q03 | 4 | 2.79 | 6.8 ms | 2.05 | 2.06 |
| Q03 | 8 | 3.95 | 7.4 ms | 2.05 | 2.06 |
| Q03 | 32 | 6.44 | 8.9 ms | 2.08 | 2.09 |
| Q04 | 1 | 0.99 | 9.7 ms | 2.07 | 2.07 |
| Q04 | 4 | 3.03 | 11.4 ms | 2.06 | 2.08 |
| Q04 | 8 | 4.68 | 12.0 ms | 2.04 | 2.06 |
| Q04 | 32 | 7.32 | 13.4 ms | 2.06 | 2.07 |
| Q05 | 1 | 0.82 | 4.2 ms | 2.07 | 2.08 |
| Q05 | 4 | 2.76 | 5.3 ms | 2.07 | 2.08 |
| Q05 | 8 | 4.00 | 5.9 ms | 2.07 | 2.07 |
| Q05 | 32 | 6.14 | 7.3 ms | 2.06 | 2.08 |
| Q06 | 1 | 0.94 | 5.9 ms | 2.05 | 2.05 |
| Q06 | 4 | 2.53 | 7.1 ms | 2.04 | 2.06 |
| Q06 | 8 | 4.12 | 7.9 ms | 2.03 | 2.03 |
| Q06 | 32 | 6.54 | 9.7 ms | 2.04 | 2.06 |
| Q07 | 1 | 0.86 | 4.9 ms | 2.04 | 2.06 |
| Q07 | 4 | 2.82 | 5.9 ms | 2.05 | 2.05 |
| Q07 | 8 | 3.86 | 6.6 ms | 2.03 | 2.06 |
| Q07 | 32 | 6.58 | 8.1 ms | 2.04 | 2.07 |
| Q10 | 1 | 1.16 | 13.6 ms | 2.06 | 2.07 |
| Q10 | 4 | 3.35 | 15.5 ms | 2.06 | 2.06 |
| Q10 | 8 | 4.66 | 16.6 ms | 2.06 | 2.07 |
| Q10 | 32 | 7.17 | 18.8 ms | 2.07 | 2.09 |
| Q11 | 1 | 1.50 | 85.5 ms | 2.08 | 2.09 |
| Q11 | 4 | 4.53 | 92.9 ms | 2.10 | 2.11 |
| Q11 | 8 | 5.59 | 95.6 ms | 2.15 | 2.17 |
| Q11 | 32 | 7.67 | 105.9 ms | 2.38 | 2.44 |
| Q12 | 1 | 0.81 | 4.1 ms | 2.40 | 2.41 |
| Q12 | 4 | 2.48 | 5.1 ms | 2.36 | 2.37 |
| Q12 | 8 | 3.81 | 5.7 ms | 2.35 | 2.36 |
| Q12 | 32 | 5.73 | 6.9 ms | 2.35 | 2.38 |
| Q13 | 1 | 2.76 | 334.0 ms | 2.37 | 2.38 |
| Q13 | 4 | 7.52 | 393.7 ms | 2.40 | 2.41 |
| Q13 | 8 | 7.97 | 395.9 ms | 2.42 | 2.45 |
| Q13 | 32 | 8.00 | 399.1 ms | 2.54 | 2.57 |
| mix | 1 | 0.92 | 6.2 ms | 2.07 | 2.07 |
| mix | 4 | 2.91 | 7.4 ms | 2.08 | 2.09 |
| mix | 8 | 4.09 | 8.2 ms | 2.08 | 2.09 |
| mix | 32 | 6.49 | 9.6 ms | 2.13 | 2.13 |

## resources, votable

| class | c | egernia-skycell-w8 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.79 | 3.5 ms | 1.99 | 2.00 |
| Q01 | 4 | 2.63 | 4.3 ms | 1.99 | 2.00 |
| Q01 | 8 | 3.97 | 4.9 ms | 1.96 | 1.99 |
| Q01 | 32 | 6.38 | 6.4 ms | 1.96 | 1.98 |
| Q02 | 1 | 0.95 | 7.4 ms | 1.97 | 1.97 |
| Q02 | 4 | 3.02 | 8.8 ms | 1.97 | 1.97 |
| Q02 | 8 | 4.40 | 9.7 ms | 1.97 | 1.98 |
| Q02 | 32 | 7.14 | 11.5 ms | 1.99 | 1.99 |
| Q03 | 1 | 0.91 | 6.0 ms | 1.99 | 2.00 |
| Q03 | 4 | 2.96 | 7.3 ms | 1.99 | 2.00 |
| Q03 | 8 | 4.44 | 8.0 ms | 1.98 | 1.98 |
| Q03 | 32 | 6.77 | 9.5 ms | 1.98 | 1.99 |
| Q04 | 1 | 1.00 | 10.4 ms | 1.97 | 1.98 |
| Q04 | 4 | 3.11 | 12.0 ms | 1.97 | 1.97 |
| Q04 | 8 | 4.75 | 12.7 ms | 1.95 | 1.97 |
| Q04 | 32 | 7.27 | 14.3 ms | 1.95 | 1.97 |
| Q05 | 1 | 0.82 | 4.5 ms | 1.96 | 1.97 |
| Q05 | 4 | 2.45 | 5.4 ms | 1.95 | 1.95 |
| Q05 | 8 | 3.70 | 6.2 ms | 1.95 | 1.95 |
| Q05 | 32 | 6.29 | 7.6 ms | 1.95 | 1.96 |
| Q06 | 1 | 0.97 | 6.7 ms | 1.96 | 1.97 |
| Q06 | 4 | 2.83 | 7.9 ms | 1.96 | 1.97 |
| Q06 | 8 | 4.50 | 8.9 ms | 1.95 | 1.96 |
| Q06 | 32 | 6.67 | 10.4 ms | 1.98 | 1.99 |
| Q07 | 1 | 0.89 | 5.4 ms | 1.98 | 1.99 |
| Q07 | 4 | 2.69 | 6.4 ms | 1.98 | 1.98 |
| Q07 | 8 | 4.03 | 7.1 ms | 1.96 | 1.98 |
| Q07 | 32 | 6.76 | 8.6 ms | 1.97 | 1.97 |
| Q10 | 1 | 1.17 | 16.3 ms | 1.97 | 1.98 |
| Q10 | 4 | 3.40 | 18.3 ms | 1.98 | 1.98 |
| Q10 | 8 | 5.31 | 20.0 ms | 1.99 | 2.00 |
| Q10 | 32 | 7.50 | 22.3 ms | 2.02 | 2.04 |
| Q11 | 1 | 1.41 | 107.3 ms | 2.05 | 2.05 |
| Q11 | 4 | 4.71 | 122.0 ms | 2.06 | 2.07 |
| Q11 | 8 | 6.26 | 127.6 ms | 2.09 | 2.11 |
| Q11 | 32 | 7.81 | 139.5 ms | 2.32 | 2.34 |
| Q12 | 1 | 0.82 | 4.2 ms | 2.23 | 2.27 |
| Q12 | 4 | 2.57 | 5.3 ms | 2.20 | 2.22 |
| Q12 | 8 | 3.96 | 6.0 ms | 2.14 | 2.16 |
| Q12 | 32 | 6.35 | 7.4 ms | 2.07 | 2.08 |
| Q13 | 1 | 2.77 | 336.1 ms | 2.07 | 2.08 |
| Q13 | 4 | 7.54 | 391.8 ms | 2.09 | 2.11 |
| Q13 | 8 | 7.97 | 397.9 ms | 2.11 | 2.13 |
| Q13 | 32 | 7.99 | 399.0 ms | 2.23 | 2.27 |
| mix | 1 | 0.94 | 6.8 ms | 1.78 | 1.80 |
| mix | 4 | 2.65 | 7.9 ms | 1.80 | 1.80 |
| mix | 8 | 4.35 | 8.9 ms | 1.80 | 1.82 |
| mix | 32 | 6.96 | 10.5 ms | 1.95 | 1.99 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | egernia-skycell-w8 | 8 | 148.0 | 0.92 | 160.2 | 6.2 |
| csv | 4 | egernia-skycell-w8 | 8 | 393.8 | 2.91 | 135.5 | 7.4 |
| csv | 8 | egernia-skycell-w8 | 8 | 499.9 | 4.09 | 122.3 | 8.2 |
| csv | 32 | egernia-skycell-w8 | 8 | 672.1 | 6.49 | 103.6 | 9.6 |
| votable | 1 | egernia-skycell-w8 | 8 | 137.6 | 0.94 | 146.4 | 6.8 |
| votable | 4 | egernia-skycell-w8 | 8 | 334.9 | 2.65 | 126.3 | 7.9 |
| votable | 8 | egernia-skycell-w8 | 8 | 490.1 | 4.35 | 112.6 | 8.9 |
| votable | 32 | egernia-skycell-w8 | 8 | 662.8 | 6.96 | 95.3 | 10.5 |

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
    -f benchmarks/tap-compare/final-skycell/pins/egernia-w8.yml \
    -f benchmarks/tap-compare/final-skycell/pins/skycell.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets egernia-skycell-w8 --scenario <scenario>
```

Environment: see `environment.json` (git 0809d7b3, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Phase B (**Table B, equal CPU**) of the pre-registered skycell rerun, egernia with eight uvicorn workers, measured again alone at `0809d7b3`. Its opponents' columns are those of `20261119T203938Z-19e19fcb-tap-compare`.
- **Why it exists.** The published skycell runs found two faults in egernia itself, fixed in PR #230: HTTP 500 on Q13 at 32 clients with more than one worker (PostgreSQL's `/dev/shm` left at 64 MiB), and Q11 slowed by a spool file whose writes the kernel throttled under the container's memory limit (`docs/postgres-performance.md`). The project lead decided to measure **egernia alone** again on the fixed revision and not to measure DaCHS and argus again (amendment 4, `tap-compare-final-skycell-prereg-v5`).
- **What that means for reading it.** This report has one server. A cell's verdict is computed by the unchanged tie rule from egernia's three repetitions here and DaCHS's and argus's three repetitions in the published run named below. **The servers were not interleaved and were measured days apart**, so nothing inside a cell cancels a drift of the host; amendment 4 states this trade and registers a control for it (E3).
- **Gates.** They ran against all three servers before anything was timed: all three `taplint` PASS and three-way agreement on 11/11 classes, on the fixed revision. DaCHS and argus were up and idle on their own cores while egernia was timed.
- **Verdicts against the published DaCHS and argus rungs: egernia 96 of 96 cells** (the published Table B was egernia 89, ties 3, argus 4). 288 rungs, 6,527,245 requests, **no error on any rung**; generator peak 0.545.
- **E1 holds.** Q13 at c=32, where 3.1-7.6% of requests failed in the published run, has no error in six rungs and ties its published throughput (CSV 20.9 → 20.1 rps, VOTable 20.8 → 20.0).
- **E2 holds.** Q11 at c=1 is 17.5 rps in CSV and 13.2 in VOTable, against 18.2 and 13.1 in phase A: eight workers are no longer slower than one. The published values were 4.7 and 2.4.
- **Q11 is higher in all eight cells**, by 1.97-5.49×: at c=32, CSV 27.8 → 72.8 rps and VOTable 14.1 → 56.3 (the published VOTable cell held the contaminated repetition).
- **Q13 and the mix tie their published values in all 16 cells.** On the mix at c=32, CSV: 672.1 rps (687.0 published), ×2.89 of phase A's 232.4, with cores used 1.86 → 6.49 and CPU per request 8.0 → 9.6 ms (+20%).
- **H1, on phase A and B of this rerun, holds in 17 of 24 cells.** Q01, Q03, Q04, Q10 and Q11 gain at c=8 and c=32 in both formats, by 1.7-3.5×. Three cells gain but exceed the registered ±25% on CPU per request (Q01 VOTable c=32 +26%, Q11 c=32 +28% and +30%); Q13's four cells tie, as before.
- **E3 (control): 72 of 72 cells tie** egernia's published values.
- **A disturbance of the host, recorded and not measured again.** The host's `sar` record shows a foreign write burst in the ten minutes ending 15:10Z (77,388 blocks/s against a run median of 246). It covers this run's first twelve rungs, the VOTable mix, which came in 3-14% below the published values (c=4: 318, 365, 321 rps against 388, 380, 406) and tie them by the registered rule. A second burst ending 21:30Z covers the last rungs, which tie. Amendment 5 records both.

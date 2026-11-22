# 20261117T003742Z-d360fb1e-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: egernia on pg_sphere in `benchmarks/tap-compare/final-skycell/pins/egernia-ab-pgsphere.yml` (`cpuset` 8-15; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=1`; `benchmarks/tap-compare/final-skycell/PROTOCOL.md`); egernia on skycell in `benchmarks/tap-compare/final-skycell/pins/egernia-w1.yml` + `skycell.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=1`; `benchmarks/tap-compare/final-skycell/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-ab-pgsphere | 1.1 | PASS (0 errors) | 10000 |
| egernia-ab-skycell | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | egernia-ab-pgsphere rps | egernia-ab-pgsphere p95 (s) | egernia-ab-skycell rps | egernia-ab-skycell p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Q03 | 1 | 156.8 ±0.9 | 0.007 ±0.000 | 160.0 ±4.7 | 0.008 ±0.000 | tie |
| Q03 | 4 | 276.1 ±1.0 | 0.019 ±0.000 | 277.8 ±1.4 | 0.019 ±0.000 | tie |
| Q03 | 8 | 268.0 ±1.0 | 0.040 ±0.000 | 270.0 ±1.2 | 0.040 ±0.000 | tie |
| Q03 | 32 | 238.7 ±1.2 | 0.154 ±0.002 | 241.4 ±0.9 | 0.152 ±0.002 | tie |
| Q05 | 1 | 195.5 ±2.3 | 0.006 ±0.000 | 193.8 ±4.8 | 0.006 ±0.000 | tie |
| Q05 | 4 | 298.5 ±2.9 | 0.017 ±0.000 | 301.3 ±1.9 | 0.017 ±0.000 | tie |
| Q05 | 8 | 290.5 ±2.2 | 0.037 ±0.000 | 291.4 ±1.6 | 0.036 ±0.000 | tie |
| Q05 | 32 | 261.7 ±1.7 | 0.140 ±0.002 | 263.1 ±2.0 | 0.139 ±0.002 | tie |
| Q06 | 1 | 159.0 ±1.3 | 0.008 ±0.000 | 162.0 ±3.8 | 0.007 ±0.000 | tie |
| Q06 | 4 | 247.5 ±0.6 | 0.021 ±0.000 | 248.4 ±3.9 | 0.021 ±0.001 | tie |
| Q06 | 8 | 240.5 ±0.3 | 0.044 ±0.000 | 242.4 ±2.0 | 0.044 ±0.001 | tie |
| Q06 | 32 | 217.2 ±2.1 | 0.169 ±0.002 | 218.1 ±1.2 | 0.169 ±0.001 | tie |
| Q07 | 1 | 180.0 ±1.4 | 0.006 ±0.000 | 180.6 ±2.2 | 0.006 ±0.000 | tie |
| Q07 | 4 | 285.3 ±1.5 | 0.018 ±0.000 | 285.4 ±2.8 | 0.018 ±0.000 | tie |
| Q07 | 8 | 276.5 ±0.8 | 0.038 ±0.000 | 277.9 ±1.2 | 0.038 ±0.000 | tie |
| Q07 | 32 | 247.2 ±0.5 | 0.147 ±0.001 | 249.2 ±2.8 | 0.147 ±0.001 | tie |
| Q12 | 1 | 200.3 ±4.8 | 0.006 ±0.000 | 200.3 ±2.8 | 0.006 ±0.000 | tie |
| Q12 | 4 | 304.1 ±0.5 | 0.017 ±0.000 | 306.8 ±2.6 | 0.017 ±0.000 | tie |
| Q12 | 8 | 295.4 ±3.3 | 0.036 ±0.001 | 296.5 ±2.9 | 0.036 ±0.001 | tie |
| Q12 | 32 | 267.1 ±0.5 | 0.136 ±0.001 | 269.3 ±4.1 | 0.136 ±0.003 | tie |
| Q13 | 1 | 7.3 ±0.2 | 0.179 ±0.010 | 8.3 ±0.2 | 0.164 ±0.005 | egernia-ab-skycell |
| Q13 | 4 | 16.3 ±0.1 | 0.321 ±0.010 | 19.2 ±0.1 | 0.274 ±0.012 | egernia-ab-skycell |
| Q13 | 8 | 16.9 ±0.2 | 0.624 ±0.029 | 20.2 ±0.3 | 0.544 ±0.005 | egernia-ab-skycell |
| Q13 | 32 | 16.8 ±0.3 | 2.112 ±0.064 | 20.1 ±0.2 | 1.806 ±0.052 | egernia-ab-skycell |
| mix | 1 | 131.7 ±3.2 | 0.013 ±0.000 | 152.0 ±1.7 | 0.011 ±0.000 | egernia-ab-skycell |
| mix | 4 | 253.1 ±1.5 | 0.024 ±0.000 | 260.2 ±0.8 | 0.022 ±0.000 | tie |
| mix | 8 | 250.6 ±1.2 | 0.044 ±0.000 | 254.8 ±2.4 | 0.043 ±0.001 | tie |
| mix | 32 | 225.5 ±0.9 | 0.164 ±0.001 | 230.5 ±0.4 | 0.161 ±0.003 | tie |

## votable

| class | c | egernia-ab-pgsphere rps | egernia-ab-pgsphere p95 (s) | egernia-ab-skycell rps | egernia-ab-skycell p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Q03 | 1 | 136.8 ±27.0 | 0.010 ±0.005 | 132.8 ±29.2 | 0.010 ±0.004 | tie |
| Q03 | 4 | 261.7 ±15.0 | 0.020 ±0.002 | 262.1 ±17.0 | 0.020 ±0.002 | tie |
| Q03 | 8 | 253.9 ±10.5 | 0.042 ±0.003 | 253.8 ±11.6 | 0.043 ±0.003 | tie |
| Q03 | 32 | 226.9 ±7.6 | 0.165 ±0.013 | 226.8 ±11.0 | 0.167 ±0.015 | tie |
| Q05 | 1 | 181.7 ±6.1 | 0.007 ±0.001 | 175.9 ±9.7 | 0.007 ±0.001 | tie |
| Q05 | 4 | 286.3 ±8.1 | 0.018 ±0.001 | 284.6 ±10.2 | 0.018 ±0.001 | tie |
| Q05 | 8 | 276.5 ±2.9 | 0.039 ±0.001 | 277.1 ±7.0 | 0.039 ±0.002 | tie |
| Q05 | 32 | 249.0 ±9.4 | 0.152 ±0.011 | 246.6 ±2.9 | 0.157 ±0.006 | tie |
| Q06 | 1 | 146.9 ±0.1 | 0.008 ±0.000 | 148.2 ±1.8 | 0.008 ±0.000 | tie |
| Q06 | 4 | 236.6 ±3.6 | 0.022 ±0.001 | 239.3 ±0.6 | 0.022 ±0.000 | tie |
| Q06 | 8 | 231.9 ±1.1 | 0.046 ±0.001 | 233.1 ±2.5 | 0.046 ±0.001 | tie |
| Q06 | 32 | 209.5 ±2.3 | 0.176 ±0.002 | 212.1 ±0.8 | 0.174 ±0.002 | tie |
| Q07 | 1 | 170.7 ±3.0 | 0.007 ±0.000 | 170.4 ±1.0 | 0.007 ±0.000 | tie |
| Q07 | 4 | 278.9 ±3.4 | 0.018 ±0.000 | 279.3 ±2.2 | 0.018 ±0.000 | tie |
| Q07 | 8 | 269.7 ±1.5 | 0.040 ±0.000 | 271.2 ±2.2 | 0.039 ±0.000 | tie |
| Q07 | 32 | 240.7 ±2.8 | 0.152 ±0.003 | 243.4 ±1.2 | 0.151 ±0.001 | tie |
| Q12 | 1 | 195.0 ±1.4 | 0.006 ±0.000 | 192.3 ±1.3 | 0.006 ±0.000 | tie |
| Q12 | 4 | 299.7 ±2.7 | 0.017 ±0.000 | 301.6 ±5.2 | 0.017 ±0.000 | tie |
| Q12 | 8 | 290.8 ±1.1 | 0.036 ±0.000 | 292.2 ±2.2 | 0.036 ±0.000 | tie |
| Q12 | 32 | 260.8 ±2.7 | 0.140 ±0.002 | 262.2 ±2.1 | 0.141 ±0.003 | tie |
| Q13 | 1 | 7.2 ±0.1 | 0.181 ±0.007 | 8.2 ±0.4 | 0.165 ±0.006 | egernia-ab-skycell |
| Q13 | 4 | 16.3 ±0.0 | 0.324 ±0.006 | 19.1 ±0.2 | 0.274 ±0.010 | egernia-ab-skycell |
| Q13 | 8 | 17.0 ±0.2 | 0.625 ±0.011 | 20.2 ±0.3 | 0.538 ±0.008 | egernia-ab-skycell |
| Q13 | 32 | 16.8 ±0.3 | 2.118 ±0.039 | 20.1 ±0.2 | 1.807 ±0.052 | egernia-ab-skycell |
| mix | 1 | 126.6 ±2.1 | 0.014 ±0.000 | 142.4 ±1.3 | 0.012 ±0.000 | egernia-ab-skycell |
| mix | 4 | 245.5 ±1.3 | 0.025 ±0.000 | 253.6 ±0.8 | 0.023 ±0.000 | tie |
| mix | 8 | 242.7 ±1.6 | 0.046 ±0.000 | 247.7 ±1.5 | 0.044 ±0.001 | tie |
| mix | 32 | 217.4 ±11.8 | 0.172 ±0.015 | 221.4 ±15.2 | 0.169 ±0.019 | tie |

## resources, csv

| class | c | egernia-ab-pgsphere cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-ab-skycell cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q03 | 1 | 0.89 | 5.7 ms | 1.07 | 1.08 | 0.89 | 5.5 ms | 0.91 | 0.91 |
| Q03 | 4 | 1.81 | 6.6 ms | 1.07 | 1.07 | 1.79 | 6.5 ms | 0.91 | 0.92 |
| Q03 | 8 | 1.88 | 7.0 ms | 1.07 | 1.07 | 1.86 | 6.9 ms | 0.91 | 0.91 |
| Q03 | 32 | 1.81 | 7.6 ms | 1.07 | 1.07 | 1.79 | 7.4 ms | 0.91 | 0.91 |
| Q05 | 1 | 0.81 | 4.1 ms | 1.07 | 1.08 | 0.81 | 4.2 ms | 0.91 | 0.91 |
| Q05 | 4 | 1.54 | 5.2 ms | 1.06 | 1.07 | 1.55 | 5.1 ms | 0.90 | 0.91 |
| Q05 | 8 | 1.59 | 5.5 ms | 1.07 | 1.08 | 1.62 | 5.5 ms | 0.91 | 0.91 |
| Q05 | 32 | 1.56 | 6.0 ms | 1.07 | 1.07 | 1.58 | 6.0 ms | 0.91 | 0.91 |
| Q06 | 1 | 0.94 | 5.9 ms | 1.07 | 1.08 | 0.94 | 5.8 ms | 0.91 | 0.92 |
| Q06 | 4 | 1.71 | 6.9 ms | 1.07 | 1.08 | 1.70 | 6.8 ms | 0.91 | 0.92 |
| Q06 | 8 | 1.76 | 7.3 ms | 1.07 | 1.08 | 1.75 | 7.2 ms | 0.91 | 0.91 |
| Q06 | 32 | 1.70 | 7.9 ms | 1.07 | 1.08 | 1.69 | 7.7 ms | 0.91 | 0.92 |
| Q07 | 1 | 0.86 | 4.8 ms | 1.07 | 1.08 | 0.85 | 4.7 ms | 0.91 | 0.91 |
| Q07 | 4 | 1.63 | 5.7 ms | 1.07 | 1.07 | 1.62 | 5.7 ms | 0.91 | 0.91 |
| Q07 | 8 | 1.69 | 6.1 ms | 1.07 | 1.08 | 1.69 | 6.1 ms | 0.91 | 0.92 |
| Q07 | 32 | 1.64 | 6.7 ms | 1.08 | 1.09 | 1.64 | 6.6 ms | 0.91 | 0.92 |
| Q12 | 1 | 0.80 | 4.0 ms | 1.07 | 1.09 | 0.80 | 4.0 ms | 0.91 | 0.92 |
| Q12 | 4 | 1.52 | 5.0 ms | 1.07 | 1.07 | 1.54 | 5.0 ms | 0.92 | 0.93 |
| Q12 | 8 | 1.58 | 5.3 ms | 1.07 | 1.07 | 1.60 | 5.4 ms | 0.92 | 0.93 |
| Q12 | 32 | 1.54 | 5.8 ms | 1.08 | 1.08 | 1.57 | 5.8 ms | 0.92 | 0.93 |
| Q13 | 1 | 2.82 | 388.6 ms | 1.09 | 1.10 | 2.75 | 333.2 ms | 0.93 | 0.94 |
| Q13 | 4 | 7.69 | 470.8 ms | 1.11 | 1.11 | 7.54 | 392.7 ms | 0.95 | 0.96 |
| Q13 | 8 | 7.98 | 471.6 ms | 1.13 | 1.13 | 7.96 | 395.1 ms | 0.97 | 0.99 |
| Q13 | 32 | 7.98 | 479.7 ms | 1.13 | 1.14 | 7.97 | 397.9 ms | 0.97 | 1.00 |
| mix | 1 | 0.93 | 7.1 ms | 1.07 | 1.07 | 0.91 | 6.0 ms | 0.91 | 0.91 |
| mix | 4 | 2.05 | 8.1 ms | 1.07 | 1.07 | 1.86 | 7.1 ms | 0.91 | 0.91 |
| mix | 8 | 2.16 | 8.6 ms | 1.07 | 1.07 | 1.93 | 7.6 ms | 0.91 | 0.92 |
| mix | 32 | 2.06 | 9.2 ms | 1.07 | 1.08 | 1.86 | 8.1 ms | 0.91 | 0.91 |

## resources, votable

| class | c | egernia-ab-pgsphere cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-ab-skycell cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q03 | 1 | 0.87 | 6.4 ms | 1.04 | 1.05 | 0.87 | 6.6 ms | 0.88 | 0.88 |
| Q03 | 4 | 1.85 | 7.1 ms | 1.04 | 1.05 | 1.82 | 7.0 ms | 0.88 | 0.88 |
| Q03 | 8 | 1.92 | 7.6 ms | 1.04 | 1.05 | 1.89 | 7.4 ms | 0.88 | 0.88 |
| Q03 | 32 | 1.84 | 8.1 ms | 1.03 | 1.04 | 1.80 | 8.0 ms | 0.87 | 0.88 |
| Q05 | 1 | 0.81 | 4.4 ms | 1.04 | 1.05 | 0.81 | 4.6 ms | 0.87 | 0.88 |
| Q05 | 4 | 1.55 | 5.4 ms | 1.03 | 1.05 | 1.57 | 5.5 ms | 0.87 | 0.87 |
| Q05 | 8 | 1.61 | 5.8 ms | 1.04 | 1.05 | 1.64 | 5.9 ms | 0.87 | 0.88 |
| Q05 | 32 | 1.57 | 6.3 ms | 1.04 | 1.05 | 1.59 | 6.5 ms | 0.88 | 0.88 |
| Q06 | 1 | 0.97 | 6.6 ms | 1.04 | 1.04 | 0.96 | 6.5 ms | 0.88 | 0.88 |
| Q06 | 4 | 1.82 | 7.7 ms | 1.04 | 1.05 | 1.80 | 7.5 ms | 0.88 | 0.88 |
| Q06 | 8 | 1.86 | 8.0 ms | 1.04 | 1.05 | 1.85 | 7.9 ms | 0.88 | 0.88 |
| Q06 | 32 | 1.79 | 8.6 ms | 1.04 | 1.05 | 1.79 | 8.4 ms | 0.88 | 0.89 |
| Q07 | 1 | 0.87 | 5.1 ms | 1.04 | 1.06 | 0.86 | 5.1 ms | 0.88 | 0.88 |
| Q07 | 4 | 1.68 | 6.0 ms | 1.04 | 1.05 | 1.68 | 6.0 ms | 0.88 | 0.89 |
| Q07 | 8 | 1.74 | 6.4 ms | 1.04 | 1.05 | 1.74 | 6.4 ms | 0.88 | 0.89 |
| Q07 | 32 | 1.68 | 7.0 ms | 1.05 | 1.05 | 1.69 | 6.9 ms | 0.88 | 0.89 |
| Q12 | 1 | 0.81 | 4.1 ms | 1.05 | 1.06 | 0.81 | 4.2 ms | 0.88 | 0.90 |
| Q12 | 4 | 1.53 | 5.1 ms | 1.04 | 1.05 | 1.56 | 5.2 ms | 0.88 | 0.89 |
| Q12 | 8 | 1.60 | 5.5 ms | 1.04 | 1.04 | 1.62 | 5.5 ms | 0.88 | 0.89 |
| Q12 | 32 | 1.56 | 6.0 ms | 1.05 | 1.06 | 1.58 | 6.0 ms | 0.89 | 0.89 |
| Q13 | 1 | 2.82 | 390.5 ms | 1.06 | 1.06 | 2.75 | 336.9 ms | 0.90 | 0.91 |
| Q13 | 4 | 7.70 | 471.8 ms | 1.07 | 1.09 | 7.53 | 393.8 ms | 0.92 | 0.93 |
| Q13 | 8 | 7.98 | 472.7 ms | 1.10 | 1.11 | 7.96 | 395.2 ms | 0.94 | 0.96 |
| Q13 | 32 | 7.98 | 479.6 ms | 1.10 | 1.11 | 7.96 | 398.4 ms | 0.94 | 0.98 |
| mix | 1 | 0.94 | 7.5 ms | 0.99 | 0.99 | 0.93 | 6.5 ms | 0.83 | 0.83 |
| mix | 4 | 2.11 | 8.6 ms | 1.00 | 1.02 | 1.93 | 7.6 ms | 0.83 | 0.84 |
| mix | 8 | 2.22 | 9.1 ms | 1.00 | 1.01 | 2.00 | 8.1 ms | 0.84 | 0.84 |
| mix | 32 | 2.11 | 9.7 ms | 1.04 | 1.06 | 1.91 | 8.6 ms | 0.88 | 0.89 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | egernia-ab-pgsphere | 1 | 131.7 | 0.93 | 141.6 | 7.1 |
| csv | 1 | egernia-ab-skycell | 1 | 152.0 | 0.91 | 166.3 | 6.0 |
| csv | 4 | egernia-ab-pgsphere | 1 | 253.1 | 2.05 | 123.2 | 8.1 |
| csv | 4 | egernia-ab-skycell | 1 | 260.2 | 1.86 | 139.9 | 7.1 |
| csv | 8 | egernia-ab-pgsphere | 1 | 250.6 | 2.16 | 115.9 | 8.6 |
| csv | 8 | egernia-ab-skycell | 1 | 254.8 | 1.93 | 132.1 | 7.6 |
| csv | 32 | egernia-ab-pgsphere | 1 | 225.5 | 2.06 | 109.3 | 9.2 |
| csv | 32 | egernia-ab-skycell | 1 | 230.5 | 1.86 | 123.9 | 8.1 |
| votable | 1 | egernia-ab-pgsphere | 1 | 126.6 | 0.94 | 134.0 | 7.5 |
| votable | 1 | egernia-ab-skycell | 1 | 142.4 | 0.93 | 152.9 | 6.5 |
| votable | 4 | egernia-ab-pgsphere | 1 | 245.5 | 2.11 | 116.2 | 8.6 |
| votable | 4 | egernia-ab-skycell | 1 | 253.6 | 1.93 | 131.1 | 7.6 |
| votable | 8 | egernia-ab-pgsphere | 1 | 242.7 | 2.22 | 109.4 | 9.1 |
| votable | 8 | egernia-ab-skycell | 1 | 247.7 | 2.00 | 124.0 | 8.1 |
| votable | 32 | egernia-ab-pgsphere | 1 | 217.4 | 2.11 | 103.2 | 9.7 |
| votable | 32 | egernia-ab-skycell | 1 | 221.4 | 1.91 | 115.8 | 8.6 |

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
docker compose -p egernia-pgs -f docker-compose.yml \
    -f benchmarks/tap-compare/final-skycell/pins/egernia-ab-pgsphere.yml \
    up -d db tap-api tap-executor
docker compose -f docker-compose.yml \
    -f benchmarks/tap-compare/final-skycell/pins/egernia-w1.yml \
    -f benchmarks/tap-compare/final-skycell/pins/skycell.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets egernia-ab-pgsphere egernia-ab-skycell --scenario <scenario>
```

Environment: see `environment.json` (git d360fb1e, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Experiment 1 of the pre-registered skycell rerun (`benchmarks/tap-compare/final-skycell/PROTOCOL.md`): **the geometry backend A/B**. The same egernia images twice, in phase A's shape (8 cores, 8 GiB as 4 db / 2 api / 2 executor, one API worker): `egernia-ab-skycell` with `TAP_GEOMETRY_BACKEND=skycell` on cores 0-7, `egernia-ab-pgsphere` with pg_sphere on cores 8-15, each over its own seeded volume, interleaved inside every cell. The two stacks differ in the backend variable, the cpuset, the host ports and the advertised base URL, and in nothing else.
- **Provenance.** Pre-registered at tag `tap-compare-final-skycell-prereg-v1`, amended before measurement at `-v2` (amendment 1); measured at `d360fb1e`. skycell is release v0.58, commit `0d998bd928e026da05631e6f0e9b3b6dbab7570d`, SQL extension version 0.50; pg_sphere is 1.5.2. Both are recorded in `pins/`.
- **Gates.** Both `taplint` PASS with 0 errors. **Agreement 11/11 classes** between the two backends, over all eleven portable classes and not only the seven measured: the same row counts and checksums from skycell and from pg_sphere.
- **Verdicts: 46 ties, skycell 10, pg_sphere 0, of 56 cells.** 336 rungs, 7.7 h (2026-11-17 00:41Z to 08:20Z), 4,134,731 requests. No rung above 1% errors, no generator guard tripped (peak 0.30).
- **K2 holds: skycell is no worse on geometry.** Q05, Q06, Q07 and Q12 tie in **32 of 32 cells**; at c=32 skycell is within ±1% of pg_sphere in every one (CSV: Q05 263.1 against 261.7 rps, Q06 218.1 against 217.2, Q07 249.2 against 247.2, Q12 269.3 against 267.1). The mix ties in 6 cells and goes to skycell in the 2 at c=1 (152.0 against 131.7 rps in CSV, 142.4 against 126.6 in VOTable). pg_sphere wins no cell.
- **K1 fails, and it bounds K2.** Q03 ties in 8 of 8 cells. **Q13 goes to skycell in 8 of 8**, by 13% at c=1 rising to 20% at c=32 (20.1 against 16.8 rps). Q13 touches no geometry, so this is the cpuset placement or the host, not the backend: it is the one control that runs on all eight cores, inside PostgreSQL, and cores 0-7 and 8-15 sit differently on the host's topology. The protocol said a non-tie here bounds what K2 may claim. It does: the geometry result is **"no measurable difference"**, and the two mix cells at c=1 (12-15%) are inside what placement alone produced on Q13, so they are not evidence of a skycell gain.
- **What this run licenses.** A claim about skycell against pg_sphere comes from this experiment only. On this corpus and workload the backend changes nothing that the tie rule can see on the cone classes, in either direction.
- **A handful of 500s, on skycell's Q13 at c=32 only**: 5 requests in 2 rungs (0.5% and 0.2%), under the ceiling. They are the first sign of what phase B and the scaling tiers show at scale; see the phase B report (`20261119T203938Z-19e19fcb-tap-compare`).

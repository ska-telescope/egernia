# 20261120T184934Z-61542dc1-tap-compare-scaling

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
| argus-scaling3 | 1.1 | PASS (2 errors) | 134217728 |
| dachs-scaling3 | 1.1 | PASS (0 errors) | 20000 |
| egernia-skycell-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 428.4 ±16.7 | 0.022 ±0.000 | 17.7 ±0.5 | 0.551 ±0.023 | 305.1 ±3.7 | 0.035 ±0.001 | argus-scaling3 |
| Q01 | 32 | 539.6 ±58.1 | 0.068 ±0.002 | 16.2 ±0.2 | 2.102 ±0.041 | 286.4 ±4.9 | 0.129 ±0.004 | argus-scaling3 |
| Q05 | 8 | 14.7 ±0.1 | 0.571 ±0.002 | 8.1 ±0.1 | 1.202 ±0.016 | 293.0 ±3.3 | 0.036 ±0.001 | egernia-skycell-scaling3 |
| Q05 | 32 | 14.9 ±0.1 | 2.252 ±0.047 | 8.2 ±0.1 | 4.218 ±0.113 | 265.6 ±1.9 | 0.138 ±0.001 | egernia-skycell-scaling3 |
| Q11 | 8 | 27.1 ±0.1 | 0.341 ±0.004 | 4.0 ±0.1 | 2.582 ±0.162 | 21.6 ±0.9 | 0.462 ±0.074 | argus-scaling3 |
| Q11 | 32 | 27.7 ±0.3 | 1.233 ±0.005 | 4.2 ±0.1 | 12.547 ±0.163 | 21.7 ±0.6 | 1.993 ±0.410 | argus-scaling3 |
| Q13 | 8 | 16.9 ±0.2 | 0.567 ±0.005 | 10.1 ±0.1 | 1.082 ±0.039 | 21.0 ±0.3 | 0.520 ±0.008 | egernia-skycell-scaling3 |
| Q13 | 32 | 17.2 ±0.1 | 2.022 ±0.039 | 9.6 ±0.2 | 3.648 ±0.033 | 20.8 ±0.1 | 1.735 ±0.007 | egernia-skycell-scaling3 |
| mix | 8 | 23.9 ±1.0 | 0.572 ±0.002 | 9.6 ±0.6 | 1.291 ±0.030 | 256.2 ±1.4 | 0.042 ±0.000 | egernia-skycell-scaling3 |
| mix | 32 | 24.7 ±1.0 | 1.712 ±0.077 | 9.2 ±0.4 | 4.026 ±0.204 | 232.2 ±2.2 | 0.160 ±0.004 | egernia-skycell-scaling3 |

### votable

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 414.9 ±54.7 | 0.022 ±0.000 | 17.5 ±0.2 | 0.557 ±0.010 | 303.5 ±4.0 | 0.035 ±0.000 | argus-scaling3 |
| Q01 | 32 | 548.1 ±17.1 | 0.067 ±0.001 | 15.8 ±0.2 | 2.153 ±0.017 | 283.6 ±3.7 | 0.129 ±0.003 | argus-scaling3 |
| Q05 | 8 | 14.8 ±0.2 | 0.574 ±0.009 | 8.0 ±0.0 | 1.226 ±0.048 | 288.5 ±1.4 | 0.037 ±0.000 | egernia-skycell-scaling3 |
| Q05 | 32 | 14.8 ±0.2 | 2.240 ±0.023 | 8.1 ±0.2 | 4.218 ±0.038 | 259.6 ±1.6 | 0.141 ±0.002 | egernia-skycell-scaling3 |
| Q11 | 8 | 21.2 ±0.1 | 0.437 ±0.006 | 4.6 ±0.1 | 2.226 ±0.152 | 18.4 ±1.0 | 0.560 ±0.197 | argus-scaling3 |
| Q11 | 32 | 21.6 ±0.2 | 1.575 ±0.007 | 4.7 ±0.3 | 10.584 ±1.356 | 19.0 ±0.4 | 2.435 ±0.400 | argus-scaling3 |
| Q13 | 8 | 16.9 ±0.1 | 0.564 ±0.008 | 9.9 ±0.1 | 1.106 ±0.016 | 21.0 ±0.1 | 0.521 ±0.008 | egernia-skycell-scaling3 |
| Q13 | 32 | 17.2 ±0.1 | 2.023 ±0.033 | 9.6 ±0.3 | 3.683 ±0.092 | 20.8 ±0.2 | 1.741 ±0.030 | egernia-skycell-scaling3 |
| mix | 8 | 23.4 ±0.7 | 0.587 ±0.021 | 9.7 ±0.5 | 1.300 ±0.011 | 248.5 ±2.5 | 0.044 ±0.000 | egernia-skycell-scaling3 |
| mix | 32 | 24.5 ±1.0 | 1.706 ±0.056 | 9.2 ±0.1 | 4.042 ±0.085 | 225.4 ±2.5 | 0.165 ±0.003 | egernia-skycell-scaling3 |

### resources, csv

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.04 | 9.4 ms | 2.47 | 2.65 | 1.97 | 112.0 ms | 1.12 | 1.12 | 1.44 | 4.7 ms | 0.97 | 0.97 |
| Q01 | 32 | 5.68 | 10.5 ms | 2.93 | 3.21 | 1.92 | 119.7 ms | 1.12 | 1.13 | 1.42 | 5.0 ms | 0.97 | 0.98 |
| Q05 | 8 | 7.75 | 529.2 ms | 3.21 | 3.22 | 6.23 | 779.4 ms | 1.23 | 1.31 | 1.62 | 5.5 ms | 0.95 | 0.95 |
| Q05 | 32 | 7.95 | 540.6 ms | 3.22 | 3.23 | 6.58 | 834.3 ms | 1.24 | 1.31 | 1.59 | 6.0 ms | 0.95 | 0.97 |
| Q11 | 8 | 5.86 | 217.0 ms | 3.16 | 3.19 | 1.49 | 372.4 ms | 1.21 | 1.25 | 2.18 | 101.0 ms | 0.98 | 0.99 |
| Q11 | 32 | 6.11 | 222.1 ms | 3.11 | 3.13 | 1.61 | 384.3 ms | 1.27 | 1.31 | 2.17 | 99.8 ms | 1.03 | 1.06 |
| Q13 | 8 | 7.71 | 457.6 ms | 3.05 | 3.09 | 5.55 | 556.1 ms | 1.23 | 1.25 | 7.96 | 379.1 ms | 1.01 | 1.04 |
| Q13 | 32 | 7.94 | 463.9 ms | 3.00 | 3.01 | 5.44 | 578.0 ms | 1.23 | 1.25 | 7.96 | 384.7 ms | 1.02 | 1.03 |
| mix | 8 | 7.54 | 317.4 ms | 2.19 | 2.20 | 4.87 | 511.9 ms | 1.19 | 1.25 | 1.92 | 7.5 ms | 0.96 | 0.96 |
| mix | 32 | 7.87 | 319.8 ms | 2.21 | 2.22 | 4.85 | 537.4 ms | 1.19 | 1.29 | 1.85 | 8.0 ms | 0.97 | 0.97 |

### resources, votable

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.92 | 9.5 ms | 1.52 | 1.71 | 2.01 | 115.2 ms | 0.99 | 0.99 | 1.46 | 4.8 ms | 0.88 | 0.88 |
| Q01 | 32 | 5.78 | 10.5 ms | 2.00 | 2.22 | 1.95 | 124.2 ms | 1.00 | 1.01 | 1.44 | 5.1 ms | 0.89 | 0.90 |
| Q05 | 8 | 7.75 | 527.4 ms | 2.23 | 2.23 | 6.20 | 784.4 ms | 1.13 | 1.20 | 1.64 | 5.7 ms | 0.87 | 0.89 |
| Q05 | 32 | 7.94 | 540.5 ms | 2.24 | 2.25 | 6.53 | 839.3 ms | 1.13 | 1.20 | 1.59 | 6.1 ms | 0.87 | 0.88 |
| Q11 | 8 | 6.04 | 285.3 ms | 2.20 | 2.22 | 1.56 | 342.8 ms | 1.15 | 1.20 | 2.41 | 130.8 ms | 0.92 | 0.94 |
| Q11 | 32 | 6.24 | 290.2 ms | 2.24 | 2.26 | 1.64 | 353.0 ms | 1.21 | 1.27 | 2.40 | 126.4 ms | 1.04 | 1.07 |
| Q13 | 8 | 7.71 | 457.5 ms | 2.20 | 2.21 | 5.51 | 560.8 ms | 1.15 | 1.16 | 7.96 | 378.9 ms | 1.00 | 1.02 |
| Q13 | 32 | 7.93 | 464.2 ms | 2.19 | 2.20 | 5.48 | 582.4 ms | 1.14 | 1.15 | 7.96 | 384.9 ms | 1.00 | 1.02 |
| mix | 8 | 7.50 | 321.8 ms | 1.20 | 1.25 | 4.90 | 513.4 ms | 1.04 | 1.11 | 1.99 | 8.0 ms | 0.84 | 0.85 |
| mix | 32 | 7.85 | 322.2 ms | 1.28 | 1.30 | 4.85 | 533.6 ms | 1.06 | 1.14 | 1.92 | 8.5 ms | 0.88 | 0.89 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | argus-scaling3 | — | 23.9 | 7.54 | 3.2 | 317.4 |
| csv | 8 | dachs-scaling3 | — | 9.6 | 4.87 | 2.0 | 511.9 |
| csv | 8 | egernia-skycell-scaling3 | 1 | 256.2 | 1.92 | 133.2 | 7.5 |
| csv | 32 | argus-scaling3 | — | 24.7 | 7.87 | 3.1 | 319.8 |
| csv | 32 | dachs-scaling3 | — | 9.2 | 4.85 | 1.9 | 537.4 |
| csv | 32 | egernia-skycell-scaling3 | 1 | 232.2 | 1.85 | 125.3 | 8.0 |
| votable | 8 | argus-scaling3 | — | 23.4 | 7.50 | 3.1 | 321.8 |
| votable | 8 | dachs-scaling3 | — | 9.7 | 4.90 | 2.0 | 513.4 |
| votable | 8 | egernia-skycell-scaling3 | 1 | 248.5 | 1.99 | 125.0 | 8.0 |
| votable | 32 | argus-scaling3 | — | 24.5 | 7.85 | 3.1 | 322.2 |
| votable | 32 | dachs-scaling3 | — | 9.2 | 4.85 | 1.9 | 533.6 |
| votable | 32 | egernia-skycell-scaling3 | 1 | 225.4 | 1.92 | 117.6 | 8.5 |

## Tier 16

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-scaling3 | 1.1 | PASS (2 errors) | 134217728 |
| dachs-scaling3 | 1.1 | PASS (0 errors) | 20000 |
| egernia-skycell-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 465.6 ±157.0 | 0.025 ±0.026 | 18.5 ±0.2 | 0.530 ±0.028 | 590.8 ±6.3 | 0.020 ±0.005 | tie |
| Q01 | 32 | 775.1 ±12.1 | 0.047 ±0.000 | 16.7 ±0.1 | 2.059 ±0.029 | 536.9 ±2.7 | 0.076 ±0.006 | argus-scaling3 |
| Q05 | 8 | 18.1 ±1.3 | 0.526 ±0.039 | 9.6 ±1.1 | 1.074 ±0.219 | 540.8 ±51.6 | 0.023 ±0.011 | egernia-skycell-scaling3 |
| Q05 | 32 | 18.6 ±0.8 | 1.936 ±0.063 | 10.6 ±0.5 | 3.251 ±0.081 | 506.6 ±3.6 | 0.085 ±0.022 | egernia-skycell-scaling3 |
| Q11 | 8 | 27.6 ±0.9 | 0.325 ±0.022 | 4.1 ±0.2 | 2.549 ±0.697 | 39.0 ±0.6 | 0.301 ±0.018 | egernia-skycell-scaling3 |
| Q11 | 32 | 27.8 ±1.8 | 1.244 ±0.150 | 4.3 ±0.0 | 11.002 ±2.846 | 40.0 ±2.4 | 1.170 ±0.592 | egernia-skycell-scaling3 |
| Q13 | 8 | 20.2 ±0.8 | 0.522 ±0.021 | 12.5 ±0.4 | 0.900 ±0.044 | 37.9 ±0.1 | 0.273 ±0.002 | egernia-skycell-scaling3 |
| Q13 | 32 | 21.3 ±1.7 | 1.670 ±0.122 | 11.4 ±1.2 | 3.172 ±0.240 | 39.9 ±0.3 | 1.249 ±0.132 | egernia-skycell-scaling3 |
| mix | 8 | 29.0 ±2.2 | 0.519 ±0.026 | 7.2 ±1.1 | 2.325 ±1.459 | 466.0 ±41.3 | 0.027 ±0.010 | egernia-skycell-scaling3 |
| mix | 32 | 29.3 ±1.0 | 1.473 ±0.085 | 10.9 ±0.3 | 3.411 ±0.016 | 446.4 ±1.0 | 0.098 ±0.019 | egernia-skycell-scaling3 |

### votable

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 501.1 ±12.1 | 0.019 ±0.001 | 18.0 ±1.3 | 0.553 ±0.076 | 581.5 ±9.8 | 0.019 ±0.005 | egernia-skycell-scaling3 |
| Q01 | 32 | 700.4 ±255.6 | 0.072 ±0.103 | 16.3 ±0.4 | 2.095 ±0.041 | 534.7 ±3.2 | 0.079 ±0.011 | tie |
| Q05 | 8 | 17.7 ±0.0 | 0.524 ±0.028 | 9.7 ±0.1 | 1.061 ±0.073 | 543.8 ±11.6 | 0.020 ±0.006 | egernia-skycell-scaling3 |
| Q05 | 32 | 17.6 ±1.6 | 2.005 ±0.146 | 10.5 ±0.6 | 3.294 ±0.178 | 496.8 ±3.9 | 0.081 ±0.003 | egernia-skycell-scaling3 |
| Q11 | 8 | 21.8 ±0.1 | 0.416 ±0.005 | 4.6 ±0.2 | 2.202 ±0.019 | 32.0 ±2.6 | 0.366 ±0.070 | egernia-skycell-scaling3 |
| Q11 | 32 | 22.0 ±0.8 | 1.549 ±0.098 | 4.8 ±0.2 | 10.728 ±0.845 | 35.3 ±0.9 | 1.262 ±0.269 | egernia-skycell-scaling3 |
| Q13 | 8 | 20.2 ±3.8 | 0.528 ±0.063 | 12.1 ±0.5 | 0.945 ±0.078 | 37.9 ±0.2 | 0.273 ±0.003 | egernia-skycell-scaling3 |
| Q13 | 32 | 21.0 ±1.7 | 1.689 ±0.142 | 7.9 ±2.3 | 5.796 ±3.180 | 39.9 ±0.2 (1% err) | 1.054 ±0.067 | argus-scaling3 |
| mix | 8 | 27.0 ±1.3 | 0.533 ±0.004 | 11.6 ±0.3 | 1.106 ±0.035 | 467.0 ±12.9 | 0.026 ±0.005 | egernia-skycell-scaling3 |
| mix | 32 | 29.2 ±1.3 | 1.487 ±0.084 | 11.0 ±0.2 | 3.377 ±0.092 | 432.8 ±3.6 | 0.095 ±0.007 | egernia-skycell-scaling3 |

### resources, csv

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.15 | 8.9 ms | 2.93 | 3.03 | 2.08 | 113.0 ms | 0.91 | 0.92 | 2.71 | 4.6 ms | 1.17 | 1.17 |
| Q01 | 32 | 7.78 | 10.0 ms | 3.45 | 3.73 | 2.02 | 122.3 ms | 0.92 | 0.92 | 2.81 | 5.2 ms | 1.16 | 1.17 |
| Q05 | 8 | 7.92 | 439.7 ms | 3.78 | 3.79 | 6.68 | 700.6 ms | 1.04 | 1.12 | 2.93 | 5.4 ms | 1.14 | 1.15 |
| Q05 | 32 | 8.14 | 442.5 ms | 3.80 | 3.81 | 7.71 | 733.5 ms | 1.06 | 1.15 | 3.14 | 6.2 ms | 1.13 | 1.13 |
| Q11 | 8 | 7.48 | 271.7 ms | 3.82 | 3.83 | 1.51 | 369.0 ms | 0.98 | 1.02 | 4.01 | 102.8 ms | 1.15 | 1.16 |
| Q11 | 32 | 7.73 | 280.0 ms | 3.86 | 3.88 | 1.63 | 378.2 ms | 1.05 | 1.08 | 4.16 | 103.8 ms | 1.23 | 1.25 |
| Q13 | 8 | 7.91 | 393.3 ms | 3.84 | 3.88 | 6.40 | 515.8 ms | 1.00 | 1.02 | 15.15 | 400.5 ms | 1.23 | 1.26 |
| Q13 | 32 | 8.15 | 384.1 ms | 3.81 | 3.85 | 6.19 | 549.1 ms | 0.98 | 1.00 | 15.94 | 401.0 ms | 1.27 | 1.30 |
| mix | 8 | 7.88 | 273.2 ms | 2.78 | 2.82 | 3.44 | 481.4 ms | 0.97 | 1.06 | 3.48 | 7.5 ms | 1.16 | 1.18 |
| mix | 32 | 8.18 | 280.0 ms | 2.79 | 2.81 | 5.36 | 494.0 ms | 0.98 | 1.09 | 3.70 | 8.3 ms | 1.17 | 1.17 |

### resources, votable

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.52 | 9.0 ms | 1.47 | 1.75 | 2.10 | 116.8 ms | 0.77 | 0.77 | 2.74 | 4.7 ms | 0.66 | 0.66 |
| Q01 | 32 | 7.10 | 10.1 ms | 2.33 | 2.78 | 2.05 | 126.6 ms | 0.78 | 0.78 | 2.83 | 5.3 ms | 0.66 | 0.66 |
| Q05 | 8 | 7.91 | 448.4 ms | 2.80 | 2.81 | 6.73 | 701.7 ms | 0.91 | 0.99 | 3.06 | 5.6 ms | 0.66 | 0.66 |
| Q05 | 32 | 8.11 | 464.9 ms | 2.82 | 2.83 | 7.60 | 738.9 ms | 0.94 | 1.02 | 3.17 | 6.4 ms | 0.66 | 0.67 |
| Q11 | 8 | 7.56 | 347.2 ms | 2.84 | 2.86 | 1.55 | 340.6 ms | 0.95 | 0.99 | 4.20 | 131.8 ms | 0.72 | 0.73 |
| Q11 | 32 | 7.72 | 352.6 ms | 2.88 | 2.89 | 1.65 | 346.3 ms | 1.01 | 1.06 | 4.64 | 132.2 ms | 0.85 | 0.88 |
| Q13 | 8 | 7.77 | 388.2 ms | 2.86 | 2.86 | 6.31 | 524.7 ms | 0.94 | 0.96 | 15.14 | 400.2 ms | 1.20 | 1.22 |
| Q13 | 32 | 8.14 | 388.6 ms | 2.81 | 2.87 | 4.35 | 559.1 ms | 0.93 | 0.94 | 15.96 | 400.8 ms | 1.25 | 1.28 |
| mix | 8 | 7.93 | 295.7 ms | 1.11 | 1.19 | 5.46 | 474.2 ms | 0.82 | 0.89 | 3.71 | 8.0 ms | 0.59 | 0.59 |
| mix | 32 | 8.19 | 282.3 ms | 1.21 | 1.23 | 5.41 | 498.7 ms | 0.85 | 0.95 | 3.83 | 8.8 ms | 0.66 | 0.66 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | argus-scaling3 | — | 29.0 | 7.88 | 3.7 | 273.2 |
| csv | 8 | dachs-scaling3 | — | 7.2 | 3.44 | 2.1 | 481.4 |
| csv | 8 | egernia-skycell-scaling3 | 2 | 466.0 | 3.48 | 133.8 | 7.5 |
| csv | 32 | argus-scaling3 | — | 29.3 | 8.18 | 3.6 | 280.0 |
| csv | 32 | dachs-scaling3 | — | 10.9 | 5.36 | 2.0 | 494.0 |
| csv | 32 | egernia-skycell-scaling3 | 2 | 446.4 | 3.70 | 120.6 | 8.3 |
| votable | 8 | argus-scaling3 | — | 27.0 | 7.93 | 3.4 | 295.7 |
| votable | 8 | dachs-scaling3 | — | 11.6 | 5.46 | 2.1 | 474.2 |
| votable | 8 | egernia-skycell-scaling3 | 2 | 467.0 | 3.71 | 125.7 | 8.0 |
| votable | 32 | argus-scaling3 | — | 29.2 | 8.19 | 3.6 | 282.3 |
| votable | 32 | dachs-scaling3 | — | 11.0 | 5.41 | 2.0 | 498.7 |
| votable | 32 | egernia-skycell-scaling3 | 2 | 432.8 | 3.83 | 113.1 | 8.8 |

## Tier 24

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-scaling3 | 1.1 | PASS (2 errors) | 134217728 |
| dachs-scaling3 | 1.1 | PASS (0 errors) | 20000 |
| egernia-skycell-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 534.5 ±8.1 | 0.018 ±0.000 | 18.2 ±2.8 | 0.543 ±0.098 | 856.5 ±333.7 | 0.018 ±0.013 | tie |
| Q01 | 32 | 812.2 ±66.9 | 0.045 ±0.003 | 16.9 ±0.3 | 2.030 ±0.007 | 1036.1 ±1.2 | 0.049 ±0.012 | egernia-skycell-scaling3 |
| Q05 | 8 | 17.8 ±1.4 | 0.549 ±0.057 | 10.4 ±0.2 | 1.012 ±0.068 | 843.4 ±85.2 | 0.016 ±0.006 | egernia-skycell-scaling3 |
| Q05 | 32 | 18.5 ±1.5 | 1.938 ±0.171 | 11.7 ±0.3 | 3.010 ±0.118 | 956.9 ±0.8 | 0.056 ±0.017 | egernia-skycell-scaling3 |
| Q11 | 8 | 29.4 ±0.2 | 0.311 ±0.002 | 4.0 ±0.4 | 2.630 ±0.520 | 40.4 ±2.5 | 0.630 ±0.174 | egernia-skycell-scaling3 |
| Q11 | 32 | 30.4 ±0.1 | 1.130 ±0.008 | 4.3 ±0.0 | 11.061 ±2.042 | 22.2 ±15.7 | 4.706 ±1.342 | tie |
| Q13 | 8 | 21.8 ±0.6 | 0.445 ±0.084 | 13.3 ±0.4 | 0.866 ±0.045 | 51.5 ±0.3 | 0.192 ±0.001 | egernia-skycell-scaling3 |
| Q13 | 32 | 22.9 ±1.9 | 1.548 ±0.178 | 12.8 ±0.1 | 2.774 ±0.033 | 60.4 ±0.2 (6% err) | 0.873 ±0.080 | argus-scaling3 |
| mix | 8 | 26.9 ±2.2 | 0.538 ±0.005 | 12.0 ±0.3 | 1.078 ±0.036 | 654.2 ±30.9 | 0.019 ±0.004 | egernia-skycell-scaling3 |
| mix | 32 | 29.0 ±1.2 | 1.492 ±0.052 | 11.1 ±1.9 | 3.414 ±0.688 | 823.2 ±14.5 | 0.058 ±0.010 | egernia-skycell-scaling3 |

### votable

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-skycell-scaling3 rps | egernia-skycell-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 523.5 ±21.8 | 0.018 ±0.000 | 18.2 ±2.5 | 0.545 ±0.114 | 865.5 ±322.8 | 0.014 ±0.006 | tie |
| Q01 | 32 | 825.0 ±16.5 | 0.045 ±0.001 | 15.9 ±2.7 | 2.187 ±0.475 | 1027.4 ±13.6 | 0.047 ±0.008 | egernia-skycell-scaling3 |
| Q05 | 8 | 18.3 ±1.0 | 0.543 ±0.033 | 10.1 ±0.1 | 1.023 ±0.016 | 788.2 ±233.5 | 0.016 ±0.012 | egernia-skycell-scaling3 |
| Q05 | 32 | 18.5 ±1.9 | 1.880 ±0.322 | 11.4 ±0.3 | 3.037 ±0.078 | 937.1 ±7.1 | 0.057 ±0.017 | egernia-skycell-scaling3 |
| Q11 | 8 | 23.0 ±0.1 | 0.407 ±0.002 | 4.6 ±0.0 | 2.296 ±0.097 | 31.6 ±5.8 | 0.732 ±0.225 | egernia-skycell-scaling3 |
| Q11 | 32 | 23.2 ±0.3 | 1.479 ±0.020 | 4.6 ±0.4 | 11.084 ±1.818 | 23.8 ±5.6 | 4.606 ±1.709 | tie |
| Q13 | 8 | 21.2 ±0.2 | 0.484 ±0.030 | 13.1 ±0.3 | 0.880 ±0.058 | 51.7 ±0.2 | 0.192 ±0.000 | egernia-skycell-scaling3 |
| Q13 | 32 | 21.8 ±2.1 | 1.637 ±0.165 | 12.7 ±0.3 | 2.805 ±0.057 | 60.8 ±0.4 (6% err) | 0.868 ±0.122 | argus-scaling3 |
| mix | 8 | 27.1 ±1.8 | 0.538 ±0.013 | 12.1 ±0.4 | 1.067 ±0.049 | 680.3 ±85.4 | 0.019 ±0.004 | egernia-skycell-scaling3 |
| mix | 32 | 27.6 ±1.0 | 1.551 ±0.012 | 11.6 ±0.3 | 3.211 ±0.013 | 805.5 ±1.4 | 0.069 ±0.008 | egernia-skycell-scaling3 |

### resources, csv

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.64 | 8.7 ms | 2.74 | 2.88 | 2.05 | 113.2 ms | 0.93 | 0.93 | 3.60 | 4.2 ms | 1.56 | 1.56 |
| Q01 | 32 | 8.01 | 9.9 ms | 3.34 | 3.70 | 2.03 | 121.2 ms | 0.93 | 0.93 | 5.52 | 5.3 ms | 1.54 | 1.57 |
| Q05 | 8 | 7.82 | 440.0 ms | 3.70 | 3.71 | 6.86 | 666.0 ms | 1.06 | 1.12 | 4.31 | 5.1 ms | 1.51 | 1.52 |
| Q05 | 32 | 8.13 | 444.4 ms | 3.72 | 3.73 | 8.00 | 696.0 ms | 1.07 | 1.13 | 6.08 | 6.4 ms | 1.48 | 1.49 |
| Q11 | 8 | 7.89 | 269.0 ms | 3.74 | 3.76 | 1.46 | 366.8 ms | 1.03 | 1.05 | 4.06 | 101.0 ms | 1.51 | 1.52 |
| Q11 | 32 | 8.20 | 271.0 ms | 3.78 | 3.80 | 1.60 | 369.5 ms | 1.09 | 1.13 | 2.29 | 104.7 ms | 1.60 | 1.61 |
| Q13 | 8 | 7.87 | 362.6 ms | 3.77 | 3.80 | 6.55 | 496.5 ms | 1.04 | 1.06 | 20.19 | 393.0 ms | 1.61 | 1.63 |
| Q13 | 32 | 8.16 | 358.5 ms | 3.75 | 3.78 | 6.61 | 522.9 ms | 1.03 | 1.05 | 23.91 | 396.4 ms | 1.70 | 1.75 |
| mix | 8 | 7.88 | 294.1 ms | 2.52 | 2.54 | 5.45 | 456.3 ms | 1.01 | 1.10 | 4.72 | 7.2 ms | 1.55 | 1.55 |
| mix | 32 | 8.19 | 283.8 ms | 2.56 | 2.58 | 5.34 | 485.6 ms | 1.00 | 1.11 | 7.09 | 8.6 ms | 1.56 | 1.57 |

### resources, votable

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.61 | 8.8 ms | 1.37 | 1.51 | 2.10 | 115.8 ms | 0.81 | 0.81 | 3.71 | 4.3 ms | 1.00 | 1.01 |
| Q01 | 32 | 8.21 | 10.0 ms | 1.94 | 2.38 | 2.02 | 128.7 ms | 0.81 | 0.82 | 5.56 | 5.4 ms | 1.01 | 1.01 |
| Q05 | 8 | 7.93 | 435.2 ms | 2.38 | 2.39 | 6.78 | 673.1 ms | 0.95 | 1.02 | 4.18 | 5.3 ms | 1.01 | 1.02 |
| Q05 | 32 | 8.12 | 444.8 ms | 2.40 | 2.41 | 7.92 | 704.0 ms | 0.97 | 1.04 | 6.16 | 6.6 ms | 1.01 | 1.01 |
| Q11 | 8 | 7.81 | 340.9 ms | 2.42 | 2.44 | 1.54 | 336.9 ms | 0.96 | 1.00 | 3.93 | 124.5 ms | 1.07 | 1.08 |
| Q11 | 32 | 7.96 | 346.5 ms | 2.47 | 2.48 | 1.59 | 348.9 ms | 1.03 | 1.09 | 3.16 | 132.8 ms | 1.20 | 1.22 |
| Q13 | 8 | 7.91 | 374.6 ms | 2.49 | 2.49 | 6.47 | 500.2 ms | 0.96 | 0.97 | 20.14 | 390.0 ms | 1.57 | 1.59 |
| Q13 | 32 | 8.15 | 377.2 ms | 2.51 | 2.52 | 6.61 | 525.4 ms | 0.95 | 0.96 | 23.90 | 393.4 ms | 1.67 | 1.72 |
| mix | 8 | 7.72 | 286.4 ms | 1.13 | 1.16 | 5.52 | 457.4 ms | 0.86 | 0.92 | 5.20 | 7.7 ms | 0.87 | 0.89 |
| mix | 32 | 8.18 | 298.3 ms | 1.19 | 1.20 | 5.53 | 480.2 ms | 0.88 | 0.98 | 7.32 | 9.1 ms | 0.99 | 1.01 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | argus-scaling3 | — | 26.9 | 7.88 | 3.4 | 294.1 |
| csv | 8 | dachs-scaling3 | — | 12.0 | 5.45 | 2.2 | 456.3 |
| csv | 8 | egernia-skycell-scaling3 | 4 | 654.2 | 4.72 | 138.5 | 7.2 |
| csv | 32 | argus-scaling3 | — | 29.0 | 8.19 | 3.5 | 283.8 |
| csv | 32 | dachs-scaling3 | — | 11.1 | 5.34 | 2.1 | 485.6 |
| csv | 32 | egernia-skycell-scaling3 | 4 | 823.2 | 7.09 | 116.1 | 8.6 |
| votable | 8 | argus-scaling3 | — | 27.1 | 7.72 | 3.5 | 286.4 |
| votable | 8 | dachs-scaling3 | — | 12.1 | 5.52 | 2.2 | 457.4 |
| votable | 8 | egernia-skycell-scaling3 | 4 | 680.3 | 5.20 | 130.7 | 7.7 |
| votable | 32 | argus-scaling3 | — | 27.6 | 8.18 | 3.4 | 298.3 |
| votable | 32 | dachs-scaling3 | — | 11.6 | 5.53 | 2.1 | 480.2 |
| votable | 32 | egernia-skycell-scaling3 | 4 | 805.5 | 7.32 | 110.1 | 9.1 |

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

Environment: see `environment.json` (git 61542dc1, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Experiment 3 of the pre-registered skycell rerun (`benchmarks/tap-compare/final-skycell/PROTOCOL.md`): **the three-server resource-scaling comparison** (`scaling-three-way/PROTOCOL.md`) measured again with egernia on the skycell geometry backend. Tiers of 8, 16 and 24 CPUs and GiB; five classes and the mix, both formats, at 8 and 32 clients. It replaces `20260912T225808Z-d43b538d-tap-compare-scaling`.
- **Provenance.** Pre-registered at `tap-compare-final-skycell-prereg-v1`, amended to `-v4`; measured at `61542dc1`. DaCHS serves as the `gavo` user throughout (amendment 3). An earlier attempt (`20261119T122908Z-d360fb1e-tap-compare-scaling`, on disk, unpublished) never measured a rung: `taplint`'s async stage waited forever behind job rows left EXECUTING by the DaCHS failure described in the phase B report. Amendment 2 empties DaCHS's job table at every bring-up.
- **Gates.** Per tier, all three `taplint` PASS and the agreement gate holds on 11/11 classes.
- **Conditions.** 540 rungs, 12.8 h (2026-11-20 18:54Z to 11-21 07:40Z), 5,273,108 requests. **No generator guard tripped** (peak 0.589; the published run voided thirteen rungs, all argus's). Tier 8 interleaved; at tiers 16 and 24 each server measured alone, in the order egernia, DaCHS, argus at 16 and argus, DaCHS, egernia at 24.
- **The mixed workload at c=32, CSV, across the tiers:**

  | server | tier 8 | tier 16 | tier 24 | factor | cores used | CPU per request |
  | --- | --- | --- | --- | --- | --- | --- |
  | egernia | 232.2 rps | 446.4 | 823.2 | ×3.55 | 1.85 → 3.70 → 7.09 | 8.0 → 8.3 → 8.6 ms |
  | DaCHS | 9.2 | 10.9 | 11.1 | ×1.21 | 4.85 → 5.36 → 5.34 | 537 → 494 → 486 ms |
  | argus | 24.7 | 29.3 | 29.0 | ×1.17 | 7.87 → 8.18 → 8.19 | 320 → 280 → 284 ms |

  The published run had egernia at 167.3 → 323.8 → 609.3 rps, DaCHS at 9.4 → 11.0 → 11.8 and argus at 24.6 → 29.4 → 31.2.
- **S2 holds**: egernia's mix at c=32 rises at each tier with non-overlapping intervals in both formats, and is above the published value at every tier. All 20 of its cells are higher at tier 16 than at tier 8; 13 are higher again at tier 24, 6 tie and 1 is lower (the ties and the loss are Q11's four cells, Q01 at c=8 and Q05 in VOTable at c=8).
- **Cross-server verdicts per tier** (of 20 cells): tier 8 egernia 12, argus 8 (Q01 and Q11); tier 16 egernia 16, argus 2, ties 2; tier 24 egernia 14, argus 2, ties 4.
- **S5 holds**: egernia's CPU per request on the mix is 8.0, 8.3 and 8.6 ms across a threefold increase in cores.
- **S4 holds**: tier 8 ties with this protocol's phase A (`20261117T203446Z-d360fb1e-tap-compare`) in **20 of 20 cells for each of the three servers**. Two of those ties are wide: Q05 in VOTable at c=8 measured DaCHS at 5.6 rps and argus at 11.4 in phase A against 8.0 and 14.8 here, a noisy cell in phase A.
- **S3: the database half holds, the metadata half does not.** argus gains from tier 8 to 16 in 13 of 20 cells and **ties from 16 to 24 in 20 of 20**, never using more than 8.21 cores at any tier: it stops at its pool of eight connections. Q01 was predicted to keep climbing and does not; it ties from 16 to 24 in all four cells (775.1 → 812.2 rps at c=32, CSV).
- **S1 fails from 8 to 16 and holds from 16 to 24**, as in the published run. DaCHS is higher at tier 16 in 10 of 20 cells (the mix by 18%) and lower in one (the mix in CSV at c=8, a noisy 7.2 rps between 9.6 and 12.0); from 16 to 24 it ties in 17 and is higher in 3. Its database's buffer cache doubles between tiers 8 and 16 under the ¼ rule.
- **egernia's Q13 returns errors at c=32, as in phase B.** Seven rungs are over the 1% ceiling: one at tier 16 (1.2%; the other five there are at 0.7-1.0%) and all six at tier 24 (4.5-5.7%). HTTP 500s from PostgreSQL's dynamic shared memory running out in the database container's 64 MiB `/dev/shm`, described in the phase B report (`20261119T203938Z-19e19fcb-tap-compare`). The fraction grows with the tier because the tiers add workers, and with them concurrent parallel queries: one worker at tier 8 (no errors), two at 16, four at 24. egernia cannot win a cell that holds such a rung: Q13 at c=32 goes to argus in VOTable at tier 16 and in both formats at tier 24.
- **Not measured again.** The supplementary tier-24 block under twelve generator processes, and the read-replica experiment (`20260910T084557Z-716fe2a1-tap-compare-scaling`), are not part of this protocol. Both stand as published, on pg_sphere at their own commits.

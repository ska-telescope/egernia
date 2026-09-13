# 20260912T225808Z-d43b538d-tap-compare-scaling

Same-hardware TAP-server resource-scaling comparison: the parity
protocol's corpus, gates, query stream, formats and statistics, with
every server's resource pins raised tier by tier. Where the host
cannot hold every pinned stack of a tier at once, the servers are
measured one at a time under that tier's pins, so repetitions do not
interleave across them; the gates run per tier with the stacks up.
The pins actually applied, as `docker inspect` and `SHOW` saw them, are
under `pins/`. See `benchmarks/tap-compare/scaling-three-way/PROTOCOL.md` for
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
| egernia-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-scaling3 rps | egernia-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 412.0 ±37.9 | 0.022 ±0.000 | 18.0 ±0.2 | 0.535 ±0.014 | 208.5 ±1.4 | 0.050 ±0.001 | argus-scaling3 |
| Q01 | 32 | 545.9 ±30.9 | 0.065 ±0.001 | 16.3 ±0.5 | 2.102 ±0.063 | 192.2 ±2.7 | 0.190 ±0.003 | argus-scaling3 |
| Q05 | 8 | 14.7 ±0.1 | 0.579 ±0.016 | 8.1 ±0.4 | 1.213 ±0.048 | 199.6 ±3.2 | 0.052 ±0.001 | egernia-scaling3 |
| Q05 | 32 | 14.8 ±0.2 | 2.261 ±0.058 | 8.2 ±0.1 | 4.162 ±0.060 | 183.2 ±0.7 | 0.198 ±0.002 | egernia-scaling3 |
| Q11 | 8 | 27.3 ±0.0 | 0.335 ±0.005 | 4.1 ±0.1 | 2.585 ±0.033 | 21.4 ±0.5 | 0.468 ±0.013 | argus-scaling3 |
| Q11 | 32 | 28.0 ±0.2 | 1.221 ±0.012 | 4.3 ±0.2 | 12.131 ±0.827 | 22.1 ±0.2 | 1.752 ±0.112 | argus-scaling3 |
| Q13 | 8 | 17.2 ±0.2 | 0.555 ±0.004 | 10.3 ±0.0 | 1.072 ±0.010 | 17.6 ±0.9 | 0.606 ±0.024 | tie |
| Q13 | 32 | 17.6 ±0.0 | 1.987 ±0.030 | 9.7 ±0.1 | 3.601 ±0.077 | 17.9 ±0.1 | 1.979 ±0.034 | tie |
| mix | 8 | 23.9 ±0.9 | 0.574 ±0.002 | 9.8 ±0.2 | 1.270 ±0.013 | 183.0 ±1.8 | 0.058 ±0.000 | egernia-scaling3 |
| mix | 32 | 24.6 ±1.4 | 1.699 ±0.101 | 9.4 ±0.2 | 3.953 ±0.107 | 167.3 ±1.4 | 0.221 ±0.003 | egernia-scaling3 |

### votable

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-scaling3 rps | egernia-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 410.6 ±37.8 | 0.022 ±0.000 | 17.8 ±0.5 | 0.551 ±0.012 | 208.4 ±1.5 | 0.050 ±0.000 | argus-scaling3 |
| Q01 | 32 | 547.1 ±31.3 | 0.066 ±0.003 | 16.1 ±0.5 | 2.140 ±0.107 | 193.3 ±0.7 | 0.188 ±0.001 | argus-scaling3 |
| Q05 | 8 | 14.5 ±0.6 | 0.575 ±0.017 | 8.0 ±0.1 | 1.235 ±0.045 | 200.2 ±1.3 | 0.051 ±0.001 | egernia-scaling3 |
| Q05 | 32 | 14.6 ±0.2 | 2.256 ±0.032 | 8.2 ±0.2 | 4.190 ±0.105 | 182.4 ±1.3 | 0.199 ±0.002 | egernia-scaling3 |
| Q11 | 8 | 21.5 ±0.1 | 0.429 ±0.004 | 4.5 ±0.2 | 2.165 ±0.095 | 18.4 ±0.9 | 0.555 ±0.030 | argus-scaling3 |
| Q11 | 32 | 21.9 ±0.2 | 1.563 ±0.005 | 4.7 ±0.0 | 10.819 ±0.684 | 19.3 ±0.0 | 2.049 ±0.155 | argus-scaling3 |
| Q13 | 8 | 17.2 ±0.2 | 0.556 ±0.004 | 10.1 ±0.3 | 1.098 ±0.039 | 17.3 ±0.2 | 0.619 ±0.013 | tie |
| Q13 | 32 | 17.6 ±0.2 | 1.989 ±0.027 | 9.7 ±0.2 | 3.644 ±0.088 | 17.7 ±0.9 | 2.016 ±0.118 | tie |
| mix | 8 | 23.5 ±1.0 | 0.583 ±0.007 | 9.9 ±0.5 | 1.271 ±0.011 | 178.0 ±0.0 | 0.061 ±0.001 | egernia-scaling3 |
| mix | 32 | 24.5 ±1.4 | 1.722 ±0.094 | 9.4 ±0.2 | 3.945 ±0.114 | 162.8 ±0.6 | 0.231 ±0.001 | egernia-scaling3 |

### resources, csv

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.70 | 9.0 ms | 2.39 | 2.58 | 1.96 | 109.0 ms | 0.96 | 0.97 | 1.47 | 7.0 ms | 1.05 | 1.06 |
| Q01 | 32 | 5.51 | 10.1 ms | 2.86 | 3.14 | 1.91 | 117.8 ms | 0.97 | 0.97 | 1.43 | 7.5 ms | 1.04 | 1.05 |
| Q05 | 8 | 7.76 | 532.0 ms | 3.15 | 3.15 | 6.24 | 782.3 ms | 1.09 | 1.17 | 1.58 | 7.9 ms | 1.00 | 1.01 |
| Q05 | 32 | 7.95 | 542.6 ms | 3.15 | 3.16 | 6.59 | 826.5 ms | 1.09 | 1.19 | 1.54 | 8.4 ms | 1.00 | 1.01 |
| Q11 | 8 | 5.88 | 215.8 ms | 3.09 | 3.10 | 1.49 | 365.3 ms | 1.02 | 1.05 | 2.22 | 103.7 ms | 1.03 | 1.04 |
| Q11 | 32 | 6.13 | 219.9 ms | 3.06 | 3.08 | 1.60 | 378.3 ms | 1.05 | 1.10 | 2.27 | 102.4 ms | 1.08 | 1.10 |
| Q13 | 8 | 7.71 | 449.7 ms | 2.99 | 3.02 | 5.58 | 547.3 ms | 1.02 | 1.04 | 7.97 | 454.8 ms | 1.06 | 1.07 |
| Q13 | 32 | 7.94 | 455.0 ms | 2.95 | 2.96 | 5.49 | 574.2 ms | 1.02 | 1.03 | 7.97 | 447.0 ms | 1.05 | 1.07 |
| mix | 8 | 7.56 | 317.7 ms | 2.10 | 2.12 | 4.94 | 510.3 ms | 1.03 | 1.09 | 1.80 | 9.8 ms | 1.04 | 1.06 |
| mix | 32 | 7.88 | 321.9 ms | 2.13 | 2.14 | 4.92 | 531.8 ms | 1.03 | 1.10 | 1.74 | 10.4 ms | 1.05 | 1.05 |

### resources, votable

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.75 | 9.1 ms | 1.46 | 1.64 | 1.99 | 112.5 ms | 0.80 | 0.81 | 1.47 | 7.1 ms | 0.94 | 0.95 |
| Q01 | 32 | 5.49 | 10.0 ms | 1.94 | 2.17 | 1.94 | 122.3 ms | 0.81 | 0.81 | 1.44 | 7.5 ms | 0.94 | 0.95 |
| Q05 | 8 | 7.67 | 533.8 ms | 2.19 | 2.19 | 6.19 | 780.1 ms | 0.93 | 1.02 | 1.59 | 8.0 ms | 0.93 | 0.94 |
| Q05 | 32 | 7.95 | 547.3 ms | 2.20 | 2.21 | 6.59 | 832.9 ms | 0.95 | 1.02 | 1.55 | 8.5 ms | 0.91 | 0.92 |
| Q11 | 8 | 6.05 | 282.0 ms | 2.15 | 2.16 | 1.52 | 339.0 ms | 0.96 | 1.01 | 2.44 | 133.3 ms | 0.96 | 0.97 |
| Q11 | 32 | 6.27 | 288.3 ms | 2.18 | 2.22 | 1.66 | 350.6 ms | 1.03 | 1.09 | 2.49 | 129.6 ms | 1.07 | 1.10 |
| Q13 | 8 | 7.71 | 449.8 ms | 2.15 | 2.17 | 5.50 | 549.2 ms | 0.99 | 1.01 | 7.97 | 461.2 ms | 1.04 | 1.05 |
| Q13 | 32 | 7.93 | 456.2 ms | 2.12 | 2.13 | 5.50 | 575.8 ms | 0.99 | 1.00 | 7.97 | 452.9 ms | 1.03 | 1.04 |
| mix | 8 | 7.52 | 321.3 ms | 1.15 | 1.18 | 4.97 | 508.4 ms | 0.85 | 0.92 | 1.84 | 10.4 ms | 0.91 | 0.92 |
| mix | 32 | 7.84 | 321.7 ms | 1.22 | 1.24 | 4.96 | 536.7 ms | 0.88 | 0.95 | 1.79 | 11.0 ms | 0.94 | 0.94 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | argus-scaling3 | — | 23.9 | 7.56 | 3.2 | 317.7 |
| csv | 8 | dachs-scaling3 | — | 9.8 | 4.94 | 2.0 | 510.3 |
| csv | 8 | egernia-scaling3 | 1 | 183.0 | 1.80 | 101.8 | 9.8 |
| csv | 32 | argus-scaling3 | — | 24.6 | 7.88 | 3.1 | 321.9 |
| csv | 32 | dachs-scaling3 | — | 9.4 | 4.92 | 1.9 | 531.8 |
| csv | 32 | egernia-scaling3 | 1 | 167.3 | 1.74 | 96.0 | 10.4 |
| votable | 8 | argus-scaling3 | — | 23.5 | 7.52 | 3.1 | 321.3 |
| votable | 8 | dachs-scaling3 | — | 9.9 | 4.97 | 2.0 | 508.4 |
| votable | 8 | egernia-scaling3 | 1 | 178.0 | 1.84 | 96.7 | 10.4 |
| votable | 32 | argus-scaling3 | — | 24.5 | 7.84 | 3.1 | 321.7 |
| votable | 32 | dachs-scaling3 | — | 9.4 | 4.96 | 1.9 | 536.7 |
| votable | 32 | egernia-scaling3 | 1 | 162.8 | 1.79 | 91.0 | 11.0 |

## Tier 16

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-scaling3 | 1.1 | PASS (2 errors) | 134217728 |
| dachs-scaling3 | 1.1 | PASS (0 errors) | 20000 |
| egernia-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-scaling3 rps | egernia-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 528.3 ±10.9 | 0.018 ±0.000 | 18.8 ±0.3 | 0.516 ±0.011 | 418.6 ±2.3 | 0.030 ±0.001 | argus-scaling3 |
| Q01 | 32 | 816.9 ±20.0 | 0.045 ±0.001 | 16.8 ±0.1 | 2.045 ±0.007 | 378.3 ±2.5 | 0.106 ±0.001 | argus-scaling3 |
| Q05 | 8 | 17.5 ±0.7 | 0.546 ±0.026 | 10.0 ±0.2 | 1.032 ±0.053 | 393.8 ±15.2 | 0.033 ±0.009 | egernia-scaling3 |
| Q05 | 32 | 17.4 ±1.6 | 2.033 ±0.089 | 11.0 ±0.6 | 3.184 ±0.182 | 356.9 ±3.6 | 0.112 ±0.002 | egernia-scaling3 |
| Q11 | 8 | 37.5 ±0.1 | 0.237 ±0.001 | 4.1 ±0.1 | 2.569 ±0.138 | 37.4 ±3.8 | 0.326 ±0.031 | invalid |
| Q11 | 32 | 39.1 ±0.3 | 0.872 ±0.011 | 4.3 ±0.0 | 12.070 ±1.434 | 41.5 ±0.5 | 1.018 ±0.060 | tie |
| Q13 | 8 | 20.7 ±0.6 | 0.501 ±0.038 | 12.6 ±0.2 | 0.899 ±0.027 | 33.5 ±0.1 | 0.312 ±0.008 | egernia-scaling3 |
| Q13 | 32 | 21.1 ±0.2 | 1.689 ±0.042 | 12.2 ±0.3 | 2.924 ±0.034 | 34.0 ±0.1 | 1.310 ±0.234 | egernia-scaling3 |
| mix | 8 | 28.5 ±1.4 | 0.534 ±0.007 | 11.7 ±0.2 | 1.097 ±0.024 | 354.7 ±5.5 | 0.034 ±0.007 | egernia-scaling3 |
| mix | 32 | 29.4 ±1.0 | 1.466 ±0.073 | 11.0 ±0.2 | 3.374 ±0.061 | 323.8 ±2.5 | 0.126 ±0.002 | egernia-scaling3 |

### votable

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-scaling3 rps | egernia-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 515.5 ±27.3 | 0.018 ±0.000 | 18.4 ±0.8 | 0.533 ±0.015 | 417.2 ±8.3 | 0.028 ±0.008 | argus-scaling3 |
| Q01 | 32 | 810.1 ±9.7 | 0.046 ±0.000 | 16.5 ±0.4 | 2.072 ±0.020 | 375.0 ±4.5 | 0.111 ±0.014 | argus-scaling3 |
| Q05 | 8 | 18.4 ±0.0 | 0.531 ±0.036 | 9.8 ±0.0 | 1.030 ±0.045 | 388.8 ±12.6 | 0.032 ±0.015 | egernia-scaling3 |
| Q05 | 32 | 18.8 ±0.2 | 1.938 ±0.051 | 10.7 ±0.4 | 3.267 ±0.096 | 352.3 ±1.7 | 0.116 ±0.020 | egernia-scaling3 |
| Q11 | 8 | 29.7 ±0.1 | 0.304 ±0.003 | 4.5 ±0.3 | 2.258 ±0.581 | 32.5 ±1.1 | 0.400 ±0.026 | invalid |
| Q11 | 32 | 30.6 ±0.3 | 1.109 ±0.011 | 4.7 ±0.1 | 10.375 ±1.580 | 36.1 ±0.7 | 1.196 ±0.084 | egernia-scaling3 |
| Q13 | 8 | 21.2 ±2.0 | 0.500 ±0.042 | 12.5 ±0.1 | 0.900 ±0.020 | 33.3 ±0.1 | 0.315 ±0.003 | egernia-scaling3 |
| Q13 | 32 | 21.3 ±0.5 | 1.683 ±0.014 | 12.1 ±0.2 | 2.923 ±0.040 | 33.8 ±0.2 | 1.301 ±0.197 | egernia-scaling3 |
| mix | 8 | 28.1 ±1.1 | 0.535 ±0.016 | 11.8 ±0.1 | 1.107 ±0.018 | 346.3 ±0.6 | 0.035 ±0.006 | egernia-scaling3 |
| mix | 32 | 30.6 ±0.7 | 1.414 ±0.037 | 11.2 ±0.2 | 3.329 ±0.077 | 316.0 ±1.5 | 0.130 ±0.001 | egernia-scaling3 |

### resources, csv

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.44 | 8.4 ms | 3.13 | 3.24 | 2.07 | 110.7 ms | 0.91 | 0.92 | 2.79 | 6.7 ms | 1.28 | 1.28 |
| Q01 | 32 | 7.68 | 9.4 ms | 3.67 | 4.04 | 2.02 | 120.6 ms | 0.92 | 0.92 | 2.87 | 7.6 ms | 1.27 | 1.29 |
| Q05 | 8 | 7.93 | 453.3 ms | 4.05 | 4.05 | 6.79 | 685.8 ms | 1.05 | 1.12 | 2.94 | 7.5 ms | 1.23 | 1.25 |
| Q05 | 32 | 8.11 | 469.6 ms | 4.06 | 4.07 | 7.85 | 724.5 ms | 1.07 | 1.17 | 3.08 | 8.6 ms | 1.20 | 1.21 |
| Q11 | 8 | 7.49 | 200.5 ms | 4.09 | 4.11 | 1.52 | 367.4 ms | 0.99 | 1.01 | 3.79 | 101.5 ms | 1.23 | 1.24 |
| Q11 | 32 | 7.90 | 202.8 ms | 4.12 | 4.13 | 1.64 | 377.7 ms | 1.04 | 1.07 | 4.32 | 104.1 ms | 1.31 | 1.32 |
| Q13 | 8 | 7.91 | 382.5 ms | 4.10 | 4.13 | 6.35 | 508.2 ms | 0.99 | 1.01 | 15.46 | 462.9 ms | 1.28 | 1.29 |
| Q13 | 32 | 8.13 | 387.9 ms | 4.06 | 4.08 | 6.41 | 533.1 ms | 0.98 | 0.99 | 15.98 | 471.6 ms | 1.33 | 1.34 |
| mix | 8 | 7.88 | 277.6 ms | 2.99 | 3.01 | 5.43 | 467.1 ms | 0.99 | 1.08 | 3.39 | 9.6 ms | 1.28 | 1.28 |
| mix | 32 | 8.19 | 280.9 ms | 2.99 | 3.02 | 5.40 | 496.3 ms | 0.99 | 1.07 | 3.46 | 10.7 ms | 1.28 | 1.29 |

### resources, votable

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.39 | 8.5 ms | 1.49 | 1.80 | 2.11 | 115.5 ms | 0.77 | 0.77 | 2.82 | 6.8 ms | 1.18 | 1.18 |
| Q01 | 32 | 7.70 | 9.5 ms | 2.44 | 2.92 | 2.05 | 125.2 ms | 0.77 | 0.78 | 2.89 | 7.7 ms | 1.18 | 1.18 |
| Q05 | 8 | 7.91 | 432.5 ms | 2.93 | 2.93 | 6.75 | 691.8 ms | 0.91 | 0.97 | 2.97 | 7.7 ms | 1.19 | 1.20 |
| Q05 | 32 | 8.13 | 433.8 ms | 2.95 | 2.95 | 7.62 | 729.5 ms | 0.93 | 1.02 | 3.11 | 8.8 ms | 1.19 | 1.20 |
| Q11 | 8 | 7.50 | 253.0 ms | 2.99 | 3.05 | 1.52 | 341.7 ms | 0.92 | 0.94 | 4.22 | 129.8 ms | 1.23 | 1.24 |
| Q11 | 32 | 7.82 | 256.3 ms | 3.07 | 3.09 | 1.66 | 352.1 ms | 0.99 | 1.05 | 4.73 | 131.4 ms | 1.37 | 1.39 |
| Q13 | 8 | 7.89 | 373.5 ms | 3.06 | 3.08 | 6.32 | 510.4 ms | 0.94 | 0.95 | 15.47 | 465.2 ms | 1.32 | 1.33 |
| Q13 | 32 | 8.13 | 383.8 ms | 3.03 | 3.04 | 6.40 | 532.0 ms | 0.93 | 0.94 | 15.98 | 475.2 ms | 1.37 | 1.38 |
| mix | 8 | 7.96 | 285.3 ms | 1.12 | 1.19 | 5.48 | 468.8 ms | 0.83 | 0.90 | 3.50 | 10.1 ms | 1.09 | 1.09 |
| mix | 32 | 8.21 | 270.4 ms | 1.20 | 1.22 | 5.46 | 493.6 ms | 0.83 | 0.92 | 3.55 | 11.2 ms | 1.18 | 1.19 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | argus-scaling3 | — | 28.5 | 7.88 | 3.6 | 277.6 |
| csv | 8 | dachs-scaling3 | — | 11.7 | 5.43 | 2.2 | 467.1 |
| csv | 8 | egernia-scaling3 | 2 | 354.7 | 3.39 | 104.6 | 9.6 |
| csv | 32 | argus-scaling3 | — | 29.4 | 8.19 | 3.6 | 280.9 |
| csv | 32 | dachs-scaling3 | — | 11.0 | 5.40 | 2.0 | 496.3 |
| csv | 32 | egernia-scaling3 | 2 | 323.8 | 3.46 | 93.6 | 10.7 |
| votable | 8 | argus-scaling3 | — | 28.1 | 7.96 | 3.5 | 285.3 |
| votable | 8 | dachs-scaling3 | — | 11.8 | 5.48 | 2.1 | 468.8 |
| votable | 8 | egernia-scaling3 | 2 | 346.3 | 3.50 | 99.0 | 10.1 |
| votable | 32 | argus-scaling3 | — | 30.6 | 8.21 | 3.7 | 270.4 |
| votable | 32 | dachs-scaling3 | — | 11.2 | 5.46 | 2.0 | 493.6 |
| votable | 32 | egernia-scaling3 | 2 | 316.0 | 3.55 | 89.1 | 11.2 |

## Tier 24

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-scaling3 | 1.1 | PASS (2 errors) | 134217728 |
| dachs-scaling3 | 1.1 | PASS (0 errors) | 20000 |
| egernia-scaling3 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

### csv

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-scaling3 rps | egernia-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 547.2 ±3.7 | 0.017 ±0.000 | 18.9 ±0.4 | 0.516 ±0.007 | 675.0 ±203.1 | 0.018 ±0.007 | tie |
| Q01 | 32 | 909.3 ±258.7 | 0.042 ±0.003 | 17.1 ±0.3 | 2.014 ±0.011 | 725.5 ±2.9 | 0.067 ±0.013 | invalid |
| Q05 | 8 | 18.7 ±1.3 | 0.511 ±0.186 | 10.4 ±0.3 | 0.987 ±0.045 | 573.6 ±177.1 | 0.026 ±0.016 | egernia-scaling3 |
| Q05 | 32 | 18.7 ±0.3 | 1.918 ±0.080 | 12.1 ±0.4 | 2.925 ±0.128 | 682.6 ±11.3 | 0.082 ±0.044 | egernia-scaling3 |
| Q11 | 8 | 40.4 ±0.1 | 0.224 ±0.002 | 4.2 ±0.1 | 2.473 ±0.182 | 54.7 ±13.0 | 0.248 ±0.083 | invalid |
| Q11 | 32 | 42.3 ±0.2 | 0.810 ±0.009 | 4.3 ±0.1 | 12.154 ±0.731 | 63.9 ±3.5 | 0.985 ±0.167 | egernia-scaling3 |
| Q13 | 8 | 20.8 ±0.5 | 0.502 ±0.038 | 13.5 ±0.5 | 0.850 ±0.034 | 46.5 ±0.5 | 0.209 ±0.001 | egernia-scaling3 |
| Q13 | 32 | 21.1 ±0.2 | 1.685 ±0.018 | 13.0 ±0.3 | 2.728 ±0.054 | 51.5 ±0.2 | 0.903 ±0.311 | egernia-scaling3 |
| mix | 8 | 30.6 ±3.9 | 0.463 ±0.160 | 12.2 ±0.3 | 1.084 ±0.012 | 520.5 ±197.5 | 0.027 ±0.019 | egernia-scaling3 |
| mix | 32 | 31.2 ±1.9 | 1.378 ±0.135 | 11.8 ±0.1 | 3.179 ±0.013 | 609.3 ±3.9 | 0.079 ±0.008 | egernia-scaling3 |

### votable

| class | c | argus-scaling3 rps | argus-scaling3 p95 (s) | dachs-scaling3 rps | dachs-scaling3 p95 (s) | egernia-scaling3 rps | egernia-scaling3 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 542.6 ±5.5 | 0.017 ±0.000 | 18.8 ±0.4 | 0.520 ±0.017 | 760.1 ±89.9 | 0.015 ±0.006 | egernia-scaling3 |
| Q01 | 32 | 855.2 ±4.5 | 0.043 ±0.001 | 16.7 ±0.2 | 2.061 ±0.025 | 718.4 ±4.4 | 0.073 ±0.025 | argus-scaling3 |
| Q05 | 8 | 18.4 ±0.5 | 0.543 ±0.047 | 10.4 ±0.4 | 0.990 ±0.040 | 612.5 ±185.3 | 0.022 ±0.009 | egernia-scaling3 |
| Q05 | 32 | 18.2 ±0.8 | 1.960 ±0.065 | 11.5 ±0.3 | 3.049 ±0.079 | 666.6 ±1.7 | 0.071 ±0.016 | egernia-scaling3 |
| Q11 | 8 | 32.1 ±0.0 | 0.290 ±0.001 | 4.6 ±0.1 | 2.207 ±0.052 | 46.2 ±5.5 | 0.287 ±0.022 | invalid |
| Q11 | 32 | 33.1 ±0.1 | 1.036 ±0.010 | 4.7 ±0.3 | 10.505 ±1.863 | 52.5 ±11.1 | 1.333 ±0.481 | egernia-scaling3 |
| Q13 | 8 | 20.8 ±1.7 | 0.492 ±0.103 | 13.1 ±0.3 | 0.877 ±0.043 | 46.6 ±0.1 | 0.208 ±0.001 | egernia-scaling3 |
| Q13 | 32 | 22.1 ±0.6 | 1.605 ±0.047 | 12.9 ±0.1 | 2.739 ±0.007 | 51.3 ±0.2 | 0.960 ±0.068 | egernia-scaling3 |
| mix | 8 | 29.6 ±0.8 | 0.521 ±0.014 | 12.2 ±0.0 | 1.052 ±0.019 | 516.7 ±166.8 | 0.028 ±0.016 | egernia-scaling3 |
| mix | 32 | 29.9 ±2.3 | 1.449 ±0.084 | 11.7 ±0.1 | 3.174 ±0.065 | 588.6 ±3.6 | 0.088 ±0.016 | egernia-scaling3 |

### resources, csv

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.58 | 8.4 ms | 2.81 | 2.95 | 2.09 | 110.7 ms | 0.92 | 0.93 | 4.10 | 6.1 ms | 1.72 | 1.73 |
| Q01 | 32 | 7.37 | 9.3 ms | 3.44 | 3.81 | 2.03 | 120.0 ms | 0.93 | 0.93 | 5.64 | 7.8 ms | 1.69 | 1.72 |
| Q05 | 8 | 7.92 | 424.6 ms | 3.80 | 3.81 | 6.91 | 665.6 ms | 1.05 | 1.13 | 3.94 | 6.9 ms | 1.62 | 1.64 |
| Q05 | 32 | 8.13 | 437.8 ms | 3.83 | 3.84 | 8.21 | 694.3 ms | 1.09 | 1.15 | 5.99 | 8.8 ms | 1.57 | 1.58 |
| Q11 | 8 | 7.97 | 197.8 ms | 3.86 | 3.88 | 1.50 | 360.4 ms | 1.00 | 1.03 | 5.49 | 100.5 ms | 1.58 | 1.59 |
| Q11 | 32 | 8.45 | 200.3 ms | 3.91 | 3.93 | 1.62 | 374.1 ms | 1.10 | 1.13 | 6.92 | 108.6 ms | 1.67 | 1.69 |
| Q13 | 8 | 7.91 | 381.1 ms | 3.90 | 3.93 | 6.51 | 483.8 ms | 1.05 | 1.07 | 20.78 | 447.3 ms | 1.69 | 1.71 |
| Q13 | 32 | 8.14 | 388.4 ms | 3.88 | 3.91 | 6.61 | 513.6 ms | 1.04 | 1.06 | 23.97 | 466.5 ms | 1.79 | 1.82 |
| mix | 8 | 7.88 | 259.0 ms | 2.59 | 2.61 | 5.46 | 450.9 ms | 1.00 | 1.12 | 4.69 | 9.0 ms | 1.70 | 1.72 |
| mix | 32 | 8.19 | 264.3 ms | 2.64 | 2.65 | 5.53 | 475.5 ms | 0.99 | 1.08 | 6.67 | 11.0 ms | 1.72 | 1.72 |

### resources, votable

| class | c | argus-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-scaling3 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.60 | 8.5 ms | 1.39 | 1.54 | 2.14 | 114.1 ms | 0.81 | 0.81 | 4.57 | 6.0 ms | 1.08 | 1.09 |
| Q01 | 32 | 8.08 | 9.5 ms | 2.00 | 2.43 | 2.07 | 125.3 ms | 0.81 | 0.82 | 5.65 | 7.9 ms | 1.08 | 1.08 |
| Q05 | 8 | 7.92 | 432.9 ms | 2.43 | 2.43 | 6.93 | 671.2 ms | 0.96 | 1.02 | 4.34 | 7.1 ms | 1.08 | 1.09 |
| Q05 | 32 | 8.12 | 447.7 ms | 2.44 | 2.45 | 7.88 | 698.7 ms | 0.98 | 1.08 | 6.05 | 9.1 ms | 1.08 | 1.09 |
| Q11 | 8 | 7.93 | 248.0 ms | 2.47 | 2.50 | 1.55 | 338.9 ms | 0.97 | 1.01 | 5.96 | 129.1 ms | 1.17 | 1.18 |
| Q11 | 32 | 8.27 | 250.4 ms | 2.53 | 2.55 | 1.64 | 346.1 ms | 1.02 | 1.08 | 7.22 | 137.8 ms | 1.31 | 1.34 |
| Q13 | 8 | 7.91 | 382.3 ms | 2.55 | 2.56 | 6.39 | 489.4 ms | 0.95 | 0.98 | 20.80 | 447.0 ms | 1.74 | 1.75 |
| Q13 | 32 | 8.14 | 369.9 ms | 2.58 | 2.59 | 6.61 | 514.2 ms | 0.94 | 0.96 | 23.97 | 467.6 ms | 1.83 | 1.86 |
| mix | 8 | 7.94 | 269.4 ms | 1.14 | 1.21 | 5.49 | 453.8 ms | 0.87 | 0.96 | 4.90 | 9.5 ms | 0.91 | 0.93 |
| mix | 32 | 8.20 | 276.1 ms | 1.20 | 1.23 | 5.55 | 477.4 ms | 0.88 | 1.00 | 6.83 | 11.6 ms | 1.06 | 1.09 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | argus-scaling3 | — | 30.6 | 7.88 | 3.9 | 259.0 |
| csv | 8 | dachs-scaling3 | — | 12.2 | 5.46 | 2.2 | 450.9 |
| csv | 8 | egernia-scaling3 | 4 | 520.5 | 4.69 | 110.9 | 9.0 |
| csv | 32 | argus-scaling3 | — | 31.2 | 8.19 | 3.8 | 264.3 |
| csv | 32 | dachs-scaling3 | — | 11.8 | 5.53 | 2.1 | 475.5 |
| csv | 32 | egernia-scaling3 | 4 | 609.3 | 6.67 | 91.3 | 11.0 |
| votable | 8 | argus-scaling3 | — | 29.6 | 7.94 | 3.7 | 269.4 |
| votable | 8 | dachs-scaling3 | — | 12.2 | 5.49 | 2.2 | 453.8 |
| votable | 8 | egernia-scaling3 | 4 | 516.7 | 4.90 | 105.5 | 9.5 |
| votable | 32 | argus-scaling3 | — | 29.9 | 8.20 | 3.6 | 276.1 |
| votable | 32 | dachs-scaling3 | — | 11.7 | 5.55 | 2.1 | 477.4 |
| votable | 32 | egernia-scaling3 | 4 | 588.6 | 6.83 | 86.2 | 11.6 |

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

Environment: see `environment.json` (git d43b538d, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** The pre-registered three-server resource-scaling comparison (`benchmarks/tap-compare/scaling-three-way/PROTOCOL.md`, tag `tap-compare-scaling-threeway-prereg-v1`): the parity workload at **8 / 16 / 24 CPUs and GiB** against **egernia, GAVO DaCHS and CADC argus**, each sized at each tier by its own documented rule. It is the data behind the paper's vertical-scaling **figure**, and it replaces the two-server `scaling/` run, which has no argus and predates PR #160. 540 rungs, 12.8 h (2026-09-12 22:57Z → 09-13 11:47Z), 4,407,102 requests, **zero rungs above 1% errors**.
- **Provenance.** Pre-registered at `3fe01e7`; measured at `d43b538d`. `git diff` between them, restricted to `scaling-three-way/scenarios.yaml`, `scaling-three-way/targets.yaml`, `scaling-three-way/pins/` and the frozen `config/`, is **empty**: the grid, the ladder, the tiers and every pin are the tagged ones. The two commits between only tighten the driver (argus's job store truncated immediately before each measured block rather than only at start-up, and the smoke scenario mapped to this protocol in the publisher).
- **Cores.** Tier 8 ran all three servers at once on disjoint cpusets (egernia 0-7, argus 8-15, DaCHS 16-23) interleaved A,B,C. Tiers 16 and 24 cannot hold three pinned stacks, so each server was measured alone with the other two **stopped**, order alternated (tier 16: egernia, DaCHS, argus; tier 24: argus, DaCHS, egernia). The generator kept cores 24-29 and six processes throughout.

### The figure: the mixed workload at c=32, CSV

| server | tier 8 | tier 16 | tier 24 | 8 → 24 |
| --- | --- | --- | --- | --- |
| **egernia** | 167.3 rps · 1.74 cores · 10.4 ms/req | 323.8 rps · 3.46 cores · 10.7 ms/req | **609.3 rps** · 6.67 cores · 11.0 ms/req | **×3.64** |
| **DaCHS** | 9.4 rps · 4.92 cores · 531.8 ms/req | 11.0 rps · 5.40 cores · 496.3 ms/req | 11.8 rps · 5.53 cores · 475.5 ms/req | ×1.26 |
| **argus** | 24.6 rps · 7.88 cores · 321.9 ms/req | 29.4 rps · 8.19 cores · 280.9 ms/req | 31.2 rps · 8.19 cores · 264.3 ms/req | ×1.27 |

Three servers given the same extra hardware: one turns it into throughput, two do not — and the cores-used column says why. egernia's cores rise with the tier (1.74 → 6.67) at a CPU cost per request that barely moves; **argus is pinned at 8.19 cores whether it is given 16 or 24**, and DaCHS never exceeds 5.5.

### Hypotheses

- **S2 holds — egernia scales.** Every one of the 20 class/format/concurrency cells is higher at tier 16 than tier 8; 18 of 20 are higher again at tier 24 (two ties). The mixed workload at c=32 goes ×1.94 then ×1.88.
- **S5 holds — and it is why S2 is a mechanism rather than a coincidence.** egernia's CPU per request on the mix is **10.4 → 10.7 → 11.0 ms** at c=32 across a threefold increase in cores (and 9.8 → 9.6 → 9.0 ms at c=8). Capacity tracked the cores the workers could reach; it was not bought with extra CPU per request.
- **S3 holds, and it is the most interesting thing here.** argus gains from tier 8 to tier 16 (18 of 20 cells higher, 2 voided) and then **stops**: from tier 16 to tier 24, **17 of 20 cells tie** and 3 are voided — not one is higher. Its cores-used figure shows the mechanism directly: 7.88 → 8.19 → **8.19**. argus has 1,024 Tomcat request threads but **8 pooled database connections at every tier**, and sync queries execute on the request thread drawing from that pool, so past about eight cores of work there is nothing for the extra hardware to do. The half of S3 about the metadata class is *suggestive but not established*: Q01 at c=32 rose 545.9 → 816.9 → 909.3 rps, but its tier-24 cell is **voided** by the generator guard (below), so the protocol does not let it be claimed.
- **S1 half-holds, and the failure is reported as such.** DaCHS is not flat from tier 8 to tier 16: 12 of 20 cells are higher (8 tie), the mix gaining 17%. From tier 16 to tier 24 it is **flat in all 20 of 20 cells**. One `dachs serve` process cannot use more cores — but its bundled PostgreSQL can use more memory, and the ¼ rule gives it 2 → 4 GB of `shared_buffers` between those tiers, which is the likeliest source of the single step. The protocol predicted ties at every tier and got them only above 16; that is a failed prediction, not a rounding error.
- **S4 holds completely.** Tier 8 of this run reproduces phase A of the final three-way comparison — same pins, same corpus, same code, same windows, same concurrencies, measured a day apart under a different protocol — in **20 of 20 cells for every one of the three servers**, largest single gap 5.8% (argus Q01 CSV c=8). Host drift between the two runs is therefore below the tie rule's resolution, which is what licenses reading the tier axis as hardware rather than time.

### The generator guard, and what it cost

Thirteen of 540 rungs were voided, **all of them argus**, and they are the only cells in the run without a verdict:

| voided cell | peak (limit 0.60) |
| --- | --- |
| tier 16, Q11, c=8, both formats, all 3 reps | 0.61 – 0.66 |
| tier 24, Q11, c=8, both formats, all 3 reps | 0.635 – 0.69 |
| tier 24, Q01, c=32, CSV, one rep | 0.88 |

The cause is **client-side cost, and it is measured rather than guessed**. Fitting each server's client CPU per request against its response size over all its rungs — `cost = a + b × MiB` — separates a per-request term from a per-byte one:

| client CPU | a, per request | b, per MiB |
| --- | --- | --- |
| egernia | 0.55 ms | **1.07 ms** |
| DaCHS | 1.42 ms | **1.42 ms** |
| argus | 1.27 ms | **4.50 ms** |

argus's extra per-request cost (2.3× egernia's) is consistent with the 303 redirect its sync endpoint requires the client to follow, but that term is small; it is the **per-byte term, 4.2× egernia's, that trips the guard**, contributing 14.5 ms of the ~15.8 ms a Q11 request costs the client. Q11 returns 3.23 MiB where every other class returns under 0.05 MiB, which is why the voids land there and only there.

**The threat to validity this does not repair:** the guard exists to catch the generator becoming the bottleneck, and on argus's widest class it now is. So **argus's Q11 figures at tiers 16 and 24 are under-reported even in the rungs that stayed under the limit** — this is not merely "the voided rungs were excluded". argus's Q11 column should be read as a lower bound, and the pre-registered supplementary re-measurement (`supplementary-plan.md` in the run directory, written at 06:40Z while tier 16 was still measuring and before any tier-24 rung existed) is what addresses it.

### Conditions

Gates per tier with all three stacks up: nine `taplint` runs, all PASS (egernia and DaCHS 0 errors, argus 0 blocking / 2 total each time), and the three-way agreement gate **11/11 classes at every tier**. Corpus `bc411050…`, 500,096 rows verified in all three servers at every tier, `ivoa.obscore` `relkind = 'r'` (PR #160) and no `TAP_QUERY_DATABASE_URL` in either egernia container. argus's UWS job store was truncated immediately before **every** measured block, after the gates and the warm pass, so no block inherited another's history. Resource telemetry covered the run from its first rung. An untimed 45 s warm pass preceded each block. Host state per tier in `pins/t*-host.txt`; nothing else ran on the box.

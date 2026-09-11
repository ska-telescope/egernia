# 20260910T084557Z-716fe2a1-tap-compare-scaling

Same-hardware TAP-server resource-scaling comparison: the parity
protocol's corpus, gates, query stream, formats and statistics, with
both servers' resource pins raised tier by tier. Within a tier each
server is measured alone under that tier's pins (the host cannot hold
two pinned stacks of the larger tiers at once), so repetitions do not
interleave across servers; the gates run per tier with both stacks up.
The pins actually applied, as `docker inspect` and `SHOW` saw them, are
under `pins/`. See `benchmarks/tap-compare/scaling/PROTOCOL.md` for
the pre-registered design. Where `resources.jsonl` covers a rung, the
resource tables give each server's CPU cores used, CPU time per request
and memory over the rung's window (`resources.csv` has every rung);
rungs measured before the sampler started show `—`.

## Tier 24b

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-local | 1.1 | PASS (0 errors) | 10000 |

### csv

| class | c | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 708.6 ±197.2 | 0.018 ±0.008 | — |
| Q01 | 32 | 722.6 ±16.7 | 0.075 ±0.047 | — |
| Q01 | 64 | 685.6 ±1.0 | 0.138 ±0.042 | — |
| Q03 | 8 | 574.6 ±97.0 | 0.022 ±0.008 | — |
| Q03 | 32 | 635.3 ±6.5 | 0.080 ±0.018 | — |
| Q03 | 64 | 604.3 ±2.0 | 0.147 ±0.026 | — |
| Q04 | 8 | 437.9 ±13.8 | 0.028 ±0.006 | — |
| Q04 | 32 | 560.3 ±6.3 | 0.084 ±0.018 | — |
| Q04 | 64 | 536.4 ±3.2 | 0.176 ±0.021 | — |
| Q10 | 8 | 345.2 ±29.0 | 0.034 ±0.003 | — |
| Q10 | 32 | 380.2 ±2.9 | 0.137 ±0.043 | — |
| Q10 | 64 | 370.5 ±1.0 | 0.245 ±0.065 | — |
| Q11 | 8 | 57.0 ±8.0 | 0.237 ±0.055 | — |
| Q11 | 32 | 64.9 ±3.0 | 0.968 ±0.120 | — |
| Q11 | 64 | 64.5 ±5.2 | 2.134 ±0.548 | — |
| Q13 | 8 | 48.2 ±0.3 | 0.203 ±0.001 | — |
| Q13 | 32 | 53.8 ±0.3 | 0.855 ±0.089 | — |
| Q13 | 64 | 53.6 ±0.3 | 2.025 ±0.581 | — |
| mix | 8 | 492.6 ±284.2 | 0.028 ±0.016 | — |
| mix | 32 | 606.0 ±8.4 | 0.092 ±0.022 | — |
| mix | 64 | 580.2 ±4.5 | 0.168 ±0.070 | — |

### votable

| class | c | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 633.1 ±85.4 | 0.024 ±0.009 | — |
| Q01 | 32 | 712.1 ±2.6 | 0.067 ±0.011 | — |
| Q01 | 64 | 682.5 ±0.7 | 0.148 ±0.066 | — |
| Q03 | 8 | 458.6 ±184.2 | 0.026 ±0.015 | — |
| Q03 | 32 | 622.9 ±4.1 | 0.095 ±0.028 | — |
| Q03 | 64 | 591.6 ±2.2 | 0.158 ±0.028 | — |
| Q04 | 8 | 346.3 ±66.5 | 0.033 ±0.010 | — |
| Q04 | 32 | 528.6 ±2.4 | 0.089 ±0.007 | — |
| Q04 | 64 | 509.5 ±7.5 | 0.227 ±0.165 | — |
| Q10 | 8 | 280.3 ±69.6 | 0.052 ±0.033 | — |
| Q10 | 32 | 350.4 ±1.6 | 0.138 ±0.017 | — |
| Q10 | 64 | 344.0 ±0.4 | 0.263 ±0.015 | — |
| Q11 | 8 | 43.6 ±4.6 | 0.300 ±0.075 | — |
| Q11 | 32 | 56.0 ±4.2 | 1.088 ±0.105 | — |
| Q11 | 64 | 51.2 ±1.6 | 3.189 ±0.780 | — |
| Q13 | 8 | 48.0 ±0.4 | 0.203 ±0.001 | — |
| Q13 | 32 | 53.5 ±0.4 | 0.883 ±0.098 | — |
| Q13 | 64 | 53.2 ±0.3 | 2.040 ±1.357 | — |
| mix | 8 | 523.1 ±106.8 | 0.023 ±0.003 | — |
| mix | 32 | 588.7 ±7.8 | 0.096 ±0.038 | — |
| mix | 64 | 561.4 ±1.3 | 0.180 ±0.062 | — |

### resources, csv

| class | c | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 4.24 | 6.0 ms | 1.90 | 1.90 |
| Q01 | 32 | 5.61 | 7.8 ms | 1.90 | 1.91 |
| Q01 | 64 | 5.59 | 8.2 ms | 1.91 | 1.92 |
| Q03 | 8 | 4.73 | 8.2 ms | 1.88 | 1.91 |
| Q03 | 32 | 6.44 | 10.1 ms | 1.78 | 1.83 |
| Q03 | 64 | 6.43 | 10.6 ms | 1.70 | 1.71 |
| Q04 | 8 | 5.47 | 12.5 ms | 1.68 | 1.68 |
| Q04 | 32 | 8.16 | 14.6 ms | 1.68 | 1.68 |
| Q04 | 64 | 8.10 | 15.1 ms | 1.69 | 1.69 |
| Q10 | 8 | 6.06 | 17.6 ms | 1.68 | 1.68 |
| Q10 | 32 | 7.42 | 19.5 ms | 1.69 | 1.69 |
| Q10 | 64 | 7.42 | 20.0 ms | 1.70 | 1.71 |
| Q11 | 8 | 5.71 | 100.4 ms | 1.72 | 1.73 |
| Q11 | 32 | 7.09 | 109.5 ms | 1.79 | 1.81 |
| Q11 | 64 | 7.08 | 110.4 ms | 1.89 | 1.93 |
| Q13 | 8 | 20.65 | 429.1 ms | 1.84 | 1.86 |
| Q13 | 32 | 23.96 | 446.1 ms | 1.93 | 1.94 |
| Q13 | 64 | 23.96 | 450.7 ms | 1.94 | 1.96 |
| mix | 8 | 4.49 | 9.2 ms | 1.88 | 1.90 |
| mix | 32 | 6.56 | 10.8 ms | 1.90 | 1.91 |
| mix | 64 | 6.62 | 11.4 ms | 1.91 | 1.91 |

### resources, votable

| class | c | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.88 | 6.1 ms | 1.66 | 1.67 |
| Q01 | 32 | 5.66 | 8.0 ms | 1.66 | 1.67 |
| Q01 | 64 | 5.63 | 8.2 ms | 1.67 | 1.67 |
| Q03 | 8 | 4.03 | 8.8 ms | 1.66 | 1.67 |
| Q03 | 32 | 6.57 | 10.5 ms | 1.67 | 1.67 |
| Q03 | 64 | 6.56 | 11.1 ms | 1.67 | 1.67 |
| Q04 | 8 | 4.69 | 13.5 ms | 1.67 | 1.68 |
| Q04 | 32 | 8.21 | 15.5 ms | 1.67 | 1.68 |
| Q04 | 64 | 8.17 | 16.0 ms | 1.68 | 1.69 |
| Q10 | 8 | 5.73 | 20.4 ms | 1.68 | 1.70 |
| Q10 | 32 | 7.97 | 22.8 ms | 1.69 | 1.72 |
| Q10 | 64 | 7.95 | 23.1 ms | 1.63 | 1.66 |
| Q11 | 8 | 5.60 | 128.5 ms | 1.60 | 1.61 |
| Q11 | 32 | 7.88 | 141.2 ms | 1.69 | 1.70 |
| Q11 | 64 | 7.16 | 140.9 ms | 1.82 | 1.88 |
| Q13 | 8 | 20.65 | 430.5 ms | 1.75 | 1.75 |
| Q13 | 32 | 23.96 | 449.2 ms | 1.82 | 1.84 |
| Q13 | 64 | 23.96 | 451.3 ms | 1.84 | 1.86 |
| mix | 8 | 5.06 | 9.7 ms | 1.39 | 1.40 |
| mix | 32 | 6.81 | 11.6 ms | 1.58 | 1.59 |
| mix | 64 | 6.77 | 12.1 ms | 1.65 | 1.67 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | egernia-local | 4 | 492.6 | 4.49 | 109.6 | 9.2 |
| csv | 32 | egernia-local | 4 | 606.0 | 6.56 | 92.4 | 10.8 |
| csv | 64 | egernia-local | 4 | 580.2 | 6.62 | 87.6 | 11.4 |
| votable | 8 | egernia-local | 4 | 523.1 | 5.06 | 103.4 | 9.7 |
| votable | 32 | egernia-local | 4 | 588.7 | 6.81 | 86.4 | 11.6 |
| votable | 64 | egernia-local | 4 | 561.4 | 6.77 | 82.9 | 12.1 |

## Tier 24r

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-local | 1.1 | PASS (0 errors) | 10000 |

### csv

| class | c | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 670.5 ±401.1 | 0.024 ±0.018 | — |
| Q01 | 32 | 1102.7 ±178.6 | 0.056 ±0.018 | — |
| Q01 | 64 | 1192.3 ±1.7 | 0.088 ±0.018 | — |
| Q03 | 8 | 546.8 ±356.0 | 0.024 ±0.018 | — |
| Q03 | 32 | 866.9 ±36.3 | 0.078 ±0.028 | — |
| Q03 | 64 | 1021.0 ±55.3 | 0.152 ±0.088 | — |
| Q04 | 8 | 439.8 ±37.8 | 0.028 ±0.007 | — |
| Q04 | 32 | 743.2 ±74.3 | 0.085 ±0.029 | — |
| Q04 | 64 | 850.4 ±4.3 | 0.136 ±0.014 | — |
| Q10 | 8 | 260.5 ±79.5 | 0.044 ±0.002 | — |
| Q10 | 32 | 537.1 ±11.9 | 0.114 ±0.035 | — |
| Q10 | 64 | 590.3 ±8.9 | 0.250 ±0.173 | — |
| Q11 | 8 | 57.6 ±6.9 | 0.257 ±0.027 | — |
| Q11 | 32 | 62.2 ±11.3 | 1.298 ±0.394 | — |
| Q11 | 64 | 47.4 ±11.9 | 3.642 ±0.905 | — |
| Q13 | 8 | 50.9 ±0.3 | 0.200 ±0.002 | — |
| Q13 | 32 | 55.2 ±0.5 | 0.885 ±0.107 | — |
| Q13 | 64 | 54.7 ±0.1 | 1.983 ±0.241 | — |
| mix | 8 | 532.7 ±73.2 | 0.027 ±0.016 | — |
| mix | 32 | 839.9 ±144.5 | 0.068 ±0.019 | — |
| mix | 64 | 979.5 ±23.7 | 0.127 ±0.028 | — |

### votable

| class | c | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| Q01 | 8 | 684.2 ±229.8 | 0.020 ±0.009 | — |
| Q01 | 32 | 1200.0 ±151.7 | 0.057 ±0.009 | — |
| Q01 | 64 | 1152.8 ±130.3 | 0.119 ±0.099 | — |
| Q03 | 8 | 580.2 ±96.5 | 0.022 ±0.008 | — |
| Q03 | 32 | 955.7 ±99.7 | 0.067 ±0.026 | — |
| Q03 | 64 | 982.0 ±135.0 | 0.129 ±0.053 | — |
| Q04 | 8 | 396.7 ±171.2 | 0.032 ±0.027 | — |
| Q04 | 32 | 711.6 ±40.1 | 0.099 ±0.012 | — |
| Q04 | 64 | 796.6 ±19.0 | 0.162 ±0.097 | — |
| Q10 | 8 | 269.1 ±180.9 | 0.042 ±0.025 | — |
| Q10 | 32 | 503.1 ±88.0 | 0.105 ±0.048 | — |
| Q10 | 64 | 536.0 ±1.3 | 0.232 ±0.073 | — |
| Q11 | 8 | 43.4 ±2.3 | 0.314 ±0.042 | — |
| Q11 | 32 | 48.9 ±7.2 | 1.624 ±0.457 | — |
| Q11 | 64 | 36.8 ±6.3 | 4.650 ±0.351 | — |
| Q13 | 8 | 50.9 ±0.2 | 0.200 ±0.001 | — |
| Q13 | 32 | 55.3 ±0.4 | 0.950 ±0.040 | — |
| Q13 | 64 | 54.7 ±0.5 | 1.925 ±0.170 | — |
| mix | 8 | 592.1 ±49.0 | 0.022 ±0.000 | — |
| mix | 32 | 842.9 ±71.2 | 0.075 ±0.008 | — |
| mix | 64 | 956.1 ±5.9 | 0.135 ±0.050 | — |

### resources, csv

| class | c | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.43 | 5.1 ms | 1.68 | 1.69 |
| Q01 | 32 | 7.42 | 6.7 ms | 1.68 | 1.69 |
| Q01 | 64 | 9.08 | 7.6 ms | 1.68 | 1.68 |
| Q03 | 8 | 3.22 | 5.9 ms | 1.68 | 1.68 |
| Q03 | 32 | 6.30 | 7.3 ms | 1.68 | 1.69 |
| Q03 | 64 | 8.20 | 8.0 ms | 1.69 | 1.70 |
| Q04 | 8 | 2.88 | 6.6 ms | 1.68 | 1.69 |
| Q04 | 32 | 5.93 | 8.0 ms | 1.69 | 1.70 |
| Q04 | 64 | 7.46 | 8.8 ms | 1.69 | 1.70 |
| Q10 | 8 | 2.70 | 10.4 ms | 1.69 | 1.69 |
| Q10 | 32 | 6.47 | 12.1 ms | 1.70 | 1.71 |
| Q10 | 64 | 7.57 | 12.8 ms | 1.71 | 1.72 |
| Q11 | 8 | 3.07 | 53.4 ms | 1.73 | 1.74 |
| Q11 | 32 | 3.81 | 61.1 ms | 1.81 | 1.83 |
| Q11 | 64 | 3.08 | 65.3 ms | 1.89 | 1.91 |
| Q13 | 8 | 0.44 | 8.7 ms | 1.77 | 1.77 |
| Q13 | 32 | 0.64 | 11.6 ms | 1.77 | 1.77 |
| Q13 | 64 | 0.79 | 14.4 ms | 1.78 | 1.79 |
| mix | 8 | 3.22 | 6.0 ms | 1.67 | 1.68 |
| mix | 32 | 6.46 | 7.7 ms | 1.67 | 1.67 |
| mix | 64 | 8.25 | 8.4 ms | 1.68 | 1.69 |

### resources, votable

| class | c | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| Q01 | 8 | 3.57 | 5.2 ms | 1.44 | 1.45 |
| Q01 | 32 | 7.92 | 6.6 ms | 1.44 | 1.44 |
| Q01 | 64 | 8.72 | 7.6 ms | 1.44 | 1.45 |
| Q03 | 8 | 3.40 | 5.9 ms | 1.44 | 1.45 |
| Q03 | 32 | 7.08 | 7.4 ms | 1.45 | 1.45 |
| Q03 | 64 | 8.06 | 8.2 ms | 1.45 | 1.45 |
| Q04 | 8 | 2.78 | 7.0 ms | 1.45 | 1.45 |
| Q04 | 32 | 5.98 | 8.4 ms | 1.45 | 1.46 |
| Q04 | 64 | 7.38 | 9.3 ms | 1.46 | 1.46 |
| Q10 | 8 | 3.04 | 11.3 ms | 1.46 | 1.47 |
| Q10 | 32 | 6.62 | 13.2 ms | 1.49 | 1.49 |
| Q10 | 64 | 7.47 | 13.9 ms | 1.54 | 1.56 |
| Q11 | 8 | 2.68 | 61.9 ms | 1.59 | 1.60 |
| Q11 | 32 | 3.51 | 71.6 ms | 1.69 | 1.72 |
| Q11 | 64 | 2.68 | 73.3 ms | 1.81 | 1.85 |
| Q13 | 8 | 0.44 | 8.7 ms | 1.66 | 1.67 |
| Q13 | 32 | 0.64 | 11.6 ms | 1.67 | 1.67 |
| Q13 | 64 | 0.80 | 14.6 ms | 1.67 | 1.68 |
| mix | 8 | 3.70 | 6.3 ms | 1.34 | 1.36 |
| mix | 32 | 6.57 | 7.8 ms | 1.39 | 1.40 |
| mix | 64 | 8.33 | 8.7 ms | 1.43 | 1.45 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | egernia-local | 8 | 532.7 | 3.22 | 165.4 | 6.0 |
| csv | 32 | egernia-local | 8 | 839.9 | 6.46 | 129.9 | 7.7 |
| csv | 64 | egernia-local | 8 | 979.5 | 8.25 | 118.8 | 8.4 |
| votable | 8 | egernia-local | 8 | 592.1 | 3.70 | 160.0 | 6.3 |
| votable | 32 | egernia-local | 8 | 842.9 | 6.57 | 128.2 | 7.8 |
| votable | 64 | egernia-local | 8 | 956.1 | 8.33 | 114.8 | 8.7 |

## Tier 24w

### Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| egernia-local | 1.1 | PASS (0 errors) | 10000 |

### csv

| class | c | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| mix | 8 | 584.2 ±7.2 | 0.023 ±0.009 | — |
| mix | 32 | 870.1 ±129.0 | 0.075 ±0.011 | — |
| mix | 64 | 969.5 ±69.5 | 0.128 ±0.063 | — |

### votable

| class | c | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- |
| mix | 8 | 480.9 ±254.0 | 0.027 ±0.008 | — |
| mix | 32 | 848.0 ±112.8 | 0.072 ±0.013 | — |
| mix | 64 | 934.9 ±74.5 | 0.134 ±0.022 | — |

### resources, csv

| class | c | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| mix | 8 | 5.21 | 8.9 ms | 2.39 | 2.40 |
| mix | 32 | 9.35 | 10.7 ms | 2.39 | 2.40 |
| mix | 64 | 11.32 | 11.7 ms | 2.44 | 2.48 |

### resources, votable

| class | c | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- |
| mix | 8 | 4.60 | 9.6 ms | 1.92 | 1.95 |
| mix | 32 | 9.75 | 11.5 ms | 2.15 | 2.19 |
| mix | 64 | 11.54 | 12.3 ms | 2.34 | 2.38 |

### throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 8 | egernia-local | 8 | 584.2 | 5.21 | 112.1 | 8.9 |
| csv | 32 | egernia-local | 8 | 870.1 | 9.35 | 93.1 | 10.7 |
| csv | 64 | egernia-local | 8 | 969.5 | 11.32 | 85.7 | 11.7 |
| votable | 8 | egernia-local | 8 | 480.9 | 4.60 | 104.5 | 9.6 |
| votable | 32 | egernia-local | 8 | 848.0 | 9.75 | 87.0 | 11.5 |
| votable | 64 | egernia-local | 8 | 934.9 | 11.54 | 81.0 | 12.3 |

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

Environment: see `environment.json` (git 716fe2a1, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What the three tiers are.** All three give egernia the same 24 CPU / 24 GiB budget on one host (generators on cores 24–29, six processes) and all three serve the denormalised `ivoa.obscore` relation of PR #160. **24b** is the baseline: four API workers, one PostgreSQL with the whole 12 GiB. **24r** is the same API with `TAP_QUERY_DATABASE_URL` (PR #161) pointing at three streaming-replication standbys, the database's 12 GiB split four ways (primary 3 GiB, standbys 3 GiB each), each server sized to its own container by the ¼/¾ rule. **24w** is a control: eight API workers against the single database, to separate "more workers" from "more databases". Protocol and hypotheses: `benchmarks/tap-compare/scaling-replicas/PROTOCOL.md`, tag `tap-compare-scaling-replicas-prereg-v1`.
- **The routing is doing what the tier claims.** Over twenty seconds of a live 24r rung the three standbys returned 26.5 M tuples (2.7 M / 13.9 M / 10.0 M) against 2,236 on the primary — metadata and health only. The split between standbys is uneven by construction: libpq assigns a host per *connection*, not per query. Replication lag over 24 observations: write 0.27 ms median / 0.76 ms max, flush 0.86 / 1.12, replay 0.97 / 1.21. That is the consistency window `docs/deployment.md` asserts for the query path, measured.
- **Where replicas help, and where they do not.** At c=32 and c=64 the API-bound classes gain 1.3–1.7× (mix ×1.69, Q01 ×1.74, Q03 ×1.69, Q04 ×1.59, Q10 ×1.59 at c=64), and the mixed workload reaches 979 rps. At c=8 there is no gain (0.95–1.06×): eight clients cannot keep four workers and three databases busy, and the closed loop, not the server, is the limit. **Q13, the full-table aggregate, does not benefit** (×1.02–1.06): one such query saturates its own standby's parallel workers, so spreading three of them over three 3 GiB standbys buys nothing a single 12 GiB instance did not already give. **Q11 loses at c=64** (×0.74): a 10,000-row result is bound by the bytes one standby can produce, and a 3 GiB standby has a quarter of the baseline's shared buffers.
- **The 24w control separates the two effects.** Doubling workers against one database reaches 870 rps at c=32 and 970 at c=64 on the mix — indistinguishable from 24r's 840 and 980. So at this budget the gain measured in 24r is the API's worker count, not the number of databases; replicas earn their place when the database is the ceiling or when it must survive one instance failing, not as a throughput multiplier for this workload on one host. Stated as a negative result: hypotheses H1 (Q13 scales with standbys) and H4 (the mix gains from replicas specifically) are **not** supported; H3 (Q01 ties between 24w and 24r) is.
- **Conditions.** 270 rungs, 08:46:58Z → 14:50Z on 2026-09-10, gates passed per tier (taplint 0 blocking errors; no agreement gate, single target), no generator-guard trip, no rung over the 1% error ceiling, resource sampler from the first rung. An earlier attempt at this run (`20260910T074757Z-e56f490c`) was abandoned at 35 rungs and left unpublished: a concurrent driver recreated the stacks onto another protocol's pins mid-run, invalidating three rungs; both drivers now refuse to start while another measurement is alive. Recorded as Amendment 2 in the protocol.

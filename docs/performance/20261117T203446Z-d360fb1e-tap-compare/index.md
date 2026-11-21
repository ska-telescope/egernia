# 20261117T203446Z-d360fb1e-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: argus in `benchmarks/tap-compare/docker-compose.argus.yml` + `final/pins/argus.yml` (`cpuset` 8-15; 8 GiB split 3 Tomcat / 5 PostgreSQL; `benchmarks/tap-compare/final/PROTOCOL.md`); DaCHS in `benchmarks/tap-compare/docker-compose.dachs.yml` + `final/pins/dachs.yml` (`cpus: 8`, `cpuset` 16-23, `mem_limit: 8g`, its PostgreSQL sized to the container by the ¼ rule; `benchmarks/tap-compare/final/PROTOCOL.md`); egernia on skycell in `benchmarks/tap-compare/final-skycell/pins/egernia-w1.yml` + `skycell.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=1`; `benchmarks/tap-compare/final-skycell/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-final | 1.1 | PASS (2 errors) | 134217728 |
| dachs-final | 1.1 | PASS (0 errors) | 20000 |
| egernia-skycell-w1 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-skycell-w1 rps | egernia-skycell-w1 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 89.8 ±12.9 | 0.012 ±0.000 | 23.1 ±0.0 | 0.164 ±0.003 | 230.0 ±1.4 | 0.005 ±0.000 | egernia-skycell-w1 |
| Q01 | 4 | 267.3 ±27.7 | 0.017 ±0.000 | 18.0 ±0.3 | 0.341 ±0.011 | 314.3 ±3.7 | 0.016 ±0.000 | egernia-skycell-w1 |
| Q01 | 8 | 431.6 ±4.5 | 0.022 ±0.000 | 17.0 ±0.0 | 0.577 ±0.011 | 304.5 ±3.7 | 0.035 ±0.000 | argus-final |
| Q01 | 32 | 527.5 ±88.6 | 0.068 ±0.002 | 15.7 ±0.1 | 2.220 ±0.077 | 284.1 ±0.6 | 0.129 ±0.002 | argus-final |
| Q02 | 1 | 2.5 ±0.0 | 0.416 ±0.018 | 5.3 ±0.3 | 0.303 ±0.024 | 136.8 ±1.1 | 0.012 ±0.000 | egernia-skycell-w1 |
| Q02 | 4 | 9.4 ±1.0 | 0.507 ±0.041 | 10.1 ±0.2 | 0.547 ±0.008 | 258.9 ±3.9 | 0.021 ±0.000 | egernia-skycell-w1 |
| Q02 | 8 | 15.7 ±0.2 | 0.536 ±0.008 | 9.3 ±0.1 | 1.061 ±0.023 | 254.4 ±1.7 | 0.042 ±0.000 | egernia-skycell-w1 |
| Q02 | 32 | 16.0 ±0.2 | 2.088 ±0.052 | 8.7 ±0.1 | 3.830 ±0.006 | 229.1 ±2.2 | 0.160 ±0.001 | egernia-skycell-w1 |
| Q03 | 1 | 41.8 ±2.0 | 0.084 ±0.001 | 11.8 ±0.1 | 0.201 ±0.002 | 161.8 ±2.4 | 0.007 ±0.000 | egernia-skycell-w1 |
| Q03 | 4 | 138.6 ±0.6 | 0.094 ±0.001 | 12.2 ±0.2 | 0.475 ±0.014 | 279.4 ±0.7 | 0.018 ±0.000 | egernia-skycell-w1 |
| Q03 | 8 | 203.8 ±6.5 | 0.115 ±0.001 | 11.7 ±0.1 | 0.846 ±0.009 | 268.1 ±12.1 | 0.040 ±0.003 | egernia-skycell-w1 |
| Q03 | 32 | 254.5 ±2.1 | 0.239 ±0.002 | 11.0 ±0.2 | 3.107 ±0.104 | 242.1 ±2.4 | 0.151 ±0.002 | tie |
| Q04 | 1 | 61.3 ±2.0 | 0.018 ±0.001 | 12.3 ±0.2 | 0.206 ±0.001 | 100.1 ±2.3 | 0.011 ±0.000 | egernia-skycell-w1 |
| Q04 | 4 | 168.0 ±8.3 | 0.028 ±0.000 | 12.3 ±0.1 | 0.464 ±0.009 | 220.4 ±1.3 | 0.023 ±0.000 | egernia-skycell-w1 |
| Q04 | 8 | 222.6 ±21.6 | 0.040 ±0.001 | 11.7 ±0.2 | 0.836 ±0.008 | 226.6 ±2.0 | 0.046 ±0.001 | tie |
| Q04 | 32 | 310.8 ±1.9 | 0.119 ±0.001 | 11.2 ±0.0 | 3.047 ±0.007 | 208.1 ±1.5 | 0.176 ±0.001 | argus-final |
| Q05 | 1 | 2.4 ±0.1 | 0.423 ±0.010 | 1.8 ±0.0 | 0.682 ±0.010 | 197.1 ±1.6 | 0.006 ±0.000 | egernia-skycell-w1 |
| Q05 | 4 | 9.3 ±1.0 | 0.501 ±0.169 | 5.8 ±0.1 | 0.845 ±0.019 | 300.8 ±2.5 | 0.017 ±0.000 | egernia-skycell-w1 |
| Q05 | 8 | 14.7 ±0.0 | 0.574 ±0.004 | 7.8 ±0.2 | 1.277 ±0.073 | 291.9 ±2.1 | 0.036 ±0.000 | egernia-skycell-w1 |
| Q05 | 32 | 14.9 ±0.1 | 2.260 ±0.016 | 7.9 ±0.1 | 4.337 ±0.026 | 264.0 ±1.5 | 0.139 ±0.001 | egernia-skycell-w1 |
| Q06 | 1 | 2.5 ±0.1 | 0.420 ±0.001 | 1.7 ±0.0 | 0.695 ±0.015 | 163.4 ±0.9 | 0.007 ±0.000 | egernia-skycell-w1 |
| Q06 | 4 | 9.3 ±1.6 | 0.500 ±0.173 | 5.8 ±0.1 | 0.862 ±0.031 | 246.0 ±3.4 | 0.021 ±0.000 | egernia-skycell-w1 |
| Q06 | 8 | 14.7 ±0.4 | 0.582 ±0.005 | 7.6 ±0.0 | 1.337 ±0.089 | 241.1 ±2.6 | 0.044 ±0.001 | egernia-skycell-w1 |
| Q06 | 32 | 14.9 ±0.1 | 2.256 ±0.039 | 7.5 ±0.8 | 5.267 ±3.566 | 218.4 ±2.8 | 0.169 ±0.003 | egernia-skycell-w1 |
| Q07 | 1 | 3.4 ±0.1 | 0.414 ±0.018 | 1.7 ±0.0 | 0.709 ±0.002 | 180.7 ±6.5 | 0.006 ±0.000 | egernia-skycell-w1 |
| Q07 | 4 | 12.3 ±0.1 | 0.489 ±0.017 | 5.4 ±0.5 | 0.924 ±0.129 | 287.1 ±2.3 | 0.018 ±0.000 | egernia-skycell-w1 |
| Q07 | 8 | 20.8 ±0.2 | 0.545 ±0.009 | 7.4 ±0.1 | 1.331 ±0.029 | 276.8 ±2.0 | 0.038 ±0.000 | egernia-skycell-w1 |
| Q07 | 32 | 21.4 ±0.0 | 1.732 ±0.055 | 7.5 ±0.2 | 4.582 ±0.059 | 248.3 ±1.0 | 0.148 ±0.001 | egernia-skycell-w1 |
| Q10 | 1 | 38.2 ±1.2 | 0.029 ±0.001 | 10.4 ±0.4 | 0.223 ±0.005 | 88.0 ±2.3 | 0.014 ±0.001 | egernia-skycell-w1 |
| Q10 | 4 | 104.5 ±15.9 | 0.044 ±0.000 | 10.8 ±0.2 | 0.517 ±0.004 | 151.0 ±1.0 | 0.034 ±0.000 | egernia-skycell-w1 |
| Q10 | 8 | 154.8 ±13.7 | 0.062 ±0.001 | 10.4 ±0.2 | 0.931 ±0.036 | 151.4 ±0.5 | 0.070 ±0.000 | tie |
| Q10 | 32 | 179.0 ±4.0 | 0.203 ±0.004 | 10.0 ±0.1 | 3.407 ±0.056 | 142.1 ±0.5 | 0.262 ±0.002 | argus-final |
| Q11 | 1 | 6.0 ±0.2 | 0.174 ±0.004 | 3.5 ±0.0 | 0.409 ±0.002 | 13.1 ±0.5 | 0.090 ±0.001 | egernia-skycell-w1 |
| Q11 | 4 | 19.1 ±0.1 | 0.235 ±0.001 | 3.9 ±0.1 | 1.262 ±0.043 | 19.7 ±0.4 | 0.309 ±0.022 | tie |
| Q11 | 8 | 27.2 ±0.0 | 0.338 ±0.003 | 4.0 ±0.0 | 2.674 ±0.202 | 20.9 ±0.8 | 0.479 ±0.078 | argus-final |
| Q11 | 32 | 27.9 ±0.3 | 1.233 ±0.036 | 4.1 ±0.0 | 12.526 ±1.686 | 19.6 ±4.7 | 3.479 ±3.293 | argus-final |
| Q12 | 1 | 2.4 ±0.1 | 0.422 ±0.014 | 1.8 ±0.0 | 0.693 ±0.010 | 201.0 ±3.3 | 0.006 ±0.000 | egernia-skycell-w1 |
| Q12 | 4 | 9.1 ±1.4 | 0.498 ±0.179 | 5.9 ±0.2 | 0.841 ±0.025 | 306.8 ±3.7 | 0.017 ±0.000 | egernia-skycell-w1 |
| Q12 | 8 | 14.8 ±0.1 | 0.573 ±0.005 | 7.8 ±0.1 | 1.286 ±0.011 | 296.7 ±1.3 | 0.036 ±0.000 | egernia-skycell-w1 |
| Q12 | 32 | 15.0 ±0.1 | 2.247 ±0.045 | 7.9 ±0.2 | 4.351 ±0.219 | 270.5 ±0.7 | 0.135 ±0.001 | egernia-skycell-w1 |
| Q13 | 1 | 2.7 ±0.0 | 0.411 ±0.005 | 2.8 ±0.3 | 0.527 ±0.011 | 8.6 ±0.2 | 0.160 ±0.001 | egernia-skycell-w1 |
| Q13 | 4 | 10.1 ±0.3 | 0.514 ±0.052 | 8.5 ±0.4 | 0.693 ±0.036 | 19.6 ±0.1 | 0.271 ±0.001 | egernia-skycell-w1 |
| Q13 | 8 | 17.0 ±0.1 | 0.561 ±0.005 | 9.7 ±0.1 | 1.176 ±0.008 | 20.7 ±0.3 | 0.532 ±0.018 | egernia-skycell-w1 |
| Q13 | 32 | 17.4 ±0.3 | 2.003 ±0.009 | 9.4 ±0.2 | 3.765 ±0.095 | 20.6 ±0.1 | 1.759 ±0.027 | egernia-skycell-w1 |
| mix | 1 | 4.1 ±0.5 | 0.413 ±0.004 | 3.1 ±0.2 | 0.653 ±0.111 | 150.1 ±5.1 | 0.011 ±0.000 | egernia-skycell-w1 |
| mix | 4 | 15.4 ±2.1 | 0.457 ±0.146 | 8.6 ±0.5 | 0.861 ±0.036 | 259.7 ±1.7 | 0.022 ±0.000 | egernia-skycell-w1 |
| mix | 8 | 24.0 ±0.9 | 0.566 ±0.002 | 9.4 ±0.6 | 1.342 ±0.025 | 254.9 ±1.0 | 0.043 ±0.000 | egernia-skycell-w1 |
| mix | 32 | 24.8 ±1.2 | 1.692 ±0.131 | 9.0 ±0.1 | 4.137 ±0.192 | 231.3 ±0.7 | 0.160 ±0.002 | egernia-skycell-w1 |

## votable

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-skycell-w1 rps | egernia-skycell-w1 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 96.4 ±2.0 | 0.012 ±0.000 | 22.4 ±0.8 | 0.131 ±0.011 | 223.4 ±10.3 | 0.005 ±0.000 | egernia-skycell-w1 |
| Q01 | 4 | 281.9 ±5.4 | 0.017 ±0.001 | 18.0 ±0.8 | 0.330 ±0.030 | 306.9 ±10.3 | 0.017 ±0.001 | tie |
| Q01 | 8 | 425.8 ±13.2 | 0.022 ±0.000 | 16.8 ±0.4 | 0.580 ±0.008 | 298.3 ±4.8 | 0.036 ±0.001 | argus-final |
| Q01 | 32 | 537.1 ±57.2 | 0.069 ±0.003 | 15.2 ±0.4 | 2.257 ±0.071 | 280.1 ±5.9 | 0.132 ±0.005 | argus-final |
| Q02 | 1 | 2.5 ±0.1 | 0.401 ±0.021 | 5.2 ±0.5 | 0.314 ±0.041 | 128.6 ±4.5 | 0.012 ±0.000 | egernia-skycell-w1 |
| Q02 | 4 | 9.4 ±0.8 | 0.484 ±0.114 | 9.9 ±0.2 | 0.552 ±0.037 | 245.4 ±9.0 | 0.022 ±0.001 | egernia-skycell-w1 |
| Q02 | 8 | 15.6 ±0.6 | 0.545 ±0.010 | 9.2 ±0.0 | 1.062 ±0.026 | 246.8 ±3.1 | 0.044 ±0.001 | egernia-skycell-w1 |
| Q02 | 32 | 15.8 ±0.6 | 2.109 ±0.037 | 8.7 ±0.3 | 3.843 ±0.075 | 223.6 ±2.5 | 0.164 ±0.002 | egernia-skycell-w1 |
| Q03 | 1 | 41.5 ±1.2 | 0.079 ±0.007 | 11.3 ±0.2 | 0.206 ±0.010 | 152.2 ±7.2 | 0.008 ±0.001 | egernia-skycell-w1 |
| Q03 | 4 | 135.8 ±1.4 | 0.094 ±0.000 | 11.9 ±0.1 | 0.480 ±0.022 | 269.1 ±3.5 | 0.019 ±0.000 | egernia-skycell-w1 |
| Q03 | 8 | 203.9 ±4.0 | 0.115 ±0.000 | 11.5 ±0.3 | 0.856 ±0.040 | 261.2 ±1.1 | 0.041 ±0.000 | egernia-skycell-w1 |
| Q03 | 32 | 239.9 ±26.7 | 0.240 ±0.007 | 10.9 ±0.2 | 3.109 ±0.040 | 236.4 ±1.7 | 0.155 ±0.003 | tie |
| Q04 | 1 | 57.2 ±2.3 | 0.019 ±0.001 | 11.9 ±0.0 | 0.211 ±0.004 | 96.7 ±2.6 | 0.012 ±0.000 | egernia-skycell-w1 |
| Q04 | 4 | 158.5 ±5.5 | 0.030 ±0.000 | 11.8 ±1.1 | 0.484 ±0.097 | 214.2 ±5.9 | 0.024 ±0.001 | egernia-skycell-w1 |
| Q04 | 8 | 233.1 ±3.9 | 0.042 ±0.000 | 11.7 ±0.2 | 0.827 ±0.004 | 219.9 ±0.8 | 0.048 ±0.000 | tie |
| Q04 | 32 | 285.5 ±7.6 | 0.130 ±0.006 | 10.9 ±0.0 | 3.114 ±0.022 | 202.4 ±3.2 | 0.182 ±0.009 | argus-final |
| Q05 | 1 | 2.4 ±0.1 | 0.422 ±0.012 | 1.8 ±0.0 | 0.688 ±0.023 | 188.4 ±3.3 | 0.006 ±0.000 | egernia-skycell-w1 |
| Q05 | 4 | 9.1 ±1.3 | 0.529 ±0.044 | 5.8 ±0.2 | 0.858 ±0.057 | 297.3 ±1.2 | 0.017 ±0.000 | egernia-skycell-w1 |
| Q05 | 8 | 11.4 ±9.3 | 1.599 ±3.405 | 5.6 ±4.7 | 2.863 ±4.675 | 266.3 ±23.1 | 0.041 ±0.006 | egernia-skycell-w1 |
| Q05 | 32 | 14.9 ±0.1 | 2.252 ±0.035 | 7.7 ±0.1 | 4.387 ±0.045 | 258.0 ±0.7 | 0.142 ±0.001 | egernia-skycell-w1 |
| Q06 | 1 | 2.4 ±0.1 | 0.427 ±0.018 | 1.7 ±0.0 | 0.702 ±0.018 | 150.3 ±2.0 | 0.008 ±0.000 | egernia-skycell-w1 |
| Q06 | 4 | 8.8 ±0.6 | 0.546 ±0.008 | 5.8 ±0.2 | 0.855 ±0.060 | 234.8 ±18.8 | 0.022 ±0.003 | egernia-skycell-w1 |
| Q06 | 8 | 14.7 ±0.1 | 0.592 ±0.007 | 7.6 ±0.2 | 1.350 ±0.086 | 228.6 ±13.9 | 0.047 ±0.004 | egernia-skycell-w1 |
| Q06 | 32 | 14.9 ±0.1 | 2.280 ±0.063 | 7.6 ±0.1 | 4.501 ±0.044 | 208.7 ±8.0 | 0.180 ±0.019 | egernia-skycell-w1 |
| Q07 | 1 | 3.5 ±0.1 | 0.405 ±0.021 | 1.7 ±0.0 | 0.709 ±0.020 | 167.5 ±15.0 | 0.007 ±0.002 | egernia-skycell-w1 |
| Q07 | 4 | 12.1 ±0.7 | 0.494 ±0.046 | 5.5 ±0.2 | 0.904 ±0.033 | 277.7 ±1.8 | 0.018 ±0.000 | egernia-skycell-w1 |
| Q07 | 8 | 20.6 ±0.7 | 0.554 ±0.018 | 7.3 ±0.2 | 1.381 ±0.085 | 269.2 ±1.1 | 0.040 ±0.000 | egernia-skycell-w1 |
| Q07 | 32 | 21.4 ±0.1 | 1.740 ±0.023 | 7.4 ±0.2 | 4.643 ±0.082 | 239.9 ±12.2 | 0.156 ±0.020 | egernia-skycell-w1 |
| Q10 | 1 | 31.3 ±3.3 | 0.034 ±0.000 | 10.4 ±0.1 | 0.232 ±0.003 | 73.2 ±2.1 | 0.017 ±0.001 | egernia-skycell-w1 |
| Q10 | 4 | 90.0 ±20.2 | 0.060 ±0.037 | 10.8 ±0.3 | 0.503 ±0.014 | 141.8 ±2.0 | 0.036 ±0.001 | egernia-skycell-w1 |
| Q10 | 8 | 134.7 ±8.6 | 0.073 ±0.001 | 10.3 ±1.5 | 0.983 ±0.299 | 141.3 ±4.4 | 0.075 ±0.004 | tie |
| Q10 | 32 | 145.8 ±1.4 | 0.248 ±0.001 | 10.2 ±0.1 | 3.395 ±0.055 | 133.6 ±1.8 | 0.279 ±0.009 | tie |
| Q11 | 1 | 4.7 ±0.5 | 0.233 ±0.069 | 3.9 ±0.1 | 0.381 ±0.022 | 10.3 ±0.9 | 0.107 ±0.001 | egernia-skycell-w1 |
| Q11 | 4 | 15.0 ±0.0 | 0.306 ±0.003 | 4.2 ±1.2 | 1.266 ±0.541 | 16.7 ±2.6 | 0.374 ±0.280 | tie |
| Q11 | 8 | 21.4 ±0.1 | 0.432 ±0.009 | 4.4 ±0.1 | 2.296 ±0.208 | 17.5 ±0.6 | 0.640 ±0.214 | argus-final |
| Q11 | 32 | 21.7 ±0.3 | 1.576 ±0.015 | 4.6 ±0.0 | 11.064 ±0.589 | 15.9 ±11.4 (1% err) | 3.727 ±5.619 | argus-final |
| Q12 | 1 | 2.4 ±0.1 | 0.419 ±0.009 | 1.7 ±0.1 | 0.687 ±0.035 | 192.1 ±5.4 | 0.006 ±0.000 | egernia-skycell-w1 |
| Q12 | 4 | 8.5 ±1.2 | 0.530 ±0.019 | 5.9 ±0.2 | 0.853 ±0.032 | 301.5 ±2.2 | 0.017 ±0.000 | egernia-skycell-w1 |
| Q12 | 8 | 14.7 ±0.1 | 0.576 ±0.019 | 7.7 ±0.1 | 1.297 ±0.076 | 289.1 ±10.3 | 0.037 ±0.002 | egernia-skycell-w1 |
| Q12 | 32 | 14.8 ±0.2 | 2.237 ±0.017 | 7.8 ±0.1 | 4.387 ±0.154 | 263.5 ±2.2 | 0.140 ±0.006 | egernia-skycell-w1 |
| Q13 | 1 | 2.7 ±0.1 | 0.413 ±0.009 | 2.8 ±0.2 | 0.499 ±0.050 | 8.5 ±0.2 | 0.160 ±0.006 | egernia-skycell-w1 |
| Q13 | 4 | 9.8 ±0.5 | 0.529 ±0.017 | 8.4 ±0.1 | 0.719 ±0.061 | 19.6 ±0.1 | 0.269 ±0.004 | egernia-skycell-w1 |
| Q13 | 8 | 17.0 ±0.2 | 0.563 ±0.002 | 9.5 ±0.1 | 1.172 ±0.029 | 20.7 ±0.3 | 0.536 ±0.003 | egernia-skycell-w1 |
| Q13 | 32 | 17.4 ±0.2 | 2.010 ±0.013 | 9.2 ±0.2 | 3.786 ±0.069 | 20.5 ±0.0 | 1.761 ±0.021 | egernia-skycell-w1 |
| mix | 1 | 4.0 ±0.6 | 0.422 ±0.004 | 3.1 ±0.3 | 0.621 ±0.094 | 138.5 ±2.8 | 0.013 ±0.000 | egernia-skycell-w1 |
| mix | 4 | 14.3 ±1.9 | 0.528 ±0.013 | 8.8 ±0.4 | 0.851 ±0.029 | 250.7 ±2.4 | 0.023 ±0.000 | egernia-skycell-w1 |
| mix | 8 | 23.8 ±1.0 | 0.575 ±0.011 | 9.5 ±0.4 | 1.304 ±0.017 | 245.5 ±5.9 | 0.044 ±0.001 | egernia-skycell-w1 |
| mix | 32 | 24.4 ±0.5 | 1.731 ±0.053 | 9.1 ±0.2 | 4.069 ±0.072 | 223.2 ±4.1 | 0.167 ±0.003 | egernia-skycell-w1 |

## resources, csv

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-w1 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.65 | 7.2 ms | 3.86 | 3.91 | 0.96 | 41.7 ms | 1.12 | 1.12 | 0.78 | 3.4 ms | 1.04 | 1.05 |
| Q01 | 4 | 2.26 | 8.5 ms | 4.17 | 4.32 | 1.77 | 98.9 ms | 1.12 | 1.13 | 1.38 | 4.4 ms | 1.03 | 1.04 |
| Q01 | 8 | 4.08 | 9.5 ms | 4.41 | 4.47 | 1.95 | 114.5 ms | 1.13 | 1.13 | 1.44 | 4.7 ms | 1.03 | 1.03 |
| Q01 | 32 | 5.56 | 10.5 ms | 4.68 | 4.83 | 1.90 | 122.8 ms | 1.14 | 1.15 | 1.41 | 5.0 ms | 1.03 | 1.04 |
| Q02 | 1 | 1.00 | 406.2 ms | 4.78 | 4.78 | 2.20 | 412.1 ms | 1.12 | 1.13 | 0.92 | 6.7 ms | 1.04 | 1.05 |
| Q02 | 4 | 3.96 | 424.6 ms | 4.79 | 4.80 | 5.07 | 503.1 ms | 1.13 | 1.15 | 2.01 | 7.8 ms | 1.04 | 1.04 |
| Q02 | 8 | 7.71 | 492.9 ms | 4.78 | 4.79 | 5.07 | 549.3 ms | 1.15 | 1.16 | 2.13 | 8.4 ms | 1.04 | 1.04 |
| Q02 | 32 | 7.92 | 498.1 ms | 4.74 | 4.77 | 4.96 | 573.0 ms | 1.15 | 1.17 | 2.04 | 8.9 ms | 1.04 | 1.05 |
| Q03 | 1 | 0.87 | 20.8 ms | 4.64 | 4.66 | 1.22 | 103.4 ms | 1.14 | 1.15 | 0.89 | 5.5 ms | 1.05 | 1.06 |
| Q03 | 4 | 3.16 | 22.8 ms | 4.55 | 4.64 | 1.93 | 158.6 ms | 1.16 | 1.16 | 1.78 | 6.4 ms | 1.04 | 1.05 |
| Q03 | 8 | 5.09 | 25.0 ms | 4.51 | 4.59 | 2.13 | 183.8 ms | 1.17 | 1.18 | 1.84 | 6.9 ms | 1.05 | 1.06 |
| Q03 | 32 | 6.88 | 27.1 ms | 4.71 | 4.77 | 2.11 | 194.8 ms | 1.17 | 1.18 | 1.78 | 7.4 ms | 1.05 | 1.06 |
| Q04 | 1 | 0.82 | 13.3 ms | 4.72 | 4.73 | 0.99 | 80.3 ms | 1.17 | 1.17 | 0.98 | 9.8 ms | 1.05 | 1.06 |
| Q04 | 4 | 2.86 | 17.0 ms | 4.76 | 4.77 | 1.62 | 132.3 ms | 1.18 | 1.18 | 2.36 | 10.7 ms | 1.05 | 1.06 |
| Q04 | 8 | 4.20 | 18.9 ms | 4.91 | 5.09 | 1.84 | 156.5 ms | 1.19 | 1.19 | 2.53 | 11.2 ms | 1.05 | 1.05 |
| Q04 | 32 | 6.33 | 20.4 ms | 5.14 | 5.19 | 1.86 | 169.5 ms | 1.19 | 1.20 | 2.43 | 11.7 ms | 1.05 | 1.06 |
| Q05 | 1 | 1.00 | 414.4 ms | 5.14 | 5.15 | 1.04 | 590.4 ms | 1.21 | 1.21 | 0.81 | 4.1 ms | 1.06 | 1.06 |
| Q05 | 4 | 3.97 | 430.4 ms | 5.16 | 5.17 | 3.92 | 673.9 ms | 1.27 | 1.30 | 1.55 | 5.1 ms | 1.05 | 1.05 |
| Q05 | 8 | 7.75 | 527.9 ms | 5.15 | 5.16 | 6.15 | 795.4 ms | 1.32 | 1.40 | 1.62 | 5.5 ms | 1.06 | 1.07 |
| Q05 | 32 | 7.94 | 538.8 ms | 5.10 | 5.12 | 6.52 | 848.7 ms | 1.33 | 1.43 | 1.58 | 6.0 ms | 1.06 | 1.06 |
| Q06 | 1 | 1.00 | 407.0 ms | 5.00 | 5.01 | 1.04 | 594.6 ms | 1.21 | 1.22 | 0.94 | 5.7 ms | 1.06 | 1.07 |
| Q06 | 4 | 3.97 | 427.0 ms | 5.00 | 5.01 | 3.91 | 673.2 ms | 1.27 | 1.30 | 1.69 | 6.9 ms | 1.06 | 1.07 |
| Q06 | 8 | 7.71 | 525.9 ms | 5.00 | 5.01 | 5.99 | 796.1 ms | 1.31 | 1.40 | 1.74 | 7.2 ms | 1.06 | 1.07 |
| Q06 | 32 | 7.90 | 537.0 ms | 4.95 | 4.97 | 6.16 | 845.3 ms | 1.33 | 1.44 | 1.68 | 7.7 ms | 1.06 | 1.07 |
| Q07 | 1 | 1.00 | 291.7 ms | 4.86 | 4.87 | 1.04 | 612.1 ms | 1.21 | 1.22 | 0.86 | 4.7 ms | 1.07 | 1.08 |
| Q07 | 4 | 3.95 | 321.3 ms | 4.86 | 4.87 | 3.84 | 710.8 ms | 1.27 | 1.30 | 1.63 | 5.7 ms | 1.06 | 1.07 |
| Q07 | 8 | 7.59 | 366.5 ms | 4.85 | 4.87 | 6.08 | 830.0 ms | 1.32 | 1.40 | 1.68 | 6.1 ms | 1.07 | 1.08 |
| Q07 | 32 | 7.90 | 371.8 ms | 4.78 | 4.82 | 6.42 | 880.0 ms | 1.33 | 1.42 | 1.64 | 6.6 ms | 1.07 | 1.08 |
| Q10 | 1 | 0.91 | 23.9 ms | 4.68 | 4.69 | 0.98 | 94.3 ms | 1.19 | 1.20 | 1.18 | 13.4 ms | 1.07 | 1.09 |
| Q10 | 4 | 3.04 | 29.1 ms | 4.76 | 4.81 | 1.58 | 146.4 ms | 1.20 | 1.21 | 2.21 | 14.6 ms | 1.07 | 1.08 |
| Q10 | 8 | 4.90 | 31.7 ms | 4.96 | 5.03 | 1.79 | 172.7 ms | 1.21 | 1.22 | 2.25 | 14.9 ms | 1.08 | 1.09 |
| Q10 | 32 | 5.95 | 33.2 ms | 5.06 | 5.09 | 1.84 | 187.3 ms | 1.22 | 1.22 | 2.18 | 15.3 ms | 1.08 | 1.08 |
| Q11 | 1 | 1.04 | 172.7 ms | 5.05 | 5.05 | 1.00 | 285.1 ms | 1.21 | 1.22 | 1.24 | 94.9 ms | 1.08 | 1.08 |
| Q11 | 4 | 3.78 | 198.8 ms | 5.06 | 5.07 | 1.39 | 353.8 ms | 1.26 | 1.28 | 1.99 | 101.1 ms | 1.09 | 1.10 |
| Q11 | 8 | 5.86 | 215.5 ms | 5.04 | 5.06 | 1.50 | 376.6 ms | 1.30 | 1.33 | 2.13 | 102.2 ms | 1.11 | 1.12 |
| Q11 | 32 | 6.11 | 219.6 ms | 5.01 | 5.03 | 1.58 | 386.0 ms | 1.33 | 1.37 | 1.98 | 101.3 ms | 1.16 | 1.18 |
| Q12 | 1 | 1.00 | 414.9 ms | 4.95 | 4.96 | 1.04 | 588.3 ms | 1.29 | 1.30 | 0.81 | 4.0 ms | 1.10 | 1.11 |
| Q12 | 4 | 3.97 | 436.3 ms | 4.94 | 4.95 | 3.96 | 675.7 ms | 1.34 | 1.37 | 1.53 | 5.0 ms | 1.10 | 1.11 |
| Q12 | 8 | 7.75 | 527.1 ms | 4.93 | 4.96 | 6.14 | 790.5 ms | 1.39 | 1.45 | 1.60 | 5.4 ms | 1.10 | 1.10 |
| Q12 | 32 | 7.95 | 537.5 ms | 4.90 | 4.91 | 6.51 | 844.6 ms | 1.38 | 1.48 | 1.57 | 5.8 ms | 1.10 | 1.10 |
| Q13 | 1 | 1.00 | 364.7 ms | 4.85 | 4.85 | 1.17 | 421.0 ms | 1.24 | 1.25 | 2.76 | 322.9 ms | 1.11 | 1.12 |
| Q13 | 4 | 3.95 | 391.4 ms | 4.85 | 4.86 | 4.10 | 483.1 ms | 1.25 | 1.26 | 7.54 | 384.6 ms | 1.13 | 1.15 |
| Q13 | 8 | 7.70 | 453.7 ms | 4.86 | 4.87 | 5.43 | 564.4 ms | 1.26 | 1.28 | 7.96 | 385.6 ms | 1.16 | 1.18 |
| Q13 | 32 | 7.94 | 461.4 ms | 4.87 | 4.88 | 5.41 | 590.4 ms | 1.25 | 1.28 | 7.96 | 390.5 ms | 1.16 | 1.18 |
| mix | 1 | 1.00 | 244.3 ms | 3.74 | 3.75 | 1.15 | 374.8 ms | 1.13 | 1.14 | 0.91 | 6.1 ms | 1.04 | 1.05 |
| mix | 4 | 3.94 | 256.9 ms | 3.77 | 3.77 | 3.81 | 443.2 ms | 1.17 | 1.22 | 1.85 | 7.1 ms | 1.03 | 1.04 |
| mix | 8 | 7.55 | 316.5 ms | 3.80 | 3.80 | 4.80 | 515.1 ms | 1.19 | 1.27 | 1.92 | 7.5 ms | 1.04 | 1.05 |
| mix | 32 | 7.87 | 319.6 ms | 3.83 | 3.84 | 4.80 | 541.3 ms | 1.20 | 1.29 | 1.85 | 8.0 ms | 1.04 | 1.05 |

## resources, votable

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-w1 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.70 | 7.3 ms | 1.63 | 1.67 | 0.96 | 42.9 ms | 0.83 | 0.84 | 0.79 | 3.5 ms | 0.90 | 0.91 |
| Q01 | 4 | 2.41 | 8.6 ms | 1.85 | 2.02 | 1.78 | 99.3 ms | 0.85 | 0.86 | 1.39 | 4.5 ms | 0.89 | 0.90 |
| Q01 | 8 | 4.04 | 9.5 ms | 2.21 | 2.36 | 1.99 | 118.3 ms | 0.87 | 0.87 | 1.45 | 4.9 ms | 0.89 | 0.90 |
| Q01 | 32 | 5.69 | 10.6 ms | 2.67 | 2.83 | 1.92 | 128.0 ms | 0.88 | 0.89 | 1.43 | 5.1 ms | 0.89 | 0.90 |
| Q02 | 1 | 1.00 | 393.9 ms | 2.80 | 2.80 | 2.19 | 419.7 ms | 0.89 | 0.89 | 0.94 | 7.3 ms | 0.91 | 0.91 |
| Q02 | 4 | 3.97 | 424.9 ms | 2.81 | 2.82 | 5.04 | 507.8 ms | 0.90 | 0.92 | 2.05 | 8.4 ms | 0.91 | 0.91 |
| Q02 | 8 | 7.70 | 496.4 ms | 2.81 | 2.82 | 5.10 | 555.2 ms | 0.91 | 0.93 | 2.19 | 8.9 ms | 0.91 | 0.92 |
| Q02 | 32 | 7.90 | 504.3 ms | 2.78 | 2.80 | 4.98 | 575.0 ms | 0.90 | 0.91 | 2.10 | 9.4 ms | 0.91 | 0.92 |
| Q03 | 1 | 0.87 | 20.9 ms | 2.71 | 2.72 | 1.22 | 107.2 ms | 0.89 | 0.89 | 0.90 | 5.9 ms | 0.92 | 0.92 |
| Q03 | 4 | 3.16 | 23.3 ms | 2.72 | 2.75 | 1.92 | 161.3 ms | 0.89 | 0.90 | 1.83 | 6.8 ms | 0.92 | 0.93 |
| Q03 | 8 | 5.22 | 25.6 ms | 2.90 | 3.04 | 2.13 | 186.1 ms | 0.90 | 0.91 | 1.89 | 7.2 ms | 0.91 | 0.92 |
| Q03 | 32 | 6.61 | 27.6 ms | 3.22 | 3.34 | 2.13 | 197.1 ms | 0.91 | 0.92 | 1.83 | 7.7 ms | 0.92 | 0.93 |
| Q04 | 1 | 0.83 | 14.5 ms | 3.32 | 3.34 | 0.99 | 83.3 ms | 0.90 | 0.90 | 0.99 | 10.3 ms | 0.92 | 0.93 |
| Q04 | 4 | 2.90 | 18.3 ms | 3.40 | 3.43 | 1.58 | 134.6 ms | 0.91 | 0.92 | 2.43 | 11.3 ms | 0.91 | 0.92 |
| Q04 | 8 | 4.69 | 20.1 ms | 3.54 | 3.66 | 1.85 | 158.6 ms | 0.92 | 0.92 | 2.59 | 11.8 ms | 0.92 | 0.92 |
| Q04 | 32 | 6.19 | 21.7 ms | 3.78 | 3.86 | 1.85 | 171.2 ms | 0.92 | 0.93 | 2.49 | 12.3 ms | 0.92 | 0.92 |
| Q05 | 1 | 1.00 | 415.8 ms | 3.82 | 3.82 | 1.04 | 592.3 ms | 0.94 | 0.94 | 0.82 | 4.4 ms | 0.92 | 0.92 |
| Q05 | 4 | 3.97 | 440.2 ms | 3.83 | 3.83 | 3.92 | 676.4 ms | 1.00 | 1.02 | 1.58 | 5.3 ms | 0.92 | 0.93 |
| Q05 | 8 | 5.94 | 517.3 ms | 3.83 | 3.85 | 4.35 | 787.4 ms | 1.00 | 1.10 | 1.62 | 6.1 ms | 0.93 | 0.93 |
| Q05 | 32 | 7.94 | 542.4 ms | 3.81 | 3.82 | 6.40 | 845.2 ms | 1.06 | 1.13 | 1.60 | 6.2 ms | 0.93 | 0.94 |
| Q06 | 1 | 1.00 | 411.9 ms | 3.71 | 3.72 | 1.04 | 596.3 ms | 0.94 | 0.95 | 0.97 | 6.5 ms | 0.93 | 0.94 |
| Q06 | 4 | 3.97 | 452.7 ms | 3.72 | 3.73 | 3.90 | 672.5 ms | 1.00 | 1.03 | 1.79 | 7.6 ms | 0.92 | 0.94 |
| Q06 | 8 | 7.67 | 526.1 ms | 3.71 | 3.73 | 5.94 | 789.1 ms | 1.04 | 1.11 | 1.84 | 8.1 ms | 0.93 | 0.94 |
| Q06 | 32 | 7.87 | 535.0 ms | 3.68 | 3.69 | 6.24 | 841.9 ms | 1.05 | 1.14 | 1.78 | 8.5 ms | 0.93 | 0.94 |
| Q07 | 1 | 1.00 | 284.1 ms | 3.59 | 3.63 | 1.03 | 611.9 ms | 0.94 | 0.95 | 0.87 | 5.2 ms | 0.93 | 0.94 |
| Q07 | 4 | 3.95 | 326.8 ms | 3.60 | 3.61 | 3.89 | 708.6 ms | 1.00 | 1.03 | 1.67 | 6.0 ms | 0.93 | 0.94 |
| Q07 | 8 | 7.49 | 365.5 ms | 3.61 | 3.63 | 6.02 | 835.8 ms | 1.05 | 1.13 | 1.73 | 6.4 ms | 0.94 | 0.94 |
| Q07 | 32 | 7.89 | 370.9 ms | 3.62 | 3.64 | 6.33 | 877.0 ms | 1.06 | 1.14 | 1.67 | 7.0 ms | 0.94 | 0.94 |
| Q10 | 1 | 0.89 | 28.6 ms | 3.65 | 3.69 | 0.99 | 95.2 ms | 0.93 | 0.93 | 1.17 | 16.0 ms | 0.94 | 0.94 |
| Q10 | 4 | 3.11 | 34.6 ms | 3.73 | 3.77 | 1.58 | 145.8 ms | 0.94 | 0.94 | 2.46 | 17.3 ms | 0.94 | 0.94 |
| Q10 | 8 | 5.11 | 37.9 ms | 3.84 | 3.87 | 1.76 | 171.8 ms | 0.95 | 0.96 | 2.48 | 17.5 ms | 0.95 | 0.96 |
| Q10 | 32 | 5.89 | 40.4 ms | 3.90 | 3.94 | 1.86 | 186.0 ms | 0.95 | 0.96 | 2.39 | 17.9 ms | 0.96 | 0.97 |
| Q11 | 1 | 1.02 | 218.4 ms | 3.89 | 3.90 | 0.99 | 256.1 ms | 0.99 | 1.00 | 1.19 | 114.8 ms | 0.97 | 0.97 |
| Q11 | 4 | 3.79 | 253.5 ms | 3.90 | 3.91 | 1.34 | 321.6 ms | 1.05 | 1.07 | 2.19 | 131.3 ms | 0.98 | 0.99 |
| Q11 | 8 | 6.04 | 282.9 ms | 3.90 | 3.94 | 1.54 | 348.6 ms | 1.13 | 1.16 | 2.27 | 130.3 ms | 1.01 | 1.03 |
| Q11 | 32 | 6.23 | 288.3 ms | 3.91 | 3.95 | 1.63 | 357.4 ms | 1.21 | 1.26 | 2.07 | 132.1 ms | 1.09 | 1.12 |
| Q12 | 1 | 1.00 | 411.5 ms | 3.81 | 3.82 | 1.03 | 591.9 ms | 1.16 | 1.17 | 0.81 | 4.2 ms | 1.01 | 1.01 |
| Q12 | 4 | 3.97 | 470.4 ms | 3.82 | 3.83 | 3.93 | 674.0 ms | 1.21 | 1.24 | 1.55 | 5.2 ms | 1.01 | 1.02 |
| Q12 | 8 | 7.74 | 529.8 ms | 3.81 | 3.83 | 6.07 | 794.2 ms | 1.24 | 1.32 | 1.62 | 5.6 ms | 1.01 | 1.02 |
| Q12 | 32 | 7.95 | 543.3 ms | 3.80 | 3.80 | 6.41 | 845.6 ms | 1.24 | 1.32 | 1.58 | 6.0 ms | 1.01 | 1.02 |
| Q13 | 1 | 1.00 | 365.3 ms | 3.74 | 3.75 | 1.16 | 419.7 ms | 1.11 | 1.12 | 2.76 | 323.2 ms | 1.03 | 1.04 |
| Q13 | 4 | 3.95 | 404.0 ms | 3.76 | 3.76 | 4.07 | 484.7 ms | 1.12 | 1.13 | 7.54 | 384.5 ms | 1.04 | 1.05 |
| Q13 | 8 | 7.70 | 455.2 ms | 3.76 | 3.77 | 5.36 | 565.0 ms | 1.13 | 1.15 | 7.96 | 385.4 ms | 1.07 | 1.10 |
| Q13 | 32 | 7.93 | 461.9 ms | 3.78 | 3.78 | 5.39 | 591.8 ms | 1.14 | 1.15 | 7.96 | 388.6 ms | 1.07 | 1.09 |
| mix | 1 | 1.01 | 252.5 ms | 1.42 | 1.43 | 1.14 | 363.6 ms | 0.82 | 0.83 | 0.92 | 6.7 ms | 0.86 | 0.86 |
| mix | 4 | 3.98 | 279.5 ms | 1.46 | 1.47 | 3.85 | 441.7 ms | 0.87 | 0.92 | 1.93 | 7.7 ms | 0.86 | 0.87 |
| mix | 8 | 7.53 | 317.4 ms | 1.55 | 1.57 | 4.91 | 520.2 ms | 0.89 | 1.00 | 1.99 | 8.1 ms | 0.87 | 0.87 |
| mix | 32 | 7.84 | 323.6 ms | 1.59 | 1.61 | 4.91 | 548.0 ms | 0.91 | 0.99 | 1.91 | 8.6 ms | 0.91 | 0.92 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | argus-final | — | 4.1 | 1.00 | 4.1 | 244.3 |
| csv | 1 | dachs-final | — | 3.1 | 1.15 | 2.7 | 374.8 |
| csv | 1 | egernia-skycell-w1 | 1 | 150.1 | 0.91 | 164.4 | 6.1 |
| csv | 4 | argus-final | — | 15.4 | 3.94 | 3.9 | 256.9 |
| csv | 4 | dachs-final | — | 8.6 | 3.81 | 2.3 | 443.2 |
| csv | 4 | egernia-skycell-w1 | 1 | 259.7 | 1.85 | 140.1 | 7.1 |
| csv | 8 | argus-final | — | 24.0 | 7.55 | 3.2 | 316.5 |
| csv | 8 | dachs-final | — | 9.4 | 4.80 | 2.0 | 515.1 |
| csv | 8 | egernia-skycell-w1 | 1 | 254.9 | 1.92 | 132.7 | 7.5 |
| csv | 32 | argus-final | — | 24.8 | 7.87 | 3.2 | 319.6 |
| csv | 32 | dachs-final | — | 9.0 | 4.80 | 1.9 | 541.3 |
| csv | 32 | egernia-skycell-w1 | 1 | 231.3 | 1.85 | 125.1 | 8.0 |
| votable | 1 | argus-final | — | 4.0 | 1.01 | 4.0 | 252.5 |
| votable | 1 | dachs-final | — | 3.1 | 1.14 | 2.8 | 363.6 |
| votable | 1 | egernia-skycell-w1 | 1 | 138.5 | 0.92 | 150.1 | 6.7 |
| votable | 4 | argus-final | — | 14.3 | 3.98 | 3.6 | 279.5 |
| votable | 4 | dachs-final | — | 8.8 | 3.85 | 2.3 | 441.7 |
| votable | 4 | egernia-skycell-w1 | 1 | 250.7 | 1.93 | 130.0 | 7.7 |
| votable | 8 | argus-final | — | 23.8 | 7.53 | 3.2 | 317.4 |
| votable | 8 | dachs-final | — | 9.5 | 4.91 | 1.9 | 520.2 |
| votable | 8 | egernia-skycell-w1 | 1 | 245.5 | 1.99 | 123.5 | 8.1 |
| votable | 32 | argus-final | — | 24.4 | 7.84 | 3.1 | 323.6 |
| votable | 32 | dachs-final | — | 9.1 | 4.91 | 1.8 | 548.0 |
| votable | 32 | egernia-skycell-w1 | 1 | 223.2 | 1.91 | 116.8 | 8.6 |

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
docker compose -f benchmarks/tap-compare/docker-compose.argus.yml \
    -f benchmarks/tap-compare/final/pins/argus.yml up -d --build
docker compose -f benchmarks/tap-compare/docker-compose.dachs.yml \
    -f benchmarks/tap-compare/final/pins/dachs.yml up -d
docker compose -f docker-compose.yml \
    -f benchmarks/tap-compare/final-skycell/pins/egernia-w1.yml \
    -f benchmarks/tap-compare/final-skycell/pins/skycell.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets argus-final dachs-final egernia-skycell-w1 --scenario <scenario>
```

Environment: see `environment.json` (git d360fb1e, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Phase A of experiment 2 of the pre-registered skycell rerun (`benchmarks/tap-compare/final-skycell/PROTOCOL.md`): **Table A, one-process parity**, the final three-way comparison (`final/PROTOCOL.md`) measured again with egernia on the skycell geometry backend. egernia with one uvicorn worker against GAVO DaCHS and CADC argus, all three up at once on disjoint cpusets (egernia 0-7, argus 8-15, DaCHS 16-23, generator 24-29), interleaved inside every cell. It replaces `20260911T065452Z-41bfc513-tap-compare`, which measured egernia on pg_sphere 165 commits earlier.
- **Provenance.** Pre-registered at tag `tap-compare-final-skycell-prereg-v1`, amended before measurement at `-v2`; measured at `d360fb1e`. skycell v0.58 (commit `0d998bd`, extension 0.50). The opponents are rebuilt from the same Dockerfiles as the published runs': DaCHS is `gavodachs2-server 2.11+dfsg-2`, argus is 1.0.27 at the same digest pin.
- **Gates.** All three `taplint` PASS: egernia 0 errors, DaCHS 0, argus 0 blocking / 2 total (the TAP_UPLOAD-by-URL stage). **Three-way agreement 11/11 classes.**
- **Verdicts: egernia 75, ties 10, argus 11, DaCHS 0, of 96 cells** (the published Table A was 66 / 12 / 18 / 0). 864 rungs, 19.8 h (2026-11-17 20:39Z to 11-18 16:29Z), 4,710,657 requests, generator peak 0.514.
- **Where argus wins**: Q01 from c=8 (527.5 rps against egernia's 284.1 at c=32, CSV), Q04 at c=32, Q10 CSV at c=32, Q11 from c=8. Everything else is egernia's or a tie. **Q13 is now egernia's in 8 of 8 cells** (20.6 rps against 17.4 at c=32, CSV); it tied at c ≥ 8 in the published table.
- **H3′ holds**: egernia wins every cell of Q05, Q06, Q07, Q12 and the mix, 40 of 40.
- **H4 fails, narrowly.** egernia shed load in two rungs, both Q11 at c=32, repetition 2: nine 503s each, 0.8% in CSV and **1.4% in VOTable, the one rung of this run above the 1% ceiling**. argus leads that cell on throughput in any case (21.7 rps against 15.9).
- **H5 holds**: DaCHS's c=8 and c=32 cells tie in every class but Q01 in VOTable; argus's c=32 beats its c=1 in 12 of 12 classes in both formats.
- **Against the published Table A, the opponents did not move.** By the tie rule DaCHS ties its published cell in **96 of 96** and argus in **95 of 96**, two months and a container rebuild apart. egernia is higher in 87 of 96 cells, by 33-46% at c=32 on every class but two: Q13 (+15%) and **Q11, which is lower (0.89× in CSV, 0.82× in VOTable)**. Experiment 1 (`20261117T003742Z-d360fb1e-tap-compare`) shows the backend is not the cause of either: the gain and the Q11 loss both come from the other commits since `1845521`. The Q11 loss is not explained here.
- **Resources.** Mixed workload, c=32, CSV: egernia 231.3 rps on 1.85 cores at **8.0 ms of CPU per request**; argus 24.8 rps on 7.87 cores at 319.6 ms; DaCHS 9.0 rps on 4.80 cores at 541.3 ms.
- **One noisy cell.** Q05 in VOTable at c=8 measured DaCHS at 5.6 rps and argus at 11.4, against 8.0 and 14.8 in the scaling run's tier 8. Both tie by the rule because the interval is wide; egernia wins the cell either way.
- **DaCHS ran as root here**, as its image starts it, and did not fail. Amendments 2 and 3 of the protocol describe the DaCHS 2.11 defect that stopped phase B; nothing in a measured request's path differs between the two users.

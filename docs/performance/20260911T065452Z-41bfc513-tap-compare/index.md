# 20260911T065452Z-41bfc513-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: argus in `benchmarks/tap-compare/docker-compose.argus.yml` + `final/pins/argus.yml` (`cpuset` 8-15; 8 GiB split 3 Tomcat / 5 PostgreSQL; `benchmarks/tap-compare/final/PROTOCOL.md`); DaCHS in `benchmarks/tap-compare/docker-compose.dachs.yml` + `final/pins/dachs.yml` (`cpus: 8`, `cpuset` 16-23, `mem_limit: 8g`, its PostgreSQL sized to the container by the ¼ rule; `benchmarks/tap-compare/final/PROTOCOL.md`); egernia in `benchmarks/tap-compare/final/pins/egernia-w1.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=1`; `benchmarks/tap-compare/final/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-final | 1.1 | PASS (2 errors) | 134217728 |
| dachs-final | 1.1 | PASS (0 errors) | 20000 |
| egernia-final-w1 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-final-w1 rps | egernia-final-w1 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 93.6 ±2.8 | 0.012 ±0.000 | 23.4 ±0.5 | 0.158 ±0.005 | 189.3 ±1.8 | 0.006 ±0.000 | egernia-final-w1 |
| Q01 | 4 | 254.5 ±66.2 | 0.016 ±0.000 | 18.7 ±0.6 | 0.328 ±0.007 | 219.6 ±1.7 | 0.023 ±0.000 | tie |
| Q01 | 8 | 437.5 ±19.1 | 0.022 ±0.000 | 17.5 ±0.2 | 0.559 ±0.022 | 209.5 ±2.2 | 0.050 ±0.000 | argus-final |
| Q01 | 32 | 545.1 ±63.2 | 0.065 ±0.001 | 16.1 ±0.2 | 2.151 ±0.054 | 194.3 ±0.3 | 0.187 ±0.002 | argus-final |
| Q02 | 1 | 2.6 ±0.0 | 0.394 ±0.005 | 5.4 ±0.3 | 0.299 ±0.022 | 124.3 ±1.2 | 0.009 ±0.000 | egernia-final-w1 |
| Q02 | 4 | 9.0 ±0.6 | 0.490 ±0.001 | 10.4 ±0.1 | 0.527 ±0.008 | 194.2 ±2.5 | 0.026 ±0.000 | egernia-final-w1 |
| Q02 | 8 | 16.0 ±0.1 | 0.532 ±0.015 | 9.5 ±0.1 | 1.043 ±0.027 | 186.8 ±0.5 | 0.055 ±0.000 | egernia-final-w1 |
| Q02 | 32 | 16.1 ±0.1 | 2.055 ±0.021 | 9.0 ±0.3 | 3.853 ±0.381 | 168.7 ±0.3 | 0.215 ±0.001 | egernia-final-w1 |
| Q03 | 1 | 42.2 ±1.6 | 0.080 ±0.001 | 12.0 ±0.3 | 0.193 ±0.005 | 137.4 ±0.7 | 0.008 ±0.000 | egernia-final-w1 |
| Q03 | 4 | 138.3 ±0.9 | 0.093 ±0.001 | 12.5 ±0.1 | 0.457 ±0.021 | 204.3 ±1.1 | 0.025 ±0.000 | egernia-final-w1 |
| Q03 | 8 | 208.2 ±7.6 | 0.115 ±0.001 | 12.1 ±0.0 | 0.812 ±0.012 | 193.2 ±1.1 | 0.054 ±0.000 | tie |
| Q03 | 32 | 256.1 ±4.3 | 0.236 ±0.004 | 10.9 ±2.5 | 3.677 ±2.978 | 175.3 ±0.2 | 0.207 ±0.001 | argus-final |
| Q04 | 1 | 55.8 ±6.2 | 0.020 ±0.001 | 12.7 ±0.2 | 0.198 ±0.002 | 89.9 ±1.0 | 0.012 ±0.000 | egernia-final-w1 |
| Q04 | 4 | 163.7 ±1.1 | 0.029 ±0.000 | 12.7 ±0.2 | 0.448 ±0.015 | 171.7 ±0.3 | 0.029 ±0.000 | tie |
| Q04 | 8 | 222.8 ±55.4 | 0.041 ±0.003 | 11.9 ±0.5 | 0.818 ±0.025 | 169.7 ±8.8 | 0.060 ±0.004 | tie |
| Q04 | 32 | 298.9 ±7.3 | 0.124 ±0.002 | 11.3 ±0.2 | 3.052 ±0.115 | 152.3 ±3.9 | 0.240 ±0.005 | argus-final |
| Q05 | 1 | 2.5 ±0.0 | 0.407 ±0.006 | 1.8 ±0.0 | 0.651 ±0.012 | 159.8 ±7.4 | 0.007 ±0.000 | egernia-final-w1 |
| Q05 | 4 | 9.0 ±1.8 | 0.505 ±0.199 | 6.1 ±0.1 | 0.814 ±0.024 | 212.3 ±1.7 | 0.024 ±0.000 | egernia-final-w1 |
| Q05 | 8 | 14.5 ±0.2 | 0.584 ±0.005 | 8.0 ±0.1 | 1.264 ±0.003 | 203.0 ±0.4 | 0.051 ±0.000 | egernia-final-w1 |
| Q05 | 32 | 14.5 ±0.1 | 2.297 ±0.026 | 8.2 ±0.2 | 4.173 ±0.067 | 185.1 ±1.2 | 0.195 ±0.002 | egernia-final-w1 |
| Q06 | 1 | 2.5 ±0.1 | 0.416 ±0.007 | 1.8 ±0.0 | 0.654 ±0.007 | 138.2 ±3.0 | 0.009 ±0.000 | egernia-final-w1 |
| Q06 | 4 | 9.1 ±1.7 | 0.508 ±0.197 | 6.0 ±0.3 | 0.834 ±0.041 | 181.6 ±1.6 | 0.028 ±0.001 | egernia-final-w1 |
| Q06 | 8 | 14.4 ±0.0 | 0.596 ±0.008 | 7.9 ±0.2 | 1.256 ±0.022 | 174.2 ±0.2 | 0.059 ±0.001 | egernia-final-w1 |
| Q06 | 32 | 14.6 ±0.3 | 2.299 ±0.018 | 8.0 ±0.3 | 4.326 ±0.179 | 159.7 ±0.4 | 0.229 ±0.002 | egernia-final-w1 |
| Q07 | 1 | 3.4 ±0.2 | 0.409 ±0.011 | 1.7 ±0.0 | 0.692 ±0.033 | 150.4 ±2.3 | 0.008 ±0.000 | egernia-final-w1 |
| Q07 | 4 | 12.6 ±2.0 | 0.469 ±0.125 | 5.6 ±0.2 | 0.883 ±0.031 | 206.8 ±0.7 | 0.025 ±0.000 | egernia-final-w1 |
| Q07 | 8 | 20.6 ±0.1 | 0.550 ±0.010 | 7.6 ±0.1 | 1.316 ±0.057 | 196.4 ±0.4 | 0.053 ±0.000 | egernia-final-w1 |
| Q07 | 32 | 21.2 ±0.2 | 1.747 ±0.030 | 7.7 ±0.1 | 4.435 ±0.031 | 178.1 ±0.7 | 0.204 ±0.003 | egernia-final-w1 |
| Q10 | 1 | 37.9 ±1.5 | 0.029 ±0.002 | 10.8 ±0.0 | 0.212 ±0.001 | 75.7 ±1.1 | 0.016 ±0.000 | egernia-final-w1 |
| Q10 | 4 | 97.1 ±18.4 | 0.044 ±0.000 | 11.2 ±0.1 | 0.497 ±0.006 | 115.2 ±0.4 | 0.043 ±0.000 | tie |
| Q10 | 8 | 154.4 ±27.5 | 0.062 ±0.002 | 10.7 ±0.1 | 0.909 ±0.025 | 112.9 ±0.9 | 0.090 ±0.001 | argus-final |
| Q10 | 32 | 173.7 ±17.8 | 0.201 ±0.001 | 10.2 ±0.1 | 3.324 ±0.142 | 106.6 ±0.5 | 0.351 ±0.003 | argus-final |
| Q11 | 1 | 6.0 ±0.0 | 0.173 ±0.005 | 3.6 ±0.1 | 0.397 ±0.007 | 13.9 ±3.8 | 0.080 ±0.006 | egernia-final-w1 |
| Q11 | 4 | 19.2 ±0.2 | 0.232 ±0.002 | 4.0 ±0.0 | 1.247 ±0.118 | 19.3 ±1.1 | 0.309 ±0.015 | tie |
| Q11 | 8 | 27.5 ±0.2 | 0.335 ±0.005 | 4.0 ±0.0 | 2.553 ±0.123 | 21.4 ±0.3 | 0.462 ±0.040 | argus-final |
| Q11 | 32 | 28.2 ±0.1 | 1.212 ±0.011 | 4.2 ±0.1 | 11.732 ±2.321 | 22.1 ±0.5 | 1.825 ±0.292 | argus-final |
| Q12 | 1 | 2.5 ±0.0 | 0.412 ±0.009 | 1.9 ±0.0 | 0.653 ±0.002 | 168.0 ±2.5 | 0.007 ±0.000 | egernia-final-w1 |
| Q12 | 4 | 9.7 ±0.4 | 0.449 ±0.133 | 6.1 ±0.1 | 0.822 ±0.026 | 215.8 ±0.4 | 0.023 ±0.000 | egernia-final-w1 |
| Q12 | 8 | 14.7 ±0.4 | 0.578 ±0.007 | 8.0 ±0.1 | 1.245 ±0.071 | 206.1 ±1.6 | 0.050 ±0.000 | egernia-final-w1 |
| Q12 | 32 | 14.5 ±0.1 | 2.282 ±0.009 | 8.1 ±0.1 | 4.143 ±0.083 | 187.8 ±0.9 | 0.193 ±0.000 | egernia-final-w1 |
| Q13 | 1 | 2.8 ±0.0 | 0.401 ±0.011 | 2.9 ±0.3 | 0.473 ±0.068 | 7.6 ±0.1 | 0.174 ±0.006 | egernia-final-w1 |
| Q13 | 4 | 11.1 ±0.7 | 0.425 ±0.105 | 8.8 ±0.3 | 0.685 ±0.051 | 17.2 ±0.1 | 0.307 ±0.010 | egernia-final-w1 |
| Q13 | 8 | 17.3 ±0.3 | 0.552 ±0.002 | 10.0 ±0.2 | 1.109 ±0.050 | 17.9 ±0.1 | 0.599 ±0.012 | tie |
| Q13 | 32 | 17.7 ±0.2 | 1.969 ±0.048 | 9.6 ±0.2 | 3.652 ±0.039 | 17.8 ±0.1 | 2.001 ±0.034 | tie |
| mix | 1 | 4.1 ±0.5 | 0.412 ±0.008 | 3.2 ±0.3 | 0.612 ±0.058 | 129.7 ±0.5 | 0.012 ±0.000 | egernia-final-w1 |
| mix | 4 | 14.8 ±1.9 | 0.521 ±0.054 | 9.0 ±0.3 | 0.855 ±0.028 | 191.6 ±0.9 | 0.029 ±0.000 | egernia-final-w1 |
| mix | 8 | 23.9 ±1.2 | 0.577 ±0.007 | 9.6 ±0.6 | 1.296 ±0.043 | 183.5 ±0.6 | 0.058 ±0.001 | egernia-final-w1 |
| mix | 32 | 24.6 ±1.2 | 1.712 ±0.084 | 9.2 ±0.2 | 4.006 ±0.126 | 167.7 ±0.8 | 0.221 ±0.004 | egernia-final-w1 |

## votable

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-final-w1 rps | egernia-final-w1 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 95.4 ±0.7 | 0.012 ±0.000 | 22.8 ±0.3 | 0.129 ±0.011 | 187.1 ±3.5 | 0.006 ±0.000 | egernia-final-w1 |
| Q01 | 4 | 274.4 ±43.8 | 0.016 ±0.000 | 18.3 ±0.2 | 0.322 ±0.011 | 218.1 ±3.2 | 0.023 ±0.000 | argus-final |
| Q01 | 8 | 419.5 ±54.6 | 0.022 ±0.000 | 17.2 ±0.3 | 0.572 ±0.016 | 207.8 ±0.3 | 0.050 ±0.000 | argus-final |
| Q01 | 32 | 542.2 ±49.8 | 0.065 ±0.002 | 15.6 ±0.1 | 2.196 ±0.009 | 192.1 ±1.2 | 0.189 ±0.002 | argus-final |
| Q02 | 1 | 2.6 ±0.1 | 0.391 ±0.012 | 5.4 ±0.2 | 0.296 ±0.004 | 118.1 ±1.5 | 0.010 ±0.000 | egernia-final-w1 |
| Q02 | 4 | 9.2 ±0.3 | 0.490 ±0.005 | 10.0 ±0.2 | 0.544 ±0.032 | 189.9 ±1.2 | 0.027 ±0.000 | egernia-final-w1 |
| Q02 | 8 | 15.9 ±0.1 | 0.530 ±0.012 | 9.4 ±0.2 | 1.044 ±0.032 | 182.6 ±0.6 | 0.057 ±0.000 | egernia-final-w1 |
| Q02 | 32 | 16.1 ±0.0 | 2.067 ±0.010 | 8.9 ±0.3 | 3.818 ±0.045 | 165.8 ±1.0 | 0.219 ±0.003 | egernia-final-w1 |
| Q03 | 1 | 41.2 ±1.1 | 0.080 ±0.000 | 11.5 ±0.2 | 0.198 ±0.001 | 131.6 ±0.8 | 0.009 ±0.000 | egernia-final-w1 |
| Q03 | 4 | 134.3 ±0.4 | 0.094 ±0.001 | 12.2 ±0.1 | 0.476 ±0.020 | 200.3 ±2.3 | 0.025 ±0.000 | egernia-final-w1 |
| Q03 | 8 | 202.0 ±3.3 | 0.115 ±0.001 | 11.8 ±0.3 | 0.839 ±0.041 | 189.3 ±0.4 | 0.054 ±0.000 | tie |
| Q03 | 32 | 246.7 ±2.3 | 0.240 ±0.003 | 11.2 ±0.2 | 3.050 ±0.060 | 172.2 ±0.4 | 0.211 ±0.001 | argus-final |
| Q04 | 1 | 51.0 ±2.7 | 0.022 ±0.001 | 12.2 ±0.1 | 0.201 ±0.003 | 84.5 ±0.9 | 0.013 ±0.000 | egernia-final-w1 |
| Q04 | 4 | 154.5 ±0.9 | 0.031 ±0.000 | 12.4 ±0.4 | 0.445 ±0.012 | 162.6 ±6.0 | 0.030 ±0.001 | tie |
| Q04 | 8 | 230.2 ±3.9 | 0.043 ±0.000 | 11.9 ±0.1 | 0.823 ±0.011 | 161.4 ±1.3 | 0.063 ±0.000 | argus-final |
| Q04 | 32 | 282.9 ±6.1 | 0.130 ±0.002 | 11.4 ±0.2 | 3.001 ±0.033 | 148.8 ±0.4 | 0.246 ±0.002 | argus-final |
| Q05 | 1 | 2.5 ±0.0 | 0.406 ±0.004 | 1.8 ±0.0 | 0.659 ±0.002 | 158.7 ±2.3 | 0.007 ±0.000 | egernia-final-w1 |
| Q05 | 4 | 8.5 ±0.0 | 0.552 ±0.001 | 6.0 ±0.1 | 0.833 ±0.041 | 210.6 ±3.2 | 0.024 ±0.001 | egernia-final-w1 |
| Q05 | 8 | 14.4 ±0.1 | 0.586 ±0.013 | 7.9 ±0.2 | 1.270 ±0.007 | 200.3 ±1.6 | 0.052 ±0.001 | egernia-final-w1 |
| Q05 | 32 | 14.3 ±0.7 | 2.490 ±0.824 | 8.0 ±0.2 | 4.273 ±0.130 | 181.6 ±0.7 | 0.200 ±0.002 | egernia-final-w1 |
| Q06 | 1 | 2.5 ±0.1 | 0.410 ±0.001 | 1.8 ±0.0 | 0.662 ±0.014 | 128.1 ±2.0 | 0.010 ±0.000 | egernia-final-w1 |
| Q06 | 4 | 9.3 ±1.6 | 0.509 ±0.190 | 6.0 ±0.1 | 0.837 ±0.043 | 176.0 ±0.4 | 0.029 ±0.000 | egernia-final-w1 |
| Q06 | 8 | 14.4 ±0.2 | 0.598 ±0.013 | 7.7 ±0.1 | 1.303 ±0.043 | 167.7 ±1.5 | 0.062 ±0.000 | egernia-final-w1 |
| Q06 | 32 | 14.5 ±0.1 | 2.312 ±0.022 | 7.9 ±0.2 | 4.372 ±0.097 | 154.8 ±0.9 | 0.238 ±0.001 | egernia-final-w1 |
| Q07 | 1 | 3.5 ±0.1 | 0.410 ±0.016 | 1.7 ±0.0 | 0.695 ±0.022 | 144.0 ±0.6 | 0.008 ±0.000 | egernia-final-w1 |
| Q07 | 4 | 12.6 ±1.9 | 0.468 ±0.122 | 5.5 ±0.5 | 0.941 ±0.247 | 202.3 ±0.5 | 0.025 ±0.000 | egernia-final-w1 |
| Q07 | 8 | 20.6 ±0.1 | 0.551 ±0.009 | 7.5 ±0.1 | 1.318 ±0.052 | 192.4 ±0.5 | 0.054 ±0.001 | egernia-final-w1 |
| Q07 | 32 | 21.2 ±0.0 | 1.751 ±0.016 | 7.6 ±0.1 | 4.496 ±0.061 | 175.1 ±1.1 | 0.208 ±0.003 | egernia-final-w1 |
| Q10 | 1 | 30.8 ±0.6 | 0.036 ±0.001 | 10.6 ±0.1 | 0.216 ±0.005 | 63.9 ±2.2 | 0.019 ±0.000 | egernia-final-w1 |
| Q10 | 4 | 89.8 ±9.3 | 0.051 ±0.001 | 11.1 ±0.1 | 0.493 ±0.015 | 105.9 ±1.7 | 0.046 ±0.001 | egernia-final-w1 |
| Q10 | 8 | 134.0 ±11.8 | 0.073 ±0.001 | 10.8 ±0.2 | 0.902 ±0.006 | 104.3 ±0.5 | 0.097 ±0.002 | argus-final |
| Q10 | 32 | 150.0 ±0.8 | 0.241 ±0.003 | 10.3 ±0.2 | 3.309 ±0.078 | 99.2 ±0.8 | 0.381 ±0.005 | argus-final |
| Q11 | 1 | 4.8 ±0.0 | 0.217 ±0.004 | 3.9 ±0.0 | 0.376 ±0.006 | 11.5 ±0.1 | 0.106 ±0.004 | egernia-final-w1 |
| Q11 | 4 | 15.0 ±0.1 | 0.302 ±0.004 | 4.4 ±0.1 | 1.091 ±0.079 | 17.4 ±0.7 | 0.330 ±0.058 | egernia-final-w1 |
| Q11 | 8 | 21.7 ±0.2 | 0.426 ±0.010 | 4.5 ±0.1 | 2.294 ±0.167 | 18.5 ±0.3 | 0.546 ±0.022 | argus-final |
| Q11 | 32 | 21.9 ±0.2 | 1.551 ±0.006 | 4.7 ±0.1 | 10.145 ±1.787 | 19.4 ±0.2 | 1.965 ±0.019 | argus-final |
| Q12 | 1 | 2.5 ±0.0 | 0.412 ±0.003 | 1.8 ±0.0 | 0.654 ±0.001 | 162.0 ±1.9 | 0.007 ±0.000 | egernia-final-w1 |
| Q12 | 4 | 9.2 ±1.2 | 0.536 ±0.040 | 6.0 ±0.1 | 0.827 ±0.013 | 211.9 ±1.7 | 0.024 ±0.000 | egernia-final-w1 |
| Q12 | 8 | 14.5 ±0.2 | 0.580 ±0.005 | 7.8 ±0.2 | 1.279 ±0.099 | 202.1 ±0.4 | 0.051 ±0.000 | egernia-final-w1 |
| Q12 | 32 | 14.6 ±0.0 | 2.284 ±0.022 | 8.1 ±0.0 | 4.256 ±0.041 | 184.1 ±0.8 | 0.197 ±0.002 | egernia-final-w1 |
| Q13 | 1 | 2.8 ±0.1 | 0.397 ±0.005 | 2.9 ±0.2 | 0.484 ±0.061 | 7.6 ±0.2 | 0.176 ±0.003 | egernia-final-w1 |
| Q13 | 4 | 10.5 ±0.8 | 0.482 ±0.034 | 8.7 ±0.1 | 0.687 ±0.022 | 17.0 ±0.1 | 0.312 ±0.005 | egernia-final-w1 |
| Q13 | 8 | 17.3 ±0.1 | 0.552 ±0.008 | 9.9 ±0.2 | 1.106 ±0.043 | 17.8 ±0.4 | 0.598 ±0.013 | tie |
| Q13 | 32 | 17.7 ±0.2 | 1.972 ±0.050 | 9.5 ±0.2 | 3.674 ±0.040 | 17.8 ±0.3 | 2.011 ±0.039 | tie |
| mix | 1 | 4.1 ±0.5 | 0.412 ±0.003 | 3.2 ±0.2 | 0.585 ±0.007 | 122.9 ±0.9 | 0.014 ±0.000 | egernia-final-w1 |
| mix | 4 | 14.7 ±0.3 | 0.516 ±0.068 | 9.0 ±0.4 | 0.838 ±0.048 | 185.7 ±0.8 | 0.030 ±0.000 | egernia-final-w1 |
| mix | 8 | 23.6 ±0.9 | 0.585 ±0.004 | 9.8 ±0.2 | 1.266 ±0.009 | 178.2 ±0.7 | 0.061 ±0.000 | egernia-final-w1 |
| mix | 32 | 24.5 ±1.1 | 1.711 ±0.103 | 9.3 ±0.4 | 3.974 ±0.039 | 163.3 ±0.3 | 0.230 ±0.002 | egernia-final-w1 |

## resources, csv

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-final-w1 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.66 | 7.1 ms | 3.58 | 3.64 | 0.96 | 40.8 ms | 1.14 | 1.15 | 0.87 | 4.6 ms | 1.09 | 1.11 |
| Q01 | 4 | 2.08 | 8.2 ms | 3.87 | 4.06 | 1.77 | 94.6 ms | 1.15 | 1.15 | 1.42 | 6.5 ms | 1.07 | 1.08 |
| Q01 | 8 | 3.96 | 9.1 ms | 4.16 | 4.23 | 1.92 | 110.4 ms | 1.16 | 1.16 | 1.46 | 7.0 ms | 1.06 | 1.07 |
| Q01 | 32 | 5.48 | 10.0 ms | 4.44 | 4.61 | 1.89 | 118.8 ms | 1.16 | 1.16 | 1.43 | 7.4 ms | 1.05 | 1.05 |
| Q02 | 1 | 1.00 | 387.7 ms | 4.57 | 4.57 | 2.22 | 409.0 ms | 1.15 | 1.16 | 0.96 | 7.7 ms | 1.06 | 1.06 |
| Q02 | 4 | 3.97 | 441.4 ms | 4.58 | 4.59 | 5.22 | 506.2 ms | 1.16 | 1.17 | 1.82 | 9.4 ms | 1.06 | 1.06 |
| Q02 | 8 | 7.72 | 483.8 ms | 4.58 | 4.60 | 5.21 | 551.2 ms | 1.17 | 1.18 | 1.89 | 10.1 ms | 1.07 | 1.08 |
| Q02 | 32 | 7.91 | 493.1 ms | 4.53 | 4.56 | 5.02 | 570.4 ms | 1.17 | 1.18 | 1.84 | 10.9 ms | 1.07 | 1.07 |
| Q03 | 1 | 0.86 | 20.5 ms | 4.44 | 4.47 | 1.24 | 103.5 ms | 1.16 | 1.17 | 0.95 | 6.9 ms | 1.07 | 1.07 |
| Q03 | 4 | 3.15 | 22.8 ms | 4.34 | 4.43 | 1.93 | 155.0 ms | 1.17 | 1.18 | 1.72 | 8.4 ms | 1.07 | 1.07 |
| Q03 | 8 | 5.20 | 25.0 ms | 4.32 | 4.45 | 2.15 | 179.2 ms | 1.17 | 1.18 | 1.77 | 9.2 ms | 1.08 | 1.08 |
| Q03 | 32 | 6.88 | 26.9 ms | 4.50 | 4.54 | 1.97 | 182.5 ms | 1.18 | 1.18 | 1.72 | 9.8 ms | 1.07 | 1.07 |
| Q04 | 1 | 0.83 | 14.9 ms | 4.50 | 4.51 | 0.98 | 77.6 ms | 1.17 | 1.17 | 1.01 | 11.2 ms | 1.07 | 1.08 |
| Q04 | 4 | 2.91 | 17.8 ms | 4.55 | 4.56 | 1.62 | 127.5 ms | 1.17 | 1.17 | 2.19 | 12.8 ms | 1.07 | 1.07 |
| Q04 | 8 | 4.29 | 19.3 ms | 4.69 | 4.86 | 1.83 | 153.4 ms | 1.18 | 1.18 | 2.33 | 13.7 ms | 1.08 | 1.09 |
| Q04 | 32 | 6.22 | 20.8 ms | 4.88 | 4.93 | 1.84 | 166.1 ms | 1.18 | 1.18 | 2.23 | 14.7 ms | 1.08 | 1.08 |
| Q05 | 1 | 1.00 | 401.2 ms | 4.88 | 4.89 | 1.05 | 566.2 ms | 1.19 | 1.20 | 0.89 | 5.6 ms | 1.09 | 1.10 |
| Q05 | 4 | 3.97 | 443.3 ms | 4.90 | 4.91 | 3.95 | 654.4 ms | 1.25 | 1.28 | 1.53 | 7.2 ms | 1.08 | 1.09 |
| Q05 | 8 | 7.76 | 537.6 ms | 4.90 | 4.92 | 6.08 | 770.8 ms | 1.30 | 1.37 | 1.58 | 7.8 ms | 1.09 | 1.09 |
| Q05 | 32 | 7.94 | 547.6 ms | 4.85 | 4.88 | 6.54 | 818.3 ms | 1.32 | 1.41 | 1.55 | 8.4 ms | 1.09 | 1.10 |
| Q06 | 1 | 1.00 | 402.8 ms | 4.76 | 4.79 | 1.05 | 565.7 ms | 1.19 | 1.20 | 0.99 | 7.2 ms | 1.09 | 1.10 |
| Q06 | 4 | 3.97 | 439.3 ms | 4.76 | 4.76 | 3.89 | 655.1 ms | 1.25 | 1.28 | 1.64 | 9.0 ms | 1.09 | 1.09 |
| Q06 | 8 | 7.71 | 536.7 ms | 4.75 | 4.77 | 6.05 | 766.7 ms | 1.30 | 1.38 | 1.67 | 9.6 ms | 1.09 | 1.10 |
| Q06 | 32 | 7.90 | 544.9 ms | 4.71 | 4.73 | 6.31 | 809.1 ms | 1.31 | 1.41 | 1.63 | 10.2 ms | 1.09 | 1.10 |
| Q07 | 1 | 0.99 | 287.7 ms | 4.62 | 4.65 | 1.04 | 606.3 ms | 1.19 | 1.20 | 0.92 | 6.1 ms | 1.09 | 1.10 |
| Q07 | 4 | 3.96 | 315.2 ms | 4.61 | 4.63 | 3.91 | 702.4 ms | 1.26 | 1.28 | 1.62 | 7.8 ms | 1.09 | 1.10 |
| Q07 | 8 | 7.60 | 370.3 ms | 4.60 | 4.64 | 6.09 | 812.2 ms | 1.30 | 1.37 | 1.67 | 8.5 ms | 1.10 | 1.10 |
| Q07 | 32 | 7.90 | 374.8 ms | 4.54 | 4.58 | 6.43 | 853.2 ms | 1.31 | 1.39 | 1.62 | 9.1 ms | 1.10 | 1.11 |
| Q10 | 1 | 0.91 | 24.0 ms | 4.46 | 4.47 | 0.99 | 91.2 ms | 1.18 | 1.18 | 1.18 | 15.6 ms | 1.10 | 1.12 |
| Q10 | 4 | 2.80 | 28.9 ms | 4.57 | 4.66 | 1.57 | 141.3 ms | 1.18 | 1.19 | 2.05 | 17.8 ms | 1.10 | 1.11 |
| Q10 | 8 | 4.85 | 31.4 ms | 4.75 | 4.78 | 1.78 | 166.9 ms | 1.19 | 1.19 | 2.06 | 18.2 ms | 1.11 | 1.12 |
| Q10 | 32 | 5.69 | 32.8 ms | 4.86 | 4.96 | 1.82 | 179.1 ms | 1.19 | 1.20 | 2.00 | 18.7 ms | 1.11 | 1.11 |
| Q11 | 1 | 1.04 | 171.8 ms | 4.92 | 4.92 | 0.99 | 278.6 ms | 1.19 | 1.20 | 1.29 | 93.1 ms | 1.11 | 1.12 |
| Q11 | 4 | 3.78 | 196.7 ms | 4.92 | 4.93 | 1.38 | 346.2 ms | 1.21 | 1.23 | 2.00 | 103.4 ms | 1.12 | 1.13 |
| Q11 | 8 | 5.86 | 213.7 ms | 4.88 | 4.91 | 1.47 | 369.6 ms | 1.24 | 1.26 | 2.22 | 103.9 ms | 1.13 | 1.14 |
| Q11 | 32 | 6.11 | 218.1 ms | 4.82 | 4.85 | 1.59 | 377.5 ms | 1.27 | 1.31 | 2.24 | 101.6 ms | 1.18 | 1.20 |
| Q12 | 1 | 1.00 | 404.5 ms | 4.76 | 4.77 | 1.05 | 563.1 ms | 1.26 | 1.27 | 0.88 | 5.3 ms | 1.12 | 1.12 |
| Q12 | 4 | 3.97 | 410.2 ms | 4.76 | 4.77 | 3.92 | 648.7 ms | 1.32 | 1.34 | 1.52 | 7.0 ms | 1.12 | 1.13 |
| Q12 | 8 | 7.75 | 531.6 ms | 4.75 | 4.77 | 6.11 | 768.9 ms | 1.35 | 1.44 | 1.57 | 7.6 ms | 1.13 | 1.13 |
| Q12 | 32 | 7.96 | 553.5 ms | 4.72 | 4.73 | 6.53 | 811.6 ms | 1.36 | 1.44 | 1.53 | 8.2 ms | 1.13 | 1.14 |
| Q13 | 1 | 0.99 | 354.3 ms | 4.65 | 4.66 | 1.18 | 405.1 ms | 1.23 | 1.23 | 2.80 | 368.3 ms | 1.14 | 1.14 |
| Q13 | 4 | 3.96 | 358.6 ms | 4.66 | 4.66 | 4.11 | 469.4 ms | 1.23 | 1.24 | 7.69 | 448.4 ms | 1.15 | 1.16 |
| Q13 | 8 | 7.71 | 446.9 ms | 4.67 | 4.67 | 5.40 | 544.0 ms | 1.24 | 1.26 | 7.97 | 446.7 ms | 1.17 | 1.18 |
| Q13 | 32 | 7.94 | 451.7 ms | 4.68 | 4.68 | 5.40 | 566.6 ms | 1.24 | 1.26 | 7.98 | 450.5 ms | 1.17 | 1.19 |
| mix | 1 | 0.99 | 241.9 ms | 3.47 | 3.48 | 1.14 | 359.9 ms | 1.16 | 1.17 | 0.97 | 7.4 ms | 1.09 | 1.10 |
| mix | 4 | 3.94 | 266.9 ms | 3.50 | 3.50 | 3.85 | 432.0 ms | 1.20 | 1.24 | 1.75 | 9.2 ms | 1.09 | 1.09 |
| mix | 8 | 7.57 | 318.8 ms | 3.53 | 3.54 | 4.86 | 507.4 ms | 1.22 | 1.30 | 1.80 | 9.8 ms | 1.09 | 1.10 |
| mix | 32 | 7.88 | 322.2 ms | 3.55 | 3.57 | 4.86 | 534.3 ms | 1.22 | 1.30 | 1.75 | 10.4 ms | 1.09 | 1.10 |

## resources, votable

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-final-w1 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.70 | 7.3 ms | 1.31 | 1.33 | 0.95 | 41.8 ms | 0.83 | 0.84 | 0.88 | 4.7 ms | 0.93 | 0.94 |
| Q01 | 4 | 2.28 | 8.3 ms | 1.51 | 1.63 | 1.78 | 97.1 ms | 0.85 | 0.87 | 1.43 | 6.6 ms | 0.90 | 0.91 |
| Q01 | 8 | 3.79 | 9.0 ms | 1.85 | 2.01 | 1.97 | 114.7 ms | 0.88 | 0.89 | 1.48 | 7.1 ms | 0.90 | 0.91 |
| Q01 | 32 | 5.47 | 10.1 ms | 2.33 | 2.51 | 1.92 | 123.7 ms | 0.90 | 0.91 | 1.44 | 7.5 ms | 0.90 | 0.90 |
| Q02 | 1 | 1.00 | 384.9 ms | 2.48 | 2.48 | 2.19 | 408.9 ms | 0.90 | 0.90 | 0.97 | 8.2 ms | 0.91 | 0.92 |
| Q02 | 4 | 3.96 | 430.6 ms | 2.47 | 2.48 | 5.13 | 511.5 ms | 0.91 | 0.92 | 1.88 | 9.9 ms | 0.91 | 0.93 |
| Q02 | 8 | 7.71 | 485.4 ms | 2.48 | 2.49 | 5.19 | 554.6 ms | 0.92 | 0.94 | 1.95 | 10.7 ms | 0.92 | 0.92 |
| Q02 | 32 | 7.91 | 495.7 ms | 2.47 | 2.48 | 5.04 | 574.9 ms | 0.93 | 0.95 | 1.89 | 11.4 ms | 0.92 | 0.92 |
| Q03 | 1 | 0.87 | 21.1 ms | 2.38 | 2.40 | 1.22 | 106.2 ms | 0.92 | 0.92 | 0.95 | 7.2 ms | 0.93 | 0.93 |
| Q03 | 4 | 3.14 | 23.4 ms | 2.41 | 2.45 | 1.94 | 159.3 ms | 0.93 | 0.93 | 1.76 | 8.8 ms | 0.92 | 0.93 |
| Q03 | 8 | 5.17 | 25.6 ms | 2.61 | 2.74 | 2.15 | 182.6 ms | 0.93 | 0.94 | 1.80 | 9.5 ms | 0.93 | 0.94 |
| Q03 | 32 | 6.78 | 27.5 ms | 2.92 | 3.03 | 2.13 | 192.8 ms | 0.93 | 0.94 | 1.75 | 10.2 ms | 0.93 | 0.93 |
| Q04 | 1 | 0.84 | 16.6 ms | 3.00 | 3.02 | 0.98 | 80.5 ms | 0.92 | 0.93 | 1.02 | 12.0 ms | 0.92 | 0.93 |
| Q04 | 4 | 2.94 | 19.0 ms | 3.09 | 3.13 | 1.62 | 130.5 ms | 0.93 | 0.93 | 2.23 | 13.7 ms | 0.92 | 0.92 |
| Q04 | 8 | 4.70 | 20.4 ms | 3.24 | 3.38 | 1.83 | 154.6 ms | 0.94 | 0.94 | 2.35 | 14.6 ms | 0.93 | 0.94 |
| Q04 | 32 | 6.16 | 21.8 ms | 3.48 | 3.57 | 1.85 | 165.1 ms | 0.94 | 0.94 | 2.26 | 15.2 ms | 0.93 | 0.94 |
| Q05 | 1 | 1.00 | 399.4 ms | 3.52 | 3.53 | 1.05 | 570.2 ms | 0.95 | 0.96 | 0.89 | 5.6 ms | 0.94 | 0.94 |
| Q05 | 4 | 3.97 | 467.5 ms | 3.55 | 3.55 | 3.93 | 659.7 ms | 1.01 | 1.04 | 1.55 | 7.4 ms | 0.93 | 0.94 |
| Q05 | 8 | 7.76 | 539.6 ms | 3.55 | 3.56 | 6.06 | 775.8 ms | 1.06 | 1.12 | 1.60 | 8.0 ms | 0.94 | 0.95 |
| Q05 | 32 | 7.85 | 552.0 ms | 3.51 | 3.53 | 6.42 | 829.1 ms | 1.06 | 1.16 | 1.56 | 8.6 ms | 0.94 | 0.95 |
| Q06 | 1 | 1.00 | 397.3 ms | 3.43 | 3.44 | 1.05 | 569.3 ms | 0.95 | 0.96 | 1.01 | 7.9 ms | 0.94 | 0.95 |
| Q06 | 4 | 3.97 | 430.8 ms | 3.43 | 3.44 | 3.91 | 658.1 ms | 1.01 | 1.04 | 1.71 | 9.7 ms | 0.94 | 0.94 |
| Q06 | 8 | 7.68 | 538.2 ms | 3.42 | 3.43 | 5.93 | 775.0 ms | 1.04 | 1.11 | 1.74 | 10.4 ms | 0.94 | 0.95 |
| Q06 | 32 | 7.88 | 547.9 ms | 3.38 | 3.39 | 6.27 | 817.9 ms | 1.07 | 1.17 | 1.70 | 11.0 ms | 0.95 | 0.95 |
| Q07 | 1 | 1.00 | 288.6 ms | 3.30 | 3.32 | 1.04 | 610.7 ms | 0.95 | 0.96 | 0.93 | 6.4 ms | 0.95 | 0.95 |
| Q07 | 4 | 3.95 | 315.2 ms | 3.32 | 3.33 | 3.86 | 702.9 ms | 1.01 | 1.04 | 1.65 | 8.2 ms | 0.94 | 0.95 |
| Q07 | 8 | 7.59 | 371.3 ms | 3.33 | 3.35 | 6.06 | 817.7 ms | 1.05 | 1.14 | 1.69 | 8.8 ms | 0.95 | 0.95 |
| Q07 | 32 | 7.90 | 374.7 ms | 3.35 | 3.36 | 6.38 | 865.5 ms | 1.07 | 1.14 | 1.65 | 9.4 ms | 0.95 | 0.95 |
| Q10 | 1 | 0.93 | 30.2 ms | 3.30 | 3.31 | 0.98 | 92.6 ms | 0.94 | 0.94 | 1.18 | 18.5 ms | 0.96 | 0.97 |
| Q10 | 4 | 3.12 | 34.7 ms | 3.42 | 3.54 | 1.58 | 142.9 ms | 0.95 | 0.95 | 2.22 | 20.9 ms | 0.96 | 0.97 |
| Q10 | 8 | 5.07 | 37.8 ms | 3.65 | 3.68 | 1.80 | 167.7 ms | 0.96 | 0.97 | 2.21 | 21.2 ms | 0.97 | 0.97 |
| Q10 | 32 | 5.93 | 39.5 ms | 3.71 | 3.73 | 1.85 | 180.6 ms | 0.97 | 0.97 | 2.14 | 21.6 ms | 0.97 | 0.98 |
| Q11 | 1 | 1.03 | 216.7 ms | 3.68 | 3.69 | 1.01 | 256.5 ms | 1.01 | 1.02 | 1.36 | 118.3 ms | 0.98 | 0.99 |
| Q11 | 4 | 3.79 | 252.8 ms | 3.69 | 3.69 | 1.42 | 320.2 ms | 1.07 | 1.10 | 2.34 | 134.0 ms | 0.99 | 1.00 |
| Q11 | 8 | 6.04 | 279.8 ms | 3.66 | 3.68 | 1.52 | 340.9 ms | 1.14 | 1.16 | 2.47 | 133.6 ms | 1.02 | 1.03 |
| Q11 | 32 | 6.23 | 287.2 ms | 3.61 | 3.62 | 1.65 | 360.2 ms | 1.21 | 1.26 | 2.52 | 130.5 ms | 1.12 | 1.13 |
| Q12 | 1 | 1.00 | 404.9 ms | 3.56 | 3.57 | 1.05 | 566.1 ms | 1.18 | 1.19 | 0.89 | 5.5 ms | 1.04 | 1.05 |
| Q12 | 4 | 3.97 | 436.3 ms | 3.57 | 3.57 | 3.94 | 659.8 ms | 1.24 | 1.27 | 1.53 | 7.2 ms | 1.04 | 1.05 |
| Q12 | 8 | 7.76 | 537.6 ms | 3.56 | 3.58 | 6.06 | 778.1 ms | 1.27 | 1.35 | 1.58 | 7.8 ms | 1.04 | 1.06 |
| Q12 | 32 | 7.95 | 554.6 ms | 3.53 | 3.54 | 6.45 | 829.8 ms | 1.26 | 1.35 | 1.55 | 8.4 ms | 1.04 | 1.05 |
| Q13 | 1 | 1.00 | 351.4 ms | 3.48 | 3.49 | 1.18 | 411.8 ms | 1.14 | 1.14 | 2.80 | 369.4 ms | 1.06 | 1.06 |
| Q13 | 4 | 3.96 | 379.8 ms | 3.49 | 3.51 | 4.09 | 471.4 ms | 1.15 | 1.16 | 7.68 | 453.6 ms | 1.07 | 1.07 |
| Q13 | 8 | 7.68 | 444.6 ms | 3.51 | 3.52 | 5.37 | 546.0 ms | 1.16 | 1.17 | 7.97 | 449.2 ms | 1.09 | 1.10 |
| Q13 | 32 | 7.93 | 452.4 ms | 3.50 | 3.51 | 5.36 | 572.3 ms | 1.16 | 1.18 | 7.97 | 452.7 ms | 1.09 | 1.11 |
| mix | 1 | 1.01 | 246.5 ms | 1.07 | 1.09 | 1.16 | 361.2 ms | 0.79 | 0.81 | 0.98 | 8.0 ms | 0.89 | 0.90 |
| mix | 4 | 3.98 | 270.7 ms | 1.11 | 1.12 | 3.88 | 433.1 ms | 0.85 | 0.89 | 1.80 | 9.7 ms | 0.89 | 0.90 |
| mix | 8 | 7.53 | 320.9 ms | 1.27 | 1.28 | 4.93 | 507.9 ms | 0.88 | 0.96 | 1.84 | 10.3 ms | 0.91 | 0.92 |
| mix | 32 | 7.85 | 323.2 ms | 1.30 | 1.32 | 4.90 | 531.6 ms | 0.89 | 0.94 | 1.79 | 11.0 ms | 0.94 | 0.95 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | argus-final | — | 4.1 | 0.99 | 4.1 | 241.9 |
| csv | 1 | dachs-final | — | 3.2 | 1.14 | 2.8 | 359.9 |
| csv | 1 | egernia-final-w1 | 1 | 129.7 | 0.97 | 134.4 | 7.4 |
| csv | 4 | argus-final | — | 14.8 | 3.94 | 3.8 | 266.9 |
| csv | 4 | dachs-final | — | 9.0 | 3.85 | 2.3 | 432.0 |
| csv | 4 | egernia-final-w1 | 1 | 191.6 | 1.75 | 109.2 | 9.2 |
| csv | 8 | argus-final | — | 23.9 | 7.57 | 3.2 | 318.8 |
| csv | 8 | dachs-final | — | 9.6 | 4.86 | 2.0 | 507.4 |
| csv | 8 | egernia-final-w1 | 1 | 183.5 | 1.80 | 101.8 | 9.8 |
| csv | 32 | argus-final | — | 24.6 | 7.88 | 3.1 | 322.2 |
| csv | 32 | dachs-final | — | 9.2 | 4.86 | 1.9 | 534.3 |
| csv | 32 | egernia-final-w1 | 1 | 167.7 | 1.75 | 95.8 | 10.4 |
| votable | 1 | argus-final | — | 4.1 | 1.01 | 4.1 | 246.5 |
| votable | 1 | dachs-final | — | 3.2 | 1.16 | 2.8 | 361.2 |
| votable | 1 | egernia-final-w1 | 1 | 122.9 | 0.98 | 125.4 | 8.0 |
| votable | 4 | argus-final | — | 14.7 | 3.98 | 3.7 | 270.7 |
| votable | 4 | dachs-final | — | 9.0 | 3.88 | 2.3 | 433.1 |
| votable | 4 | egernia-final-w1 | 1 | 185.7 | 1.80 | 103.0 | 9.7 |
| votable | 8 | argus-final | — | 23.6 | 7.53 | 3.1 | 320.9 |
| votable | 8 | dachs-final | — | 9.8 | 4.93 | 2.0 | 507.9 |
| votable | 8 | egernia-final-w1 | 1 | 178.2 | 1.84 | 96.9 | 10.3 |
| votable | 32 | argus-final | — | 24.5 | 7.85 | 3.1 | 323.2 |
| votable | 32 | dachs-final | — | 9.3 | 4.90 | 1.9 | 531.6 |
| votable | 32 | egernia-final-w1 | 1 | 163.3 | 1.79 | 91.3 | 11.0 |

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
    -f benchmarks/tap-compare/final/pins/egernia-w1.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets argus-final dachs-final egernia-final-w1 --scenario <scenario>
```

Environment: see `environment.json` (git 41bfc513, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Phase A of the pre-registered final three-way comparison (`benchmarks/tap-compare/final/PROTOCOL.md`): **Table A — one-process parity**. egernia with one uvicorn worker against GAVO DaCHS and CADC argus, all three up at once on **disjoint cpusets** (egernia 0-7, argus 8-15, DaCHS 16-23, generator 24-29), so the three targets interleave A,B,C inside every cell — the interleaving the argus and resource-scaling runs had to give up. Phase B measures the same DaCHS and the same argus against egernia with eight workers; together the two reports replace every earlier performance table.
- **Provenance.** Pre-registered at tag `tap-compare-final-prereg-v1` = `dbff366`; measured at `41bfc513`. The commits in between touch only `final/PROTOCOL.md` (prose and its amendment 1), `final/run.sh` (the pre-measurement verification and refusal path) and `tests/test_final.py`: `git diff dbff366..41bfc513` restricted to `final/scenarios.yaml`, `final/targets.yaml`, `final/pins/` and the frozen `config/` is **empty**, so the workload, grid, windows, repetitions, gate criteria, statistics, tie rule, error ceiling, generator guard and every pin that produced these numbers are byte-identical to the pre-registration.
- **Servers.** egernia `main` 1845521 (PRs #160 denormalised `ivoa.obscore` and #161 read-replica routing), API image built 2026-09-10, **one** uvicorn worker, `TAP_QUERY_DATABASE_URL` unset in both the API and the executor so #161 is inert and every query goes to the one database — verified before measuring, as was `ivoa.obscore` being a table (`relkind = 'r'`, #160). GAVO DaCHS 2.11, schema 36/36, Debian `gavodachs2-server`, its PostgreSQL sized to its container by the ¼ rule (`shared_buffers` 2 GB, `effective_cache_size` 6 GB, parallel budget 32/40). CADC argus 1.0.27 (`IMAGE_VERSION=1.0.27`), PostgreSQL 17 + pgsphere, `caom2.obscore` as a plain table, pools of 8, **UWS job store truncated before the phase** (4,301,717 rows removed) so argus starts where its first published run started.
- **Gates.** All three `taplint` PASS — egernia 0 errors, DaCHS 0, argus 0 blocking / 2 total (the TAP_UPLOAD-by-URL stage, as in its earlier run; uploads are not in the workload). **Three-way agreement 11/11 classes, none excluded**: the gate requires unanimity across all three servers on row count and an order-independent checksum, with no reference server and no privileged pair. Corpus `obscore.csv` sha256 `bc411050…`, 500,096 rows in all three servers.
- **Verdicts: egernia 66, argus 18, ties 12, DaCHS 0 — of 96 cells** (12 classes × 2 formats × 4 concurrencies). **No rung was invalidated, no generator guard tripped (peak 0.505 of one core against the 0.6 limit), and not one rung of 864 exceeded 1% errors** across 3,888,305 requests.
- **Where each wins, and why.** egernia takes every cell of the cone classes (Q05, Q06, Q07, Q12), the DID lookup Q02, the aggregate-heavy Q13 (4 wins, 4 ties) and the mixed workload. argus takes the classes whose cost is server-side rendering and streaming, from c ≥ 8: Q01 (metadata), Q10 and Q11 (large results), and Q03/Q04 at c = 32. The resource tables explain the split exactly: on the mix at c = 32 argus, a JVM with a thread per request, uses **7.9 of its 8 cores at 322 ms of CPU per request** and DaCHS **4.9 cores at 534 ms**, while egernia uses **1.8 cores at 10.4 ms** — 31× and 51× less CPU per request, with six of its eight cores idle because one uvicorn worker is one core. That idle headroom is the whole subject of phase B.
- **DaCHS wins nothing here**, against 1 winning cell in the last two-way run — and it is measured under a *fairer* PostgreSQL than that run gave it (the ¼ rule rather than Debian's stock 128 MB).
- **Hypotheses settled by this phase.** **H3(a) holds**: after #160 the scan-heavy classes are no worse than the published parity run and the cells an opponent was level on resolve in egernia's favour or stay ties — Q13 moves from ties at c ≥ 8 to 4 wins and 4 ties, Q11 and Q12 lose nothing, and DaCHS's one former winning cell (CSV Q11 at c=32) is gone; egernia's CPU per request on the mix is ~10 ms here against the ~22–24 ms the scaling run measured on the view. **H4 holds**: zero shed load anywhere, at any concurrency. **H5 holds in both halves**: DaCHS is flat — 23 of 24 class/format pairs tie between c=8 and c=32 — while argus's c=32 beats its own c=1 in **24 of 24**, more than the eight-of-twelve the protocol predicted. **H1 and H2 are phase B's**, and nothing here pre-empts them.
- **Conditions.** 864 rungs interleaved A,B,C, 19.8 h (2026-09-11 06:58:43Z → 09-12 02:48:42Z), four concurrencies {1, 4, 8, 32}, 20 s warm-up and 60 s windows, six generator processes pinned to cores 24-29, an untimed 45 s warm pass per server before the grid. Resource telemetry covered **every** rung (mean coverage 0.92) — unlike the scaling run, the sampler started before the first one. Nothing else ran on the host; the driver refuses to start while another tap-compare measurement is alive or an unpinned foreign container is burning CPU, and recorded the host's state in `pins/a-host.txt`.

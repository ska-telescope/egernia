# 20260908T061813Z-f1cf2c25-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: argus in `benchmarks/tap-compare/docker-compose.argus.yml` (shared `cpuset` of 8 cores; 8 GiB split 3 Tomcat / 5 PostgreSQL; `benchmarks/tap-compare/argus/PROTOCOL.md`); egernia in `benchmarks/tap-compare/argus-equal-cpu/egernia-equalcpu.yml` (shared `cpuset` of 8 cores; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=8`, PostgreSQL parallel budget 144/152; `benchmarks/tap-compare/argus-equal-cpu/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-local | 1.1 | PASS (2 errors) | 134217728 |
| egernia-local-equalcpu | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | argus-local rps | argus-local p95 (s) | egernia-local-equalcpu rps | egernia-local-equalcpu p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 79.9 ±14.0 | 0.015 ±0.000 | 168.1 ±1.1 | 0.008 ±0.000 | egernia-local-equalcpu |
| Q01 | 4 | 231.0 ±45.7 | 0.019 ±0.000 | 421.9 ±170.0 | 0.015 ±0.008 | tie |
| Q01 | 8 | 402.1 ±16.0 | 0.024 ±0.001 | 641.1 ±136.5 | 0.022 ±0.013 | egernia-local-equalcpu |
| Q01 | 16 | 549.7 ±6.5 | 0.036 ±0.002 | 726.4 ±186.6 | 0.042 ±0.009 | tie |
| Q01 | 32 | 552.2 ±6.9 | 0.068 ±0.002 | 740.6 ±97.6 | 0.081 ±0.016 | egernia-local-equalcpu |
| Q02 | 1 | 2.4 ±0.1 | 0.435 ±0.009 | 65.4 ±0.4 | 0.022 ±0.001 | egernia-local-equalcpu |
| Q02 | 4 | 9.0 ±0.6 | 0.510 ±0.005 | 179.2 ±22.0 | 0.032 ±0.004 | egernia-local-equalcpu |
| Q02 | 8 | 15.4 ±0.1 | 0.545 ±0.001 | 256.3 ±19.2 | 0.045 ±0.005 | egernia-local-equalcpu |
| Q02 | 16 | 15.6 ±0.0 | 1.084 ±0.005 | 310.2 ±16.6 | 0.077 ±0.006 | egernia-local-equalcpu |
| Q02 | 32 | 15.7 ±0.1 | 2.122 ±0.016 | 324.9 ±11.6 | 0.176 ±0.027 | egernia-local-equalcpu |
| Q03 | 1 | 37.5 ±0.2 | 0.086 ±0.001 | 34.9 ±0.8 | 0.124 ±0.001 | tie |
| Q03 | 4 | 122.9 ±15.8 | 0.100 ±0.000 | 108.9 ±4.2 | 0.156 ±0.002 | tie |
| Q03 | 8 | 188.8 ±16.2 | 0.120 ±0.001 | 164.3 ±5.6 | 0.192 ±0.008 | argus-local |
| Q03 | 16 | 242.7 ±8.1 | 0.176 ±0.002 | 188.9 ±1.8 | 0.340 ±0.010 | argus-local |
| Q03 | 32 | 245.9 ±5.3 | 0.246 ±0.004 | 192.6 ±2.6 | 0.722 ±0.012 | argus-local |
| Q04 | 1 | 46.1 ±0.3 | 0.025 ±0.000 | 46.9 ±0.5 | 0.025 ±0.001 | tie |
| Q04 | 4 | 147.5 ±1.9 | 0.032 ±0.000 | 140.3 ±15.1 | 0.036 ±0.006 | tie |
| Q04 | 8 | 227.0 ±7.2 | 0.043 ±0.001 | 194.9 ±5.1 | 0.054 ±0.002 | argus-local |
| Q04 | 16 | 292.9 ±8.3 | 0.069 ±0.002 | 242.9 ±9.9 | 0.092 ±0.010 | argus-local |
| Q04 | 32 | 293.8 ±4.2 | 0.127 ±0.002 | 257.0 ±8.0 | 0.195 ±0.040 | argus-local |
| Q05 | 1 | 2.3 ±0.0 | 0.448 ±0.002 | 102.6 ±2.4 | 0.012 ±0.001 | egernia-local-equalcpu |
| Q05 | 4 | 8.0 ±0.7 | 0.559 ±0.007 | 269.9 ±30.4 | 0.020 ±0.001 | egernia-local-equalcpu |
| Q05 | 8 | 14.1 ±0.2 | 0.590 ±0.008 | 365.9 ±129.3 | 0.032 ±0.008 | egernia-local-equalcpu |
| Q05 | 16 | 14.4 ±0.1 | 1.194 ±0.033 | 476.3 ±23.3 | 0.061 ±0.016 | egernia-local-equalcpu |
| Q05 | 32 | 14.4 ±0.2 | 2.307 ±0.028 | 500.4 ±28.5 | 0.116 ±0.037 | egernia-local-equalcpu |
| Q06 | 1 | 2.3 ±0.0 | 0.454 ±0.003 | 57.1 ±0.4 | 0.023 ±0.000 | egernia-local-equalcpu |
| Q06 | 4 | 8.1 ±0.7 | 0.563 ±0.002 | 163.4 ±13.6 | 0.034 ±0.004 | egernia-local-equalcpu |
| Q06 | 8 | 14.2 ±0.1 | 0.608 ±0.010 | 225.4 ±13.8 | 0.053 ±0.011 | egernia-local-equalcpu |
| Q06 | 16 | 14.5 ±0.1 | 1.195 ±0.022 | 283.4 ±13.5 | 0.088 ±0.015 | egernia-local-equalcpu |
| Q06 | 32 | 14.3 ±0.6 | 2.340 ±0.063 | 290.9 ±32.2 | 0.202 ±0.099 | egernia-local-equalcpu |
| Q07 | 1 | 3.1 ±0.2 | 0.437 ±0.002 | 78.0 ±0.6 | 0.017 ±0.000 | egernia-local-equalcpu |
| Q07 | 4 | 11.4 ±0.5 | 0.508 ±0.016 | 227.2 ±11.5 | 0.025 ±0.002 | egernia-local-equalcpu |
| Q07 | 8 | 19.8 ±0.1 | 0.564 ±0.002 | 299.4 ±28.5 | 0.040 ±0.005 | egernia-local-equalcpu |
| Q07 | 16 | 20.5 ±0.1 | 0.987 ±0.006 | 362.8 ±23.8 | 0.076 ±0.017 | egernia-local-equalcpu |
| Q07 | 32 | 20.5 ±0.1 | 1.819 ±0.032 | 409.6 ±11.0 | 0.133 ±0.009 | egernia-local-equalcpu |
| Q10 | 1 | 31.3 ±1.7 | 0.036 ±0.000 | 31.0 ±0.5 | 0.037 ±0.001 | tie |
| Q10 | 4 | 91.3 ±21.2 | 0.047 ±0.001 | 91.7 ±5.0 | 0.055 ±0.004 | tie |
| Q10 | 8 | 144.0 ±19.5 | 0.064 ±0.002 | 125.0 ±6.3 | 0.086 ±0.007 | tie |
| Q10 | 16 | 174.2 ±7.1 | 0.116 ±0.005 | 146.9 ±2.6 | 0.155 ±0.005 | argus-local |
| Q10 | 32 | 175.0 ±0.6 | 0.208 ±0.002 | 147.4 ±1.1 | 0.325 ±0.027 | argus-local |
| Q11 | 1 | 5.6 ±0.0 | 0.188 ±0.002 | 2.9 ±0.1 | 0.401 ±0.012 | argus-local |
| Q11 | 4 | 18.4 ±0.0 | 0.241 ±0.001 | 10.2 ±1.1 | 0.551 ±0.157 | argus-local |
| Q11 | 8 | 26.6 ±0.1 | 0.346 ±0.004 | 15.8 ±0.5 | 0.722 ±0.099 | argus-local |
| Q11 | 16 | 27.3 ±0.1 | 0.662 ±0.006 | 17.7 ±0.5 | 1.373 ±0.030 | argus-local |
| Q11 | 32 | 27.4 ±0.2 | 1.245 ±0.017 | 18.5 ±1.2 | 2.697 ±1.232 | argus-local |
| Q12 | 1 | 2.3 ±0.0 | 0.449 ±0.002 | 108.3 ±0.8 | 0.012 ±0.001 | egernia-local-equalcpu |
| Q12 | 4 | 8.4 ±0.5 | 0.551 ±0.017 | 302.7 ±31.9 | 0.018 ±0.003 | egernia-local-equalcpu |
| Q12 | 8 | 14.3 ±0.1 | 0.588 ±0.005 | 357.2 ±92.8 | 0.033 ±0.002 | egernia-local-equalcpu |
| Q12 | 16 | 14.6 ±0.2 | 1.184 ±0.010 | 499.4 ±48.5 | 0.052 ±0.014 | egernia-local-equalcpu |
| Q12 | 32 | 14.5 ±0.2 | 2.293 ±0.033 | 520.2 ±39.5 | 0.110 ±0.033 | egernia-local-equalcpu |
| Q13 | 1 | 2.6 ±0.0 | 0.431 ±0.003 | 4.2 ±0.1 | 0.327 ±0.003 | egernia-local-equalcpu |
| Q13 | 4 | 10.0 ±0.6 | 0.467 ±0.067 | 9.6 ±0.2 | 0.563 ±0.012 | tie |
| Q13 | 8 | 16.7 ±0.1 | 0.567 ±0.005 | 9.7 ±0.0 | 1.110 ±0.012 | argus-local |
| Q13 | 16 | 17.3 ±0.2 | 1.067 ±0.011 | 9.7 ±0.3 | 2.231 ±0.037 | argus-local |
| Q13 | 32 | 17.3 ±0.1 | 2.013 ±0.007 | 9.7 ±0.1 | 4.615 ±0.614 | argus-local |
| mix | 1 | 3.9 ±0.3 | 0.434 ±0.004 | 57.9 ±0.9 | 0.032 ±0.000 | egernia-local-equalcpu |
| mix | 4 | 13.8 ±0.7 | 0.540 ±0.011 | 170.2 ±6.9 | 0.043 ±0.002 | egernia-local-equalcpu |
| mix | 8 | 23.5 ±0.2 | 0.582 ±0.003 | 238.6 ±22.3 | 0.060 ±0.005 | egernia-local-equalcpu |
| mix | 16 | 24.4 ±0.3 | 1.017 ±0.004 | 287.3 ±45.5 | 0.105 ±0.030 | egernia-local-equalcpu |
| mix | 32 | 24.4 ±0.3 | 1.727 ±0.080 | 310.0 ±3.6 | 0.199 ±0.038 | egernia-local-equalcpu |

## votable

| class | c | argus-local rps | argus-local p95 (s) | egernia-local-equalcpu rps | egernia-local-equalcpu p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 83.8 ±0.4 | 0.015 ±0.000 | 166.3 ±1.9 | 0.008 ±0.000 | egernia-local-equalcpu |
| Q01 | 4 | 251.1 ±19.7 | 0.019 ±0.000 | 418.9 ±164.3 | 0.015 ±0.008 | tie |
| Q01 | 8 | 396.1 ±6.1 | 0.024 ±0.000 | 574.2 ±7.2 | 0.024 ±0.007 | egernia-local-equalcpu |
| Q01 | 16 | 552.1 ±15.3 | 0.035 ±0.000 | 793.5 ±33.1 | 0.035 ±0.001 | egernia-local-equalcpu |
| Q01 | 32 | 556.8 ±13.7 | 0.067 ±0.000 | 750.0 ±35.3 | 0.097 ±0.041 | egernia-local-equalcpu |
| Q02 | 1 | 2.5 ±0.0 | 0.421 ±0.004 | 63.8 ±1.4 | 0.022 ±0.000 | egernia-local-equalcpu |
| Q02 | 4 | 8.9 ±0.5 | 0.506 ±0.006 | 177.5 ±19.7 | 0.032 ±0.003 | egernia-local-equalcpu |
| Q02 | 8 | 15.6 ±0.0 | 0.543 ±0.010 | 236.1 ±10.8 | 0.050 ±0.006 | egernia-local-equalcpu |
| Q02 | 16 | 15.9 ±0.1 | 1.072 ±0.035 | 306.9 ±22.0 | 0.078 ±0.011 | egernia-local-equalcpu |
| Q02 | 32 | 15.8 ±0.0 | 2.105 ±0.011 | 317.0 ±6.9 | 0.167 ±0.016 | egernia-local-equalcpu |
| Q03 | 1 | 37.4 ±0.3 | 0.085 ±0.000 | 34.3 ±0.7 | 0.125 ±0.000 | tie |
| Q03 | 4 | 122.7 ±5.7 | 0.099 ±0.000 | 108.1 ±8.2 | 0.157 ±0.005 | argus-local |
| Q03 | 8 | 194.8 ±0.8 | 0.119 ±0.000 | 162.4 ±5.0 | 0.194 ±0.010 | argus-local |
| Q03 | 16 | 239.0 ±4.0 | 0.176 ±0.002 | 186.5 ±4.4 | 0.350 ±0.021 | argus-local |
| Q03 | 32 | 237.3 ±14.8 | 0.246 ±0.006 | 189.1 ±2.0 | 0.777 ±0.070 | argus-local |
| Q04 | 1 | 45.1 ±0.5 | 0.026 ±0.000 | 45.2 ±0.1 | 0.026 ±0.001 | tie |
| Q04 | 4 | 142.6 ±1.7 | 0.034 ±0.000 | 138.5 ±2.6 | 0.036 ±0.001 | tie |
| Q04 | 8 | 216.4 ±16.2 | 0.045 ±0.001 | 190.2 ±16.4 | 0.055 ±0.007 | tie |
| Q04 | 16 | 277.1 ±2.4 | 0.074 ±0.001 | 223.8 ±35.4 | 0.103 ±0.010 | argus-local |
| Q04 | 32 | 275.0 ±3.5 | 0.134 ±0.002 | 247.3 ±2.0 | 0.202 ±0.021 | argus-local |
| Q05 | 1 | 2.4 ±0.0 | 0.441 ±0.004 | 99.8 ±3.6 | 0.013 ±0.001 | egernia-local-equalcpu |
| Q05 | 4 | 8.6 ±1.7 | 0.508 ±0.137 | 250.2 ±24.1 | 0.022 ±0.005 | egernia-local-equalcpu |
| Q05 | 8 | 14.4 ±0.1 | 0.583 ±0.005 | 350.8 ±103.2 | 0.039 ±0.016 | egernia-local-equalcpu |
| Q05 | 16 | 14.6 ±0.0 | 1.174 ±0.044 | 456.5 ±60.0 | 0.055 ±0.011 | egernia-local-equalcpu |
| Q05 | 32 | 14.6 ±0.1 | 2.272 ±0.020 | 491.8 ±28.0 | 0.127 ±0.036 | egernia-local-equalcpu |
| Q06 | 1 | 2.4 ±0.0 | 0.443 ±0.004 | 55.0 ±0.7 | 0.025 ±0.000 | egernia-local-equalcpu |
| Q06 | 4 | 8.7 ±1.3 | 0.521 ±0.139 | 161.2 ±15.8 | 0.035 ±0.004 | egernia-local-equalcpu |
| Q06 | 8 | 14.3 ±0.1 | 0.602 ±0.006 | 206.7 ±33.9 | 0.058 ±0.007 | egernia-local-equalcpu |
| Q06 | 16 | 14.6 ±0.2 | 1.181 ±0.009 | 257.2 ±66.2 | 0.109 ±0.057 | egernia-local-equalcpu |
| Q06 | 32 | 14.6 ±0.1 | 2.294 ±0.011 | 283.2 ±22.6 | 0.195 ±0.022 | egernia-local-equalcpu |
| Q07 | 1 | 3.2 ±0.2 | 0.427 ±0.010 | 76.5 ±0.3 | 0.018 ±0.000 | egernia-local-equalcpu |
| Q07 | 4 | 12.0 ±0.5 | 0.478 ±0.037 | 217.7 ±7.3 | 0.026 ±0.001 | egernia-local-equalcpu |
| Q07 | 8 | 20.2 ±0.1 | 0.559 ±0.001 | 288.0 ±22.9 | 0.042 ±0.001 | egernia-local-equalcpu |
| Q07 | 16 | 20.9 ±0.1 | 0.972 ±0.019 | 364.0 ±13.1 | 0.069 ±0.017 | egernia-local-equalcpu |
| Q07 | 32 | 20.8 ±0.5 | 1.796 ±0.098 | 399.4 ±26.2 | 0.142 ±0.061 | egernia-local-equalcpu |
| Q10 | 1 | 28.0 ±0.2 | 0.041 ±0.000 | 28.8 ±0.0 | 0.041 ±0.001 | tie |
| Q10 | 4 | 85.0 ±4.5 | 0.055 ±0.003 | 82.9 ±4.9 | 0.062 ±0.005 | tie |
| Q10 | 8 | 129.3 ±3.3 | 0.075 ±0.001 | 116.1 ±9.0 | 0.092 ±0.009 | argus-local |
| Q10 | 16 | 148.9 ±0.4 | 0.135 ±0.001 | 135.1 ±2.2 | 0.167 ±0.007 | argus-local |
| Q10 | 32 | 146.3 ±0.5 | 0.248 ±0.004 | 134.4 ±1.5 | 0.351 ±0.036 | tie |
| Q11 | 1 | 4.5 ±0.0 | 0.234 ±0.002 | 1.8 ±0.0 | 0.656 ±0.019 | argus-local |
| Q11 | 4 | 14.6 ±0.1 | 0.308 ±0.003 | 8.7 ±0.5 | 0.645 ±0.064 | argus-local |
| Q11 | 8 | 20.9 ±1.3 | 0.442 ±0.014 | 14.5 ±0.6 | 0.752 ±0.078 | argus-local |
| Q11 | 16 | 21.6 ±0.0 | 0.839 ±0.006 | 16.2 ±0.3 | 1.500 ±0.119 | argus-local |
| Q11 | 32 | 21.7 ±0.1 | 1.579 ±0.002 | 17.2 ±0.3 | 2.665 ±0.308 | argus-local |
| Q12 | 1 | 2.4 ±0.0 | 0.440 ±0.001 | 106.5 ±1.6 | 0.012 ±0.001 | egernia-local-equalcpu |
| Q12 | 4 | 8.7 ±1.2 | 0.515 ±0.145 | 279.4 ±60.7 | 0.020 ±0.006 | egernia-local-equalcpu |
| Q12 | 8 | 14.5 ±0.0 | 0.580 ±0.003 | 412.8 ±20.2 | 0.029 ±0.000 | egernia-local-equalcpu |
| Q12 | 16 | 14.5 ±0.7 | 1.187 ±0.124 | 469.1 ±65.4 | 0.058 ±0.005 | egernia-local-equalcpu |
| Q12 | 32 | 14.7 ±0.2 | 2.268 ±0.012 | 505.2 ±30.4 | 0.118 ±0.022 | egernia-local-equalcpu |
| Q13 | 1 | 2.7 ±0.0 | 0.421 ±0.004 | 4.4 ±0.1 | 0.311 ±0.005 | egernia-local-equalcpu |
| Q13 | 4 | 9.9 ±0.5 | 0.509 ±0.059 | 9.9 ±0.2 | 0.546 ±0.016 | tie |
| Q13 | 8 | 17.0 ±0.0 | 0.556 ±0.005 | 10.1 ±0.1 | 1.071 ±0.005 | argus-local |
| Q13 | 16 | 17.5 ±0.2 | 1.052 ±0.023 | 10.1 ±0.2 | 2.176 ±0.059 | argus-local |
| Q13 | 32 | 17.5 ±0.2 | 2.044 ±0.241 | 10.0 ±0.1 | 4.361 ±0.277 | argus-local |
| mix | 1 | 3.9 ±0.4 | 0.429 ±0.010 | 56.3 ±1.3 | 0.034 ±0.001 | egernia-local-equalcpu |
| mix | 4 | 14.0 ±0.6 | 0.526 ±0.009 | 172.8 ±10.0 | 0.044 ±0.002 | egernia-local-equalcpu |
| mix | 8 | 23.7 ±0.3 | 0.576 ±0.006 | 238.4 ±12.1 | 0.063 ±0.003 | egernia-local-equalcpu |
| mix | 16 | 24.6 ±0.3 | 1.006 ±0.011 | 285.2 ±8.9 | 0.106 ±0.004 | egernia-local-equalcpu |
| mix | 32 | 24.6 ±0.1 | 1.704 ±0.027 | 296.5 ±10.9 | 0.223 ±0.052 | egernia-local-equalcpu |

## resources, csv

| class | c | argus-local cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-local-equalcpu cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.64 | 8.0 ms | 5.44 | 5.52 | 0.90 | 5.3 ms | 3.21 | 3.27 |
| Q01 | 4 | 2.00 | 8.7 ms | 5.80 | 5.93 | 2.57 | 6.1 ms | 3.04 | 3.09 |
| Q01 | 8 | 3.76 | 9.4 ms | 5.93 | 5.93 | 4.31 | 6.7 ms | 2.87 | 2.95 |
| Q01 | 16 | 5.52 | 10.0 ms | 5.93 | 5.93 | 5.53 | 7.6 ms | 2.81 | 2.82 |
| Q01 | 32 | 5.63 | 10.2 ms | 5.93 | 5.94 | 6.24 | 8.4 ms | 2.83 | 2.85 |
| Q02 | 1 | 0.98 | 415.2 ms | 5.89 | 5.90 | 1.08 | 16.6 ms | 2.90 | 2.92 |
| Q02 | 4 | 3.96 | 439.8 ms | 5.91 | 5.92 | 3.29 | 18.4 ms | 2.91 | 2.95 |
| Q02 | 8 | 7.71 | 500.9 ms | 5.86 | 5.89 | 5.13 | 20.0 ms | 2.92 | 2.95 |
| Q02 | 16 | 7.92 | 508.5 ms | 5.77 | 5.81 | 6.80 | 21.9 ms | 2.94 | 2.96 |
| Q02 | 32 | 7.92 | 506.9 ms | 5.68 | 5.72 | 7.57 | 23.3 ms | 3.03 | 3.06 |
| Q03 | 1 | 0.85 | 22.5 ms | 5.62 | 5.68 | 1.06 | 30.2 ms | 3.01 | 3.03 |
| Q03 | 4 | 2.98 | 24.3 ms | 5.58 | 5.66 | 3.54 | 32.5 ms | 2.94 | 2.97 |
| Q03 | 8 | 4.91 | 26.0 ms | 5.84 | 5.94 | 5.94 | 36.2 ms | 2.89 | 2.90 |
| Q03 | 16 | 6.72 | 27.7 ms | 5.93 | 5.94 | 7.41 | 39.2 ms | 2.93 | 2.96 |
| Q03 | 32 | 6.87 | 28.0 ms | 5.93 | 5.94 | 7.97 | 41.4 ms | 3.02 | 3.04 |
| Q04 | 1 | 0.81 | 17.6 ms | 5.91 | 5.93 | 1.06 | 22.6 ms | 3.03 | 3.05 |
| Q04 | 4 | 2.82 | 19.1 ms | 5.90 | 5.93 | 3.36 | 24.0 ms | 2.98 | 3.00 |
| Q04 | 8 | 4.55 | 20.1 ms | 5.93 | 5.94 | 5.18 | 26.6 ms | 2.96 | 2.99 |
| Q04 | 16 | 6.17 | 21.1 ms | 5.93 | 5.94 | 7.07 | 29.1 ms | 2.97 | 3.00 |
| Q04 | 32 | 6.22 | 21.2 ms | 5.93 | 5.94 | 7.74 | 30.1 ms | 3.07 | 3.11 |
| Q05 | 1 | 1.00 | 431.2 ms | 5.90 | 5.91 | 0.96 | 9.3 ms | 3.09 | 3.11 |
| Q05 | 4 | 3.96 | 494.8 ms | 5.93 | 5.93 | 2.78 | 10.3 ms | 3.03 | 3.07 |
| Q05 | 8 | 7.75 | 548.5 ms | 5.90 | 5.91 | 4.14 | 11.3 ms | 2.97 | 2.99 |
| Q05 | 16 | 7.95 | 551.4 ms | 5.83 | 5.86 | 5.91 | 12.4 ms | 2.94 | 2.96 |
| Q05 | 32 | 7.95 | 553.0 ms | 5.75 | 5.79 | 6.71 | 13.4 ms | 3.01 | 3.04 |
| Q06 | 1 | 1.00 | 430.8 ms | 5.60 | 5.64 | 1.05 | 18.5 ms | 3.03 | 3.05 |
| Q06 | 4 | 3.93 | 487.9 ms | 5.59 | 5.61 | 3.28 | 20.1 ms | 2.98 | 3.00 |
| Q06 | 8 | 7.69 | 543.7 ms | 5.56 | 5.61 | 4.94 | 21.9 ms | 2.96 | 2.98 |
| Q06 | 16 | 7.91 | 547.6 ms | 5.47 | 5.52 | 6.83 | 24.1 ms | 2.97 | 3.01 |
| Q06 | 32 | 7.83 | 547.7 ms | 5.39 | 5.44 | 7.39 | 25.4 ms | 3.04 | 3.07 |
| Q07 | 1 | 0.99 | 316.0 ms | 5.24 | 5.30 | 1.00 | 12.9 ms | 3.05 | 3.07 |
| Q07 | 4 | 3.94 | 347.4 ms | 5.23 | 5.25 | 3.16 | 13.9 ms | 2.99 | 3.02 |
| Q07 | 8 | 7.59 | 383.6 ms | 5.26 | 5.28 | 4.53 | 15.1 ms | 2.95 | 2.98 |
| Q07 | 16 | 7.91 | 386.9 ms | 5.27 | 5.30 | 6.00 | 16.5 ms | 2.97 | 3.00 |
| Q07 | 32 | 7.91 | 386.7 ms | 5.29 | 5.32 | 7.32 | 17.9 ms | 3.06 | 3.11 |
| Q10 | 1 | 0.87 | 27.8 ms | 5.28 | 5.31 | 1.15 | 37.0 ms | 3.07 | 3.09 |
| Q10 | 4 | 2.80 | 30.7 ms | 5.51 | 5.63 | 3.83 | 41.8 ms | 3.02 | 3.07 |
| Q10 | 8 | 4.70 | 32.7 ms | 5.81 | 5.94 | 5.83 | 46.6 ms | 2.95 | 2.97 |
| Q10 | 16 | 5.92 | 34.0 ms | 5.93 | 5.94 | 7.54 | 51.4 ms | 2.96 | 2.99 |
| Q10 | 32 | 5.95 | 34.0 ms | 5.94 | 5.94 | 7.96 | 54.1 ms | 3.03 | 3.06 |
| Q11 | 1 | 1.03 | 182.1 ms | 5.91 | 5.93 | 0.83 | 284.1 ms | 3.03 | 3.05 |
| Q11 | 4 | 3.76 | 204.1 ms | 5.90 | 5.92 | 3.20 | 315.0 ms | 2.99 | 3.01 |
| Q11 | 8 | 5.82 | 219.0 ms | 5.81 | 5.85 | 5.63 | 356.2 ms | 2.97 | 2.98 |
| Q11 | 16 | 6.03 | 220.9 ms | 5.65 | 5.71 | 6.73 | 380.4 ms | 3.01 | 3.05 |
| Q11 | 32 | 6.09 | 222.7 ms | 5.49 | 5.52 | 7.30 | 395.3 ms | 3.13 | 3.19 |
| Q12 | 1 | 1.00 | 431.7 ms | 5.39 | 5.41 | 0.95 | 8.8 ms | 3.10 | 3.12 |
| Q12 | 4 | 3.95 | 471.4 ms | 5.40 | 5.41 | 2.94 | 9.7 ms | 3.05 | 3.07 |
| Q12 | 8 | 7.76 | 544.8 ms | 5.37 | 5.40 | 3.83 | 10.7 ms | 3.01 | 3.03 |
| Q12 | 16 | 7.95 | 545.5 ms | 5.31 | 5.32 | 5.85 | 11.7 ms | 3.00 | 3.00 |
| Q12 | 32 | 7.95 | 549.1 ms | 5.29 | 5.30 | 6.61 | 12.7 ms | 3.08 | 3.11 |
| Q13 | 1 | 1.00 | 378.0 ms | 5.23 | 5.24 | 2.84 | 675.1 ms | 3.11 | 3.13 |
| Q13 | 4 | 3.93 | 393.7 ms | 5.24 | 5.26 | 7.79 | 812.2 ms | 3.11 | 3.12 |
| Q13 | 8 | 7.68 | 460.6 ms | 5.26 | 5.28 | 7.99 | 822.8 ms | 3.12 | 3.16 |
| Q13 | 16 | 7.94 | 461.0 ms | 5.27 | 5.29 | 7.99 | 821.5 ms | 3.21 | 3.25 |
| Q13 | 32 | 7.95 | 460.7 ms | 5.29 | 5.30 | 8.00 | 829.4 ms | 3.43 | 3.50 |
| mix | 1 | 0.99 | 257.1 ms | 5.56 | 5.57 | 1.05 | 18.1 ms | 3.07 | 3.10 |
| mix | 4 | 3.93 | 285.5 ms | 5.59 | 5.60 | 3.35 | 19.7 ms | 3.08 | 3.13 |
| mix | 8 | 7.52 | 320.5 ms | 5.57 | 5.60 | 5.11 | 21.4 ms | 3.01 | 3.05 |
| mix | 16 | 7.87 | 323.7 ms | 5.54 | 5.56 | 6.72 | 23.4 ms | 3.04 | 3.08 |
| mix | 32 | 7.87 | 324.0 ms | 5.48 | 5.54 | 7.78 | 25.1 ms | 3.19 | 3.26 |

## resources, votable

| class | c | argus-local cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-local-equalcpu cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.66 | 7.9 ms | 1.40 | 1.44 | 0.90 | 5.4 ms | 3.12 | 3.17 |
| Q01 | 4 | 2.17 | 8.6 ms | 1.74 | 1.97 | 2.57 | 6.2 ms | 2.93 | 3.00 |
| Q01 | 8 | 3.70 | 9.3 ms | 2.36 | 2.66 | 3.95 | 6.9 ms | 2.74 | 2.79 |
| Q01 | 16 | 5.52 | 10.0 ms | 3.11 | 3.54 | 6.08 | 7.7 ms | 2.61 | 2.63 |
| Q01 | 32 | 5.68 | 10.2 ms | 3.83 | 4.01 | 6.31 | 8.4 ms | 2.64 | 2.66 |
| Q02 | 1 | 1.00 | 403.8 ms | 3.97 | 3.97 | 1.09 | 17.1 ms | 2.68 | 2.69 |
| Q02 | 4 | 3.96 | 447.6 ms | 3.94 | 3.97 | 3.36 | 19.0 ms | 2.70 | 2.72 |
| Q02 | 8 | 7.70 | 495.4 ms | 3.87 | 3.93 | 4.88 | 20.6 ms | 2.72 | 2.76 |
| Q02 | 16 | 7.91 | 499.2 ms | 3.78 | 3.81 | 6.97 | 22.7 ms | 2.73 | 2.74 |
| Q02 | 32 | 7.91 | 501.3 ms | 3.71 | 3.75 | 7.68 | 24.2 ms | 2.87 | 2.91 |
| Q03 | 1 | 0.85 | 22.6 ms | 3.60 | 3.64 | 1.06 | 30.8 ms | 2.85 | 2.88 |
| Q03 | 4 | 3.00 | 24.5 ms | 3.67 | 3.77 | 3.58 | 33.2 ms | 2.78 | 2.81 |
| Q03 | 8 | 5.11 | 26.2 ms | 3.98 | 4.12 | 5.99 | 36.9 ms | 2.72 | 2.74 |
| Q03 | 16 | 6.68 | 28.0 ms | 4.33 | 4.48 | 7.48 | 40.1 ms | 2.74 | 2.76 |
| Q03 | 32 | 6.67 | 28.1 ms | 4.57 | 4.64 | 7.97 | 42.2 ms | 2.80 | 2.82 |
| Q04 | 1 | 0.82 | 18.2 ms | 4.61 | 4.62 | 1.06 | 23.5 ms | 2.80 | 2.83 |
| Q04 | 4 | 2.83 | 19.9 ms | 4.60 | 4.62 | 3.48 | 25.1 ms | 2.74 | 2.77 |
| Q04 | 8 | 4.54 | 21.0 ms | 4.84 | 4.93 | 5.34 | 28.1 ms | 2.72 | 2.73 |
| Q04 | 16 | 6.10 | 22.0 ms | 5.02 | 5.10 | 6.76 | 30.2 ms | 2.77 | 2.79 |
| Q04 | 32 | 6.11 | 22.2 ms | 5.19 | 5.27 | 7.85 | 31.7 ms | 2.86 | 2.88 |
| Q05 | 1 | 1.00 | 423.1 ms | 5.23 | 5.23 | 0.96 | 9.6 ms | 2.86 | 2.89 |
| Q05 | 4 | 3.96 | 461.4 ms | 5.24 | 5.26 | 2.65 | 10.6 ms | 2.80 | 2.85 |
| Q05 | 8 | 7.74 | 540.2 ms | 5.20 | 5.26 | 4.02 | 11.5 ms | 2.74 | 2.76 |
| Q05 | 16 | 7.94 | 543.6 ms | 5.08 | 5.12 | 5.78 | 12.7 ms | 2.78 | 2.80 |
| Q05 | 32 | 7.94 | 544.3 ms | 4.98 | 5.02 | 6.73 | 13.7 ms | 2.85 | 2.86 |
| Q06 | 1 | 1.00 | 420.6 ms | 4.84 | 4.86 | 1.06 | 19.3 ms | 2.82 | 2.85 |
| Q06 | 4 | 3.96 | 456.0 ms | 4.83 | 4.86 | 3.39 | 21.0 ms | 2.78 | 2.81 |
| Q06 | 8 | 7.67 | 537.1 ms | 4.81 | 4.84 | 4.74 | 22.9 ms | 2.75 | 2.76 |
| Q06 | 16 | 7.89 | 541.4 ms | 4.73 | 4.75 | 6.40 | 24.8 ms | 2.79 | 2.81 |
| Q06 | 32 | 7.88 | 539.5 ms | 4.72 | 4.74 | 7.61 | 26.9 ms | 2.87 | 2.90 |
| Q07 | 1 | 0.99 | 308.0 ms | 4.66 | 4.68 | 1.00 | 13.1 ms | 2.87 | 2.90 |
| Q07 | 4 | 3.94 | 328.9 ms | 4.67 | 4.69 | 3.11 | 14.3 ms | 2.80 | 2.82 |
| Q07 | 8 | 7.56 | 375.4 ms | 4.70 | 4.73 | 4.47 | 15.5 ms | 2.77 | 2.79 |
| Q07 | 16 | 7.89 | 378.6 ms | 4.73 | 4.75 | 6.20 | 17.0 ms | 2.79 | 2.81 |
| Q07 | 32 | 7.85 | 378.5 ms | 4.75 | 4.77 | 7.34 | 18.4 ms | 2.89 | 2.93 |
| Q10 | 1 | 0.90 | 32.2 ms | 4.71 | 4.73 | 1.15 | 39.8 ms | 2.91 | 2.92 |
| Q10 | 4 | 3.06 | 36.0 ms | 4.90 | 4.99 | 3.75 | 45.3 ms | 2.85 | 2.90 |
| Q10 | 8 | 5.00 | 38.7 ms | 5.13 | 5.21 | 5.90 | 50.8 ms | 2.78 | 2.82 |
| Q10 | 16 | 6.00 | 40.3 ms | 5.28 | 5.34 | 7.58 | 56.1 ms | 2.79 | 2.81 |
| Q10 | 32 | 5.90 | 40.4 ms | 5.41 | 5.45 | 7.80 | 58.0 ms | 2.89 | 2.93 |
| Q11 | 1 | 1.03 | 227.5 ms | 5.40 | 5.41 | 0.59 | 329.9 ms | 2.91 | 2.93 |
| Q11 | 4 | 3.78 | 258.5 ms | 5.39 | 5.41 | 2.97 | 342.7 ms | 2.87 | 2.90 |
| Q11 | 8 | 5.91 | 283.9 ms | 5.33 | 5.36 | 5.66 | 389.2 ms | 2.82 | 2.85 |
| Q11 | 16 | 6.19 | 286.2 ms | 5.32 | 5.35 | 6.70 | 413.9 ms | 2.88 | 2.93 |
| Q11 | 32 | 6.24 | 288.6 ms | 5.31 | 5.33 | 7.48 | 436.8 ms | 3.00 | 3.07 |
| Q12 | 1 | 1.00 | 423.0 ms | 5.26 | 5.27 | 0.95 | 8.9 ms | 2.95 | 2.95 |
| Q12 | 4 | 3.96 | 455.3 ms | 5.27 | 5.28 | 2.76 | 9.9 ms | 2.90 | 2.92 |
| Q12 | 8 | 7.75 | 537.4 ms | 5.25 | 5.28 | 4.48 | 10.8 ms | 2.85 | 2.89 |
| Q12 | 16 | 7.84 | 539.6 ms | 5.26 | 5.27 | 5.58 | 11.9 ms | 2.85 | 2.86 |
| Q12 | 32 | 7.95 | 541.4 ms | 5.25 | 5.26 | 6.52 | 12.9 ms | 2.91 | 2.94 |
| Q13 | 1 | 1.00 | 368.9 ms | 5.21 | 5.21 | 2.86 | 643.1 ms | 2.95 | 2.97 |
| Q13 | 4 | 3.95 | 397.7 ms | 5.22 | 5.22 | 7.79 | 786.3 ms | 2.96 | 2.99 |
| Q13 | 8 | 7.68 | 453.0 ms | 5.25 | 5.25 | 7.98 | 791.6 ms | 2.98 | 3.00 |
| Q13 | 16 | 7.94 | 454.2 ms | 5.26 | 5.27 | 8.00 | 793.0 ms | 3.08 | 3.10 |
| Q13 | 32 | 7.94 | 454.1 ms | 5.57 | 5.61 | 8.00 | 801.6 ms | 3.30 | 3.35 |
| mix | 1 | 1.02 | 262.4 ms | 1.04 | 1.05 | 1.06 | 18.8 ms | 2.68 | 2.72 |
| mix | 4 | 3.96 | 283.6 ms | 1.12 | 1.23 | 3.49 | 20.2 ms | 2.65 | 2.66 |
| mix | 8 | 7.50 | 316.8 ms | 1.25 | 1.27 | 5.30 | 22.3 ms | 2.72 | 2.77 |
| mix | 16 | 7.85 | 320.0 ms | 1.30 | 1.33 | 6.94 | 24.3 ms | 2.85 | 2.91 |
| mix | 32 | 7.84 | 319.7 ms | 1.37 | 1.40 | 7.70 | 26.0 ms | 3.08 | 3.16 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | argus-local | — | 3.9 | 0.99 | 3.9 | 257.1 |
| csv | 1 | egernia-local-equalcpu | 8 | 57.9 | 1.05 | 55.2 | 18.1 |
| csv | 4 | argus-local | — | 13.8 | 3.93 | 3.5 | 285.5 |
| csv | 4 | egernia-local-equalcpu | 8 | 170.2 | 3.35 | 50.8 | 19.7 |
| csv | 8 | argus-local | — | 23.5 | 7.52 | 3.1 | 320.5 |
| csv | 8 | egernia-local-equalcpu | 8 | 238.6 | 5.11 | 46.7 | 21.4 |
| csv | 16 | argus-local | — | 24.4 | 7.87 | 3.1 | 323.7 |
| csv | 16 | egernia-local-equalcpu | 8 | 287.3 | 6.72 | 42.8 | 23.4 |
| csv | 32 | argus-local | — | 24.4 | 7.87 | 3.1 | 324.0 |
| csv | 32 | egernia-local-equalcpu | 8 | 310.0 | 7.78 | 39.8 | 25.1 |
| votable | 1 | argus-local | — | 3.9 | 1.02 | 3.8 | 262.4 |
| votable | 1 | egernia-local-equalcpu | 8 | 56.3 | 1.06 | 53.3 | 18.8 |
| votable | 4 | argus-local | — | 14.0 | 3.96 | 3.5 | 283.6 |
| votable | 4 | egernia-local-equalcpu | 8 | 172.8 | 3.49 | 49.5 | 20.2 |
| votable | 8 | argus-local | — | 23.7 | 7.50 | 3.2 | 316.8 |
| votable | 8 | egernia-local-equalcpu | 8 | 238.4 | 5.30 | 45.0 | 22.3 |
| votable | 16 | argus-local | — | 24.6 | 7.85 | 3.1 | 320.0 |
| votable | 16 | egernia-local-equalcpu | 8 | 285.2 | 6.94 | 41.1 | 24.3 |
| votable | 32 | argus-local | — | 24.6 | 7.84 | 3.1 | 319.7 |
| votable | 32 | egernia-local-equalcpu | 8 | 296.5 | 7.70 | 38.5 | 26.0 |

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
docker compose -f benchmarks/tap-compare/docker-compose.argus.yml up -d --build
docker compose -f docker-compose.yml \
    -f benchmarks/tap-compare/argus-equal-cpu/egernia-equalcpu.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets argus-local egernia-local-equalcpu --scenario <scenario>
```

Environment: see `environment.json` (git f1cf2c25, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **Shapes.** egernia `main` f1cf2c2 with `TAP_API_WORKERS=8` in the unchanged 8 CPU / 8 GiB pin (`argus-equal-cpu/egernia-equalcpu.yml`; PostgreSQL parallel budget re-derived for the pool total); CADC argus 1.0.27 unchanged from the one-process run, on its own eight cores (`argus-equal-cpu/argus-disjoint.yml`) with an empty UWS job store at the start, per Amendment 1 of `benchmarks/tap-compare/argus-equal-cpu/PROTOCOL.md` (tag `tap-compare-argus-equalcpu-prereg-v2`). Resource telemetry from the first rung.
- **Gates.** egernia taplint 0 errors; argus 0 blocking / 2 total (TAP_UPLOAD-by-URL, not in the workload); agreement 11/11 classes.
- **Verdicts.** egernia 69, argus 32, ties 19 of 120; no rung over 1% errors on either side.
- **Where each wins.** With equal CPU egernia takes the metadata class (Q01: 741 vs 552 rps at c=32), every cone class, the DID lookup and the mix (310 vs 24 rps at c=32, on 7.8 cores each: 25 ms vs 324 ms of CPU per request). argus keeps the small-indexed-result classes Q03, Q04 and Q10 by 15–25%, and the two scan-heavy classes clearly: Q11 (10,000-row results) 27.4 vs 18.5 rps and Q13 (the aggregate) 17.3 vs 9.7 rps at c=32. Those two did not move between one and eight egernia workers, so they are bound in PostgreSQL within the pin: egernia's `ivoa.obscore` is a live view over the ODP model (a 559 MB table joined to observations, with a per-row lookup for the access columns), argus scans a flat 372 MB ObsCore table.
- **Conditions.** Interleaved A/B rungs, 30.7 h (2026-09-08 06:18Z → 09-09 12:58Z), the two stacks on disjoint cpusets (0–7 / 8–15), generators on 24–29, nothing else on the host.

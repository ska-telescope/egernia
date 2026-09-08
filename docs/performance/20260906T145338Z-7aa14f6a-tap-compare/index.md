# 20260906T145338Z-7aa14f6a-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: argus in `benchmarks/tap-compare/docker-compose.argus.yml` (shared `cpuset` of 8 cores; 8 GiB split 3 Tomcat / 5 PostgreSQL; `benchmarks/tap-compare/argus/PROTOCOL.md`); egernia in `benchmarks/tap-compare/docker-compose.egernia-pins.yml` (shared `cpuset` of 8 cores; 8 GiB split 4 db / 2 api / 2 executor).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-local | 1.1 | PASS (2 errors) | 134217728 |
| egernia-local | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | argus-local rps | argus-local p95 (s) | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 79.0 ±10.8 | 0.015 ±0.000 | 165.8 ±1.0 | 0.008 ±0.000 | egernia-local |
| Q01 | 4 | 239.8 ±74.6 | 0.019 ±0.000 | 203.2 ±0.5 | 0.028 ±0.000 | tie |
| Q01 | 8 | 410.9 ±5.2 | 0.024 ±0.000 | 192.8 ±0.5 | 0.059 ±0.001 | argus-local |
| Q01 | 16 | 555.9 ±14.2 | 0.036 ±0.001 | 185.9 ±1.3 | 0.114 ±0.001 | argus-local |
| Q01 | 32 | 544.1 ±14.7 | 0.070 ±0.003 | 175.3 ±1.5 | 0.225 ±0.005 | argus-local |
| Q02 | 1 | 2.3 ±0.0 | 0.445 ±0.008 | 64.7 ±0.6 | 0.024 ±0.000 | egernia-local |
| Q02 | 4 | 8.7 ±0.9 | 0.513 ±0.024 | 138.8 ±2.2 | 0.042 ±0.001 | egernia-local |
| Q02 | 8 | 15.0 ±0.1 | 0.579 ±0.003 | 152.4 ±0.3 | 0.073 ±0.001 | egernia-local |
| Q02 | 16 | 15.2 ±0.1 | 1.137 ±0.020 | 148.4 ±1.5 | 0.141 ±0.001 | egernia-local |
| Q02 | 32 | 15.2 ±0.1 | 2.209 ±0.014 | 140.8 ±0.9 | 0.277 ±0.001 | egernia-local |
| Q03 | 1 | 37.5 ±0.2 | 0.088 ±0.000 | 34.4 ±0.5 | 0.125 ±0.001 | tie |
| Q03 | 4 | 121.1 ±19.7 | 0.102 ±0.000 | 103.2 ±2.3 | 0.156 ±0.003 | tie |
| Q03 | 8 | 187.1 ±16.4 | 0.123 ±0.001 | 138.0 ±0.9 | 0.190 ±0.002 | argus-local |
| Q03 | 16 | 240.9 ±7.1 | 0.180 ±0.005 | 135.3 ±1.0 | 0.256 ±0.002 | argus-local |
| Q03 | 32 | 243.0 ±3.0 | 0.251 ±0.004 | 129.0 ±1.8 | 0.388 ±0.003 | argus-local |
| Q04 | 1 | 46.2 ±3.2 | 0.025 ±0.000 | 46.5 ±0.2 | 0.026 ±0.001 | tie |
| Q04 | 4 | 144.7 ±14.8 | 0.033 ±0.003 | 114.2 ±1.4 | 0.046 ±0.001 | argus-local |
| Q04 | 8 | 229.6 ±1.7 | 0.043 ±0.000 | 133.3 ±0.3 | 0.080 ±0.001 | argus-local |
| Q04 | 16 | 293.1 ±2.6 | 0.070 ±0.001 | 135.6 ±0.6 | 0.151 ±0.002 | argus-local |
| Q04 | 32 | 291.7 ±2.3 | 0.129 ±0.003 | 128.1 ±0.4 | 0.301 ±0.001 | argus-local |
| Q05 | 1 | 2.3 ±0.0 | 0.455 ±0.007 | 101.0 ±0.8 | 0.013 ±0.000 | egernia-local |
| Q05 | 4 | 8.2 ±0.2 | 0.560 ±0.005 | 179.5 ±1.5 | 0.032 ±0.001 | egernia-local |
| Q05 | 8 | 13.7 ±0.9 | 0.630 ±0.028 | 176.4 ±5.9 | 0.065 ±0.005 | egernia-local |
| Q05 | 16 | 14.1 ±0.1 | 1.245 ±0.038 | 169.2 ±1.4 | 0.124 ±0.002 | egernia-local |
| Q05 | 32 | 14.1 ±0.1 | 2.398 ±0.018 | 159.7 ±0.1 | 0.248 ±0.001 | egernia-local |
| Q06 | 1 | 2.3 ±0.0 | 0.454 ±0.006 | 56.8 ±0.4 | 0.024 ±0.000 | egernia-local |
| Q06 | 4 | 8.6 ±0.7 | 0.561 ±0.016 | 129.4 ±1.6 | 0.044 ±0.000 | egernia-local |
| Q06 | 8 | 14.0 ±0.1 | 0.635 ±0.010 | 140.7 ±1.3 | 0.079 ±0.001 | egernia-local |
| Q06 | 16 | 14.2 ±0.2 | 1.244 ±0.082 | 137.2 ±0.9 | 0.152 ±0.000 | egernia-local |
| Q06 | 32 | 14.2 ±0.0 | 2.388 ±0.025 | 129.6 ±1.3 | 0.303 ±0.006 | egernia-local |
| Q07 | 1 | 3.2 ±0.2 | 0.433 ±0.005 | 77.6 ±0.7 | 0.018 ±0.000 | egernia-local |
| Q07 | 4 | 11.3 ±0.0 | 0.512 ±0.005 | 160.4 ±1.7 | 0.036 ±0.000 | egernia-local |
| Q07 | 8 | 19.5 ±0.1 | 0.577 ±0.002 | 165.8 ±1.6 | 0.068 ±0.001 | egernia-local |
| Q07 | 16 | 20.0 ±0.2 | 1.012 ±0.006 | 157.8 ±1.8 | 0.133 ±0.003 | egernia-local |
| Q07 | 32 | 20.1 ±0.1 | 1.853 ±0.021 | 149.5 ±0.6 | 0.264 ±0.004 | egernia-local |
| Q10 | 1 | 31.3 ±1.8 | 0.036 ±0.000 | 30.5 ±0.1 | 0.039 ±0.001 | tie |
| Q10 | 4 | 89.4 ±17.4 | 0.048 ±0.000 | 76.3 ±1.0 | 0.069 ±0.001 | tie |
| Q10 | 8 | 141.7 ±14.2 | 0.066 ±0.001 | 87.7 ±1.5 | 0.117 ±0.002 | argus-local |
| Q10 | 16 | 175.5 ±1.3 | 0.115 ±0.001 | 87.3 ±1.9 | 0.235 ±0.006 | argus-local |
| Q10 | 32 | 173.7 ±0.6 | 0.211 ±0.002 | 84.4 ±0.4 | 0.455 ±0.002 | argus-local |
| Q11 | 1 | 5.7 ±0.0 | 0.188 ±0.002 | 4.3 ±0.1 | 0.258 ±0.011 | argus-local |
| Q11 | 4 | 18.4 ±0.1 | 0.243 ±0.004 | 11.3 ±0.2 | 0.491 ±0.044 | argus-local |
| Q11 | 8 | 26.0 ±1.7 | 0.350 ±0.003 | 15.1 ±0.1 | 0.654 ±0.031 | argus-local |
| Q11 | 16 | 27.2 ±0.1 | 0.668 ±0.008 | 16.5 ±0.1 | 1.191 ±0.020 | argus-local |
| Q11 | 32 | 27.2 ±0.1 | 1.263 ±0.009 | 16.3 ±0.3 | 2.360 ±0.153 | argus-local |
| Q12 | 1 | 2.3 ±0.0 | 0.456 ±0.002 | 106.3 ±1.5 | 0.013 ±0.000 | egernia-local |
| Q12 | 4 | 8.3 ±0.8 | 0.561 ±0.008 | 183.0 ±1.5 | 0.031 ±0.000 | egernia-local |
| Q12 | 8 | 13.9 ±0.1 | 0.622 ±0.009 | 180.6 ±1.1 | 0.062 ±0.001 | egernia-local |
| Q12 | 16 | 14.2 ±0.0 | 1.243 ±0.013 | 170.7 ±2.7 | 0.124 ±0.002 | egernia-local |
| Q12 | 32 | 14.1 ±0.0 | 2.430 ±0.113 | 160.8 ±1.4 | 0.245 ±0.001 | egernia-local |
| Q13 | 1 | 2.6 ±0.0 | 0.437 ±0.008 | 4.2 ±0.1 | 0.328 ±0.004 | egernia-local |
| Q13 | 4 | 9.6 ±0.5 | 0.515 ±0.046 | 9.5 ±0.1 | 0.562 ±0.003 | tie |
| Q13 | 8 | 16.3 ±0.1 | 0.586 ±0.005 | 9.8 ±0.1 | 1.103 ±0.009 | argus-local |
| Q13 | 16 | 16.8 ±0.2 | 1.097 ±0.005 | 9.8 ±0.2 | 1.970 ±0.017 | argus-local |
| Q13 | 32 | 16.7 ±0.2 | 2.095 ±0.052 | 9.8 ±0.1 | 3.683 ±0.053 | argus-local |
| mix | 1 | 3.8 ±0.2 | 0.437 ±0.005 | 57.1 ±1.0 | 0.032 ±0.001 | egernia-local |
| mix | 4 | 14.0 ±1.8 | 0.512 ±0.105 | 141.2 ±0.9 | 0.049 ±0.001 | egernia-local |
| mix | 8 | 23.1 ±0.5 | 0.597 ±0.007 | 152.3 ±0.9 | 0.082 ±0.003 | egernia-local |
| mix | 16 | 24.0 ±0.2 | 1.034 ±0.007 | 146.1 ±1.9 | 0.158 ±0.005 | egernia-local |
| mix | 32 | 23.6 ±1.3 | 1.776 ±0.068 | 138.6 ±0.6 | 0.315 ±0.008 | egernia-local |

## votable

| class | c | argus-local rps | argus-local p95 (s) | egernia-local rps | egernia-local p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 84.4 ±0.4 | 0.015 ±0.000 | 162.9 ±1.0 | 0.008 ±0.000 | egernia-local |
| Q01 | 4 | 255.4 ±8.1 | 0.019 ±0.000 | 201.2 ±0.3 | 0.029 ±0.000 | argus-local |
| Q01 | 8 | 403.9 ±15.6 | 0.024 ±0.000 | 191.0 ±1.2 | 0.059 ±0.001 | argus-local |
| Q01 | 16 | 512.7 ±159.0 | 0.040 ±0.021 | 184.7 ±1.0 | 0.114 ±0.001 | argus-local |
| Q01 | 32 | 552.2 ±16.7 | 0.068 ±0.000 | 174.3 ±0.2 | 0.227 ±0.003 | argus-local |
| Q02 | 1 | 2.4 ±0.1 | 0.427 ±0.010 | 63.4 ±0.2 | 0.024 ±0.001 | egernia-local |
| Q02 | 4 | 8.9 ±0.3 | 0.506 ±0.001 | 136.5 ±1.6 | 0.042 ±0.001 | egernia-local |
| Q02 | 8 | 15.3 ±0.0 | 0.567 ±0.006 | 150.3 ±0.5 | 0.074 ±0.001 | egernia-local |
| Q02 | 16 | 15.5 ±0.3 | 1.121 ±0.046 | 146.1 ±1.1 | 0.143 ±0.002 | egernia-local |
| Q02 | 32 | 15.5 ±0.1 | 2.176 ±0.013 | 138.4 ±1.1 | 0.282 ±0.003 | egernia-local |
| Q03 | 1 | 37.3 ±1.0 | 0.085 ±0.001 | 34.3 ±0.6 | 0.124 ±0.001 | tie |
| Q03 | 4 | 123.0 ±4.4 | 0.100 ±0.001 | 102.8 ±1.8 | 0.154 ±0.003 | argus-local |
| Q03 | 8 | 193.7 ±1.6 | 0.120 ±0.001 | 136.6 ±1.3 | 0.189 ±0.000 | argus-local |
| Q03 | 16 | 234.6 ±8.6 | 0.180 ±0.006 | 133.4 ±0.1 | 0.255 ±0.000 | argus-local |
| Q03 | 32 | 213.3 ±101.3 | 0.394 ±0.617 | 126.9 ±2.0 | 0.391 ±0.007 | tie |
| Q04 | 1 | 45.7 ±0.4 | 0.026 ±0.000 | 44.7 ±0.4 | 0.027 ±0.001 | tie |
| Q04 | 4 | 143.5 ±1.6 | 0.034 ±0.000 | 108.8 ±0.7 | 0.049 ±0.001 | argus-local |
| Q04 | 8 | 219.0 ±8.3 | 0.045 ±0.000 | 126.7 ±0.6 | 0.083 ±0.000 | argus-local |
| Q04 | 16 | 276.2 ±4.0 | 0.074 ±0.001 | 129.0 ±0.0 | 0.159 ±0.001 | argus-local |
| Q04 | 32 | 274.1 ±2.8 | 0.136 ±0.001 | 122.4 ±0.4 | 0.315 ±0.002 | argus-local |
| Q05 | 1 | 2.3 ±0.0 | 0.446 ±0.005 | 99.6 ±0.4 | 0.013 ±0.000 | egernia-local |
| Q05 | 4 | 8.6 ±0.7 | 0.553 ±0.004 | 176.6 ±2.0 | 0.033 ±0.000 | egernia-local |
| Q05 | 8 | 14.1 ±0.0 | 0.618 ±0.006 | 175.4 ±0.5 | 0.064 ±0.001 | egernia-local |
| Q05 | 16 | 14.3 ±0.1 | 1.222 ±0.029 | 166.3 ±0.5 | 0.126 ±0.002 | egernia-local |
| Q05 | 32 | 14.3 ±0.1 | 2.367 ±0.013 | 157.8 ±0.6 | 0.250 ±0.002 | egernia-local |
| Q06 | 1 | 2.4 ±0.0 | 0.449 ±0.014 | 54.9 ±0.3 | 0.025 ±0.000 | egernia-local |
| Q06 | 4 | 8.5 ±1.6 | 0.528 ±0.146 | 125.9 ±3.1 | 0.046 ±0.001 | egernia-local |
| Q06 | 8 | 14.0 ±0.1 | 0.627 ±0.008 | 136.4 ±0.9 | 0.081 ±0.001 | egernia-local |
| Q06 | 16 | 14.3 ±0.1 | 1.224 ±0.008 | 132.6 ±0.9 | 0.159 ±0.003 | egernia-local |
| Q06 | 32 | 14.3 ±0.1 | 2.374 ±0.011 | 125.8 ±1.3 | 0.312 ±0.005 | egernia-local |
| Q07 | 1 | 3.2 ±0.1 | 0.432 ±0.003 | 75.9 ±0.3 | 0.019 ±0.000 | egernia-local |
| Q07 | 4 | 11.9 ±0.8 | 0.476 ±0.048 | 157.9 ±1.0 | 0.037 ±0.000 | egernia-local |
| Q07 | 8 | 19.7 ±0.1 | 0.571 ±0.005 | 163.2 ±0.4 | 0.069 ±0.000 | egernia-local |
| Q07 | 16 | 20.4 ±0.0 | 1.001 ±0.007 | 156.6 ±1.1 | 0.134 ±0.001 | egernia-local |
| Q07 | 32 | 20.2 ±0.7 | 1.848 ±0.086 | 148.4 ±0.4 | 0.266 ±0.004 | egernia-local |
| Q10 | 1 | 28.0 ±1.1 | 0.041 ±0.000 | 28.6 ±0.3 | 0.042 ±0.001 | tie |
| Q10 | 4 | 88.3 ±4.9 | 0.054 ±0.000 | 71.0 ±0.6 | 0.074 ±0.001 | argus-local |
| Q10 | 8 | 132.3 ±4.4 | 0.076 ±0.001 | 82.3 ±0.5 | 0.124 ±0.001 | argus-local |
| Q10 | 16 | 148.1 ±2.5 | 0.136 ±0.000 | 82.2 ±0.2 | 0.250 ±0.001 | argus-local |
| Q10 | 32 | 146.7 ±0.5 | 0.249 ±0.001 | 79.4 ±0.2 | 0.483 ±0.004 | argus-local |
| Q11 | 1 | 4.6 ±0.0 | 0.233 ±0.003 | 4.1 ±0.0 | 0.271 ±0.005 | argus-local |
| Q11 | 4 | 14.7 ±0.0 | 0.306 ±0.004 | 10.9 ±0.1 | 0.465 ±0.036 | argus-local |
| Q11 | 8 | 21.2 ±0.1 | 0.440 ±0.002 | 13.9 ±0.5 | 0.681 ±0.024 | argus-local |
| Q11 | 16 | 21.7 ±0.1 | 0.834 ±0.003 | 15.0 ±0.2 | 1.256 ±0.020 | argus-local |
| Q11 | 32 | 21.7 ±0.0 | 1.579 ±0.002 | 14.8 ±0.1 | 2.488 ±0.078 | argus-local |
| Q12 | 1 | 2.3 ±0.0 | 0.444 ±0.006 | 105.2 ±0.4 | 0.013 ±0.000 | egernia-local |
| Q12 | 4 | 8.5 ±0.3 | 0.551 ±0.005 | 182.0 ±1.4 | 0.032 ±0.000 | egernia-local |
| Q12 | 8 | 14.2 ±0.1 | 0.612 ±0.006 | 179.0 ±0.6 | 0.063 ±0.001 | egernia-local |
| Q12 | 16 | 14.4 ±0.0 | 1.212 ±0.008 | 170.3 ±0.8 | 0.124 ±0.002 | egernia-local |
| Q12 | 32 | 14.4 ±0.1 | 2.342 ±0.020 | 160.5 ±1.0 | 0.246 ±0.005 | egernia-local |
| Q13 | 1 | 2.7 ±0.0 | 0.420 ±0.010 | 4.2 ±0.1 | 0.326 ±0.003 | egernia-local |
| Q13 | 4 | 10.3 ±0.9 | 0.461 ±0.116 | 9.6 ±0.2 | 0.559 ±0.012 | tie |
| Q13 | 8 | 16.7 ±0.1 | 0.570 ±0.007 | 9.8 ±0.1 | 1.095 ±0.026 | argus-local |
| Q13 | 16 | 17.2 ±0.1 | 1.075 ±0.011 | 9.8 ±0.1 | 1.974 ±0.014 | argus-local |
| Q13 | 32 | 17.2 ±0.1 | 2.034 ±0.007 | 9.8 ±0.1 | 3.656 ±0.042 | argus-local |
| mix | 1 | 3.8 ±0.3 | 0.438 ±0.003 | 55.9 ±0.8 | 0.034 ±0.001 | egernia-local |
| mix | 4 | 13.9 ±0.1 | 0.531 ±0.007 | 139.6 ±2.0 | 0.052 ±0.001 | egernia-local |
| mix | 8 | 23.3 ±0.3 | 0.595 ±0.009 | 147.7 ±1.5 | 0.087 ±0.002 | egernia-local |
| mix | 16 | 24.0 ±0.3 | 1.029 ±0.016 | 142.1 ±0.9 | 0.169 ±0.002 | egernia-local |
| mix | 32 | 24.1 ±0.3 | 1.752 ±0.026 | 134.6 ±0.7 | 0.324 ±0.008 | egernia-local |

## resources, csv

| class | c | argus-local cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.61 | 7.8 ms | 5.42 | 5.51 | 0.87 | 5.2 ms | 1.61 | 1.62 |
| Q01 | 4 | 2.06 | 8.6 ms | 5.88 | 5.99 | 1.38 | 6.8 ms | 1.56 | 1.58 |
| Q01 | 8 | 3.80 | 9.2 ms | 5.99 | 5.99 | 1.43 | 7.4 ms | 1.55 | 1.57 |
| Q01 | 16 | 5.52 | 9.9 ms | 5.99 | 5.99 | 1.42 | 7.6 ms | 1.54 | 1.56 |
| Q01 | 32 | 5.50 | 10.1 ms | 6.00 | 6.01 | 1.41 | 8.0 ms | 1.54 | 1.55 |
| Q02 | 1 | 1.00 | 426.5 ms | 5.97 | 5.97 | 1.06 | 16.4 ms | 1.58 | 1.59 |
| Q02 | 4 | 3.95 | 456.0 ms | 5.98 | 6.00 | 2.57 | 18.6 ms | 1.57 | 1.59 |
| Q02 | 8 | 7.62 | 509.9 ms | 5.94 | 5.97 | 3.00 | 19.7 ms | 1.58 | 1.59 |
| Q02 | 16 | 7.83 | 514.6 ms | 5.85 | 5.90 | 2.97 | 20.0 ms | 1.58 | 1.60 |
| Q02 | 32 | 7.82 | 515.0 ms | 5.76 | 5.80 | 2.88 | 20.4 ms | 1.58 | 1.59 |
| Q03 | 1 | 0.85 | 22.6 ms | 5.56 | 5.65 | 1.03 | 30.0 ms | 1.58 | 1.60 |
| Q03 | 4 | 2.95 | 24.3 ms | 5.49 | 5.56 | 3.38 | 32.7 ms | 1.57 | 1.58 |
| Q03 | 8 | 4.91 | 26.2 ms | 5.76 | 5.91 | 4.96 | 36.0 ms | 1.58 | 1.58 |
| Q03 | 16 | 6.71 | 27.9 ms | 5.94 | 5.94 | 4.99 | 36.9 ms | 1.58 | 1.59 |
| Q03 | 32 | 6.79 | 28.0 ms | 5.94 | 5.94 | 4.81 | 37.3 ms | 1.58 | 1.59 |
| Q04 | 1 | 0.80 | 17.3 ms | 5.91 | 5.93 | 1.04 | 22.3 ms | 1.59 | 1.59 |
| Q04 | 4 | 2.75 | 19.0 ms | 5.90 | 5.94 | 2.77 | 24.2 ms | 1.59 | 1.60 |
| Q04 | 8 | 4.57 | 19.9 ms | 5.94 | 5.95 | 3.50 | 26.3 ms | 1.60 | 1.61 |
| Q04 | 16 | 6.07 | 20.7 ms | 5.94 | 5.95 | 3.53 | 26.0 ms | 1.60 | 1.60 |
| Q04 | 32 | 6.10 | 20.9 ms | 5.94 | 5.95 | 3.39 | 26.4 ms | 1.60 | 1.62 |
| Q05 | 1 | 1.00 | 436.6 ms | 5.90 | 5.91 | 0.93 | 9.2 ms | 1.61 | 1.62 |
| Q05 | 4 | 3.96 | 486.8 ms | 5.91 | 5.92 | 1.90 | 10.6 ms | 1.59 | 1.60 |
| Q05 | 8 | 7.53 | 550.2 ms | 5.90 | 5.92 | 2.03 | 11.5 ms | 1.60 | 1.62 |
| Q05 | 16 | 7.83 | 556.2 ms | 5.82 | 5.86 | 2.01 | 11.9 ms | 1.60 | 1.61 |
| Q05 | 32 | 7.84 | 557.8 ms | 5.73 | 5.77 | 1.96 | 12.2 ms | 1.60 | 1.60 |
| Q06 | 1 | 1.00 | 428.6 ms | 5.58 | 5.61 | 1.03 | 18.2 ms | 1.61 | 1.62 |
| Q06 | 4 | 3.95 | 458.2 ms | 5.58 | 5.59 | 2.62 | 20.2 ms | 1.60 | 1.60 |
| Q06 | 8 | 7.59 | 544.3 ms | 5.56 | 5.58 | 3.03 | 21.5 ms | 1.61 | 1.63 |
| Q06 | 16 | 7.80 | 550.7 ms | 5.49 | 5.53 | 2.97 | 21.7 ms | 1.61 | 1.62 |
| Q06 | 32 | 7.80 | 550.7 ms | 5.38 | 5.43 | 2.86 | 22.1 ms | 1.62 | 1.63 |
| Q07 | 1 | 0.99 | 313.3 ms | 5.23 | 5.27 | 0.98 | 12.6 ms | 1.62 | 1.62 |
| Q07 | 4 | 3.94 | 348.4 ms | 5.23 | 5.26 | 2.25 | 14.1 ms | 1.61 | 1.61 |
| Q07 | 8 | 7.50 | 385.9 ms | 5.22 | 5.26 | 2.50 | 15.0 ms | 1.62 | 1.63 |
| Q07 | 16 | 7.80 | 390.4 ms | 5.23 | 5.25 | 2.45 | 15.5 ms | 1.62 | 1.64 |
| Q07 | 32 | 7.81 | 390.2 ms | 5.25 | 5.27 | 2.38 | 15.9 ms | 1.63 | 1.64 |
| Q10 | 1 | 0.87 | 27.8 ms | 5.22 | 5.26 | 1.12 | 36.9 ms | 1.62 | 1.63 |
| Q10 | 4 | 2.73 | 30.5 ms | 5.43 | 5.56 | 3.25 | 42.6 ms | 1.61 | 1.62 |
| Q10 | 8 | 4.62 | 32.6 ms | 5.85 | 5.94 | 3.96 | 45.1 ms | 1.62 | 1.62 |
| Q10 | 16 | 5.91 | 33.7 ms | 5.94 | 5.95 | 3.83 | 43.9 ms | 1.63 | 1.64 |
| Q10 | 32 | 5.85 | 33.7 ms | 5.94 | 5.95 | 3.72 | 44.1 ms | 1.63 | 1.63 |
| Q11 | 1 | 1.03 | 181.5 ms | 5.90 | 5.91 | 1.21 | 277.1 ms | 1.63 | 1.64 |
| Q11 | 4 | 3.73 | 202.7 ms | 5.88 | 5.90 | 3.68 | 325.8 ms | 1.63 | 1.65 |
| Q11 | 8 | 5.66 | 217.5 ms | 5.79 | 5.84 | 5.39 | 357.7 ms | 1.65 | 1.67 |
| Q11 | 16 | 5.94 | 219.0 ms | 5.67 | 5.69 | 5.76 | 349.2 ms | 1.67 | 1.69 |
| Q11 | 32 | 6.00 | 220.8 ms | 5.63 | 5.65 | 5.65 | 346.7 ms | 1.70 | 1.72 |
| Q12 | 1 | 1.00 | 439.3 ms | 5.57 | 5.59 | 0.93 | 8.7 ms | 1.66 | 1.67 |
| Q12 | 4 | 3.93 | 472.3 ms | 5.58 | 5.59 | 1.85 | 10.1 ms | 1.65 | 1.66 |
| Q12 | 8 | 7.65 | 551.4 ms | 5.55 | 5.58 | 1.97 | 10.9 ms | 1.65 | 1.67 |
| Q12 | 16 | 7.85 | 555.7 ms | 5.53 | 5.54 | 1.94 | 11.4 ms | 1.65 | 1.66 |
| Q12 | 32 | 7.85 | 558.9 ms | 5.54 | 5.55 | 1.89 | 11.8 ms | 1.65 | 1.66 |
| Q13 | 1 | 1.00 | 382.8 ms | 5.46 | 5.47 | 2.83 | 682.5 ms | 1.68 | 1.69 |
| Q13 | 4 | 3.95 | 411.2 ms | 5.48 | 5.49 | 7.76 | 815.0 ms | 1.71 | 1.72 |
| Q13 | 8 | 7.59 | 466.6 ms | 5.50 | 5.51 | 7.97 | 817.8 ms | 1.75 | 1.77 |
| Q13 | 16 | 7.84 | 467.3 ms | 5.52 | 5.52 | 7.97 | 815.5 ms | 1.75 | 1.76 |
| Q13 | 32 | 7.80 | 469.3 ms | 5.53 | 5.54 | 7.97 | 818.1 ms | 1.75 | 1.77 |
| mix | 1 | 0.99 | 258.2 ms | 5.21 | 5.22 | 1.03 | 18.0 ms | 1.59 | 1.60 |
| mix | 4 | 3.93 | 280.9 ms | 5.25 | 5.26 | 2.77 | 19.6 ms | 1.59 | 1.60 |
| mix | 8 | 7.43 | 322.1 ms | 5.29 | 5.32 | 3.20 | 21.0 ms | 1.61 | 1.62 |
| mix | 16 | 7.78 | 325.7 ms | 5.33 | 5.34 | 3.14 | 21.5 ms | 1.60 | 1.62 |
| mix | 32 | 7.68 | 326.2 ms | 5.34 | 5.36 | 3.03 | 21.9 ms | 1.61 | 1.61 |

## resources, votable

| class | c | argus-local cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-local cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.66 | 7.8 ms | 1.40 | 1.44 | 0.87 | 5.3 ms | 1.42 | 1.43 |
| Q01 | 4 | 2.19 | 8.6 ms | 1.73 | 1.94 | 1.39 | 6.9 ms | 1.38 | 1.39 |
| Q01 | 8 | 3.75 | 9.3 ms | 2.31 | 2.57 | 1.44 | 7.5 ms | 1.37 | 1.39 |
| Q01 | 16 | 5.06 | 9.8 ms | 2.97 | 3.32 | 1.43 | 7.7 ms | 1.36 | 1.37 |
| Q01 | 32 | 5.58 | 10.1 ms | 3.69 | 3.92 | 1.41 | 8.1 ms | 1.36 | 1.37 |
| Q02 | 1 | 1.00 | 409.0 ms | 3.87 | 3.88 | 1.07 | 16.9 ms | 1.39 | 1.40 |
| Q02 | 4 | 3.95 | 445.6 ms | 3.88 | 3.90 | 2.61 | 19.1 ms | 1.39 | 1.41 |
| Q02 | 8 | 7.60 | 498.7 ms | 3.85 | 3.87 | 3.05 | 20.3 ms | 1.40 | 1.41 |
| Q02 | 16 | 7.78 | 504.4 ms | 3.80 | 3.82 | 3.01 | 20.6 ms | 1.40 | 1.41 |
| Q02 | 32 | 7.81 | 503.9 ms | 3.74 | 3.77 | 2.90 | 21.0 ms | 1.40 | 1.41 |
| Q03 | 1 | 0.84 | 22.7 ms | 3.63 | 3.68 | 1.04 | 30.3 ms | 1.40 | 1.42 |
| Q03 | 4 | 3.01 | 24.4 ms | 3.69 | 3.76 | 3.39 | 33.0 ms | 1.40 | 1.40 |
| Q03 | 8 | 5.09 | 26.3 ms | 3.94 | 4.06 | 4.95 | 36.3 ms | 1.41 | 1.42 |
| Q03 | 16 | 6.55 | 27.9 ms | 4.20 | 4.42 | 4.96 | 37.2 ms | 1.40 | 1.42 |
| Q03 | 32 | 6.02 | 28.3 ms | 4.52 | 4.61 | 4.77 | 37.6 ms | 1.40 | 1.41 |
| Q04 | 1 | 0.82 | 17.9 ms | 4.57 | 4.59 | 1.04 | 23.3 ms | 1.41 | 1.42 |
| Q04 | 4 | 2.83 | 19.7 ms | 4.58 | 4.60 | 2.77 | 25.5 ms | 1.41 | 1.41 |
| Q04 | 8 | 4.55 | 20.8 ms | 4.67 | 4.81 | 3.51 | 27.7 ms | 1.42 | 1.42 |
| Q04 | 16 | 6.01 | 21.8 ms | 4.95 | 5.04 | 3.50 | 27.1 ms | 1.43 | 1.44 |
| Q04 | 32 | 6.04 | 22.0 ms | 5.14 | 5.22 | 3.36 | 27.5 ms | 1.43 | 1.44 |
| Q05 | 1 | 1.00 | 427.9 ms | 5.17 | 5.18 | 0.94 | 9.4 ms | 1.43 | 1.43 |
| Q05 | 4 | 3.95 | 463.2 ms | 5.17 | 5.19 | 1.91 | 10.8 ms | 1.42 | 1.43 |
| Q05 | 8 | 7.64 | 544.4 ms | 5.15 | 5.19 | 2.05 | 11.7 ms | 1.42 | 1.43 |
| Q05 | 16 | 7.84 | 548.7 ms | 5.07 | 5.10 | 2.01 | 12.1 ms | 1.42 | 1.43 |
| Q05 | 32 | 7.84 | 549.1 ms | 4.99 | 5.02 | 1.96 | 12.4 ms | 1.43 | 1.44 |
| Q06 | 1 | 1.00 | 422.4 ms | 4.85 | 4.88 | 1.04 | 18.9 ms | 1.43 | 1.44 |
| Q06 | 4 | 3.96 | 466.7 ms | 4.85 | 4.85 | 2.66 | 21.1 ms | 1.42 | 1.43 |
| Q06 | 8 | 7.58 | 539.6 ms | 4.81 | 4.84 | 3.06 | 22.4 ms | 1.44 | 1.45 |
| Q06 | 16 | 7.77 | 544.8 ms | 4.73 | 4.77 | 2.99 | 22.6 ms | 1.44 | 1.44 |
| Q06 | 32 | 7.77 | 545.8 ms | 4.69 | 4.70 | 2.89 | 23.0 ms | 1.44 | 1.45 |
| Q07 | 1 | 0.99 | 308.6 ms | 4.62 | 4.63 | 0.98 | 12.9 ms | 1.44 | 1.44 |
| Q07 | 4 | 3.94 | 330.4 ms | 4.65 | 4.67 | 2.28 | 14.4 ms | 1.43 | 1.45 |
| Q07 | 8 | 7.47 | 378.9 ms | 4.68 | 4.71 | 2.51 | 15.4 ms | 1.44 | 1.46 |
| Q07 | 16 | 7.79 | 382.4 ms | 4.71 | 4.74 | 2.47 | 15.8 ms | 1.45 | 1.46 |
| Q07 | 32 | 7.72 | 382.7 ms | 4.77 | 4.98 | 2.41 | 16.2 ms | 1.45 | 1.45 |
| Q10 | 1 | 0.89 | 31.9 ms | 4.95 | 4.96 | 1.13 | 39.5 ms | 1.45 | 1.46 |
| Q10 | 4 | 3.13 | 35.5 ms | 5.02 | 5.06 | 3.26 | 46.0 ms | 1.44 | 1.45 |
| Q10 | 8 | 5.03 | 38.0 ms | 5.14 | 5.19 | 3.99 | 48.4 ms | 1.46 | 1.46 |
| Q10 | 16 | 5.88 | 39.7 ms | 5.26 | 5.33 | 3.86 | 47.0 ms | 1.46 | 1.48 |
| Q10 | 32 | 5.82 | 39.7 ms | 5.38 | 5.42 | 3.74 | 47.2 ms | 1.47 | 1.48 |
| Q11 | 1 | 1.03 | 225.4 ms | 5.38 | 5.38 | 1.22 | 300.1 ms | 1.48 | 1.49 |
| Q11 | 4 | 3.75 | 255.1 ms | 5.36 | 5.39 | 3.91 | 360.1 ms | 1.48 | 1.50 |
| Q11 | 8 | 5.90 | 278.6 ms | 5.29 | 5.33 | 5.42 | 390.6 ms | 1.51 | 1.53 |
| Q11 | 16 | 6.08 | 280.8 ms | 5.28 | 5.31 | 5.71 | 380.9 ms | 1.55 | 1.56 |
| Q11 | 32 | 6.14 | 282.9 ms | 5.27 | 5.28 | 5.57 | 375.3 ms | 1.59 | 1.62 |
| Q12 | 1 | 1.00 | 426.6 ms | 5.23 | 5.24 | 0.93 | 8.8 ms | 1.53 | 1.55 |
| Q12 | 4 | 3.95 | 468.7 ms | 5.23 | 5.25 | 1.86 | 10.2 ms | 1.52 | 1.52 |
| Q12 | 8 | 7.65 | 541.0 ms | 5.22 | 5.23 | 1.98 | 11.0 ms | 1.53 | 1.53 |
| Q12 | 16 | 7.85 | 544.6 ms | 5.23 | 5.24 | 1.95 | 11.5 ms | 1.53 | 1.54 |
| Q12 | 32 | 7.85 | 546.1 ms | 5.24 | 5.25 | 1.90 | 11.8 ms | 1.53 | 1.53 |
| Q13 | 1 | 1.00 | 368.2 ms | 5.17 | 5.18 | 2.83 | 678.0 ms | 1.56 | 1.57 |
| Q13 | 4 | 3.95 | 383.6 ms | 5.19 | 5.19 | 7.75 | 808.8 ms | 1.58 | 1.60 |
| Q13 | 8 | 7.59 | 455.3 ms | 5.22 | 5.22 | 7.97 | 813.0 ms | 1.62 | 1.63 |
| Q13 | 16 | 7.83 | 456.4 ms | 5.23 | 5.24 | 7.97 | 817.9 ms | 1.62 | 1.65 |
| Q13 | 32 | 7.83 | 456.9 ms | 5.25 | 5.26 | 7.97 | 822.1 ms | 1.63 | 1.65 |
| mix | 1 | 1.01 | 265.0 ms | 1.07 | 1.08 | 1.03 | 18.4 ms | 1.34 | 1.34 |
| mix | 4 | 3.95 | 284.1 ms | 1.15 | 1.21 | 2.82 | 20.2 ms | 1.35 | 1.36 |
| mix | 8 | 7.41 | 319.0 ms | 1.25 | 1.27 | 3.20 | 21.7 ms | 1.40 | 1.41 |
| mix | 16 | 7.74 | 322.6 ms | 1.31 | 1.33 | 3.14 | 22.1 ms | 1.41 | 1.41 |
| mix | 32 | 7.74 | 322.7 ms | 1.37 | 1.39 | 3.04 | 22.6 ms | 1.42 | 1.43 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | argus-local | — | 3.8 | 0.99 | 3.9 | 258.2 |
| csv | 1 | egernia-local | 1 | 57.1 | 1.03 | 55.6 | 18.0 |
| csv | 4 | argus-local | — | 14.0 | 3.93 | 3.6 | 280.9 |
| csv | 4 | egernia-local | 1 | 141.2 | 2.77 | 51.0 | 19.6 |
| csv | 8 | argus-local | — | 23.1 | 7.43 | 3.1 | 322.1 |
| csv | 8 | egernia-local | 1 | 152.3 | 3.20 | 47.6 | 21.0 |
| csv | 16 | argus-local | — | 24.0 | 7.78 | 3.1 | 325.7 |
| csv | 16 | egernia-local | 1 | 146.1 | 3.14 | 46.5 | 21.5 |
| csv | 32 | argus-local | — | 23.6 | 7.68 | 3.1 | 326.2 |
| csv | 32 | egernia-local | 1 | 138.6 | 3.03 | 45.7 | 21.9 |
| votable | 1 | argus-local | — | 3.8 | 1.01 | 3.8 | 265.0 |
| votable | 1 | egernia-local | 1 | 55.9 | 1.03 | 54.3 | 18.4 |
| votable | 4 | argus-local | — | 13.9 | 3.95 | 3.5 | 284.1 |
| votable | 4 | egernia-local | 1 | 139.6 | 2.82 | 49.5 | 20.2 |
| votable | 8 | argus-local | — | 23.3 | 7.41 | 3.1 | 319.0 |
| votable | 8 | egernia-local | 1 | 147.7 | 3.20 | 46.1 | 21.7 |
| votable | 16 | argus-local | — | 24.0 | 7.74 | 3.1 | 322.6 |
| votable | 16 | egernia-local | 1 | 142.1 | 3.14 | 45.2 | 22.1 |
| votable | 32 | argus-local | — | 24.1 | 7.74 | 3.1 | 322.7 |
| votable | 32 | egernia-local | 1 | 134.6 | 3.04 | 44.3 | 22.6 |

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
    -f benchmarks/tap-compare/docker-compose.egernia-pins.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets argus-local egernia-local --scenario <scenario>
```

Environment: see `environment.json` (git 7aa14f6a, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **Servers.** egernia `main` 0c2afec (PRs #144–#146 and the argus target #154), one uvicorn worker, under the parity pins; CADC argus `images.opencadc.org/caom2/argus:1.0.27` (digest `34a74b23…`, the newest release: see `benchmarks/tap-compare/argus/PROTOCOL.md`), PostgreSQL 17 + pgsphere 1.5.2, `caom2.ObsCore` as a plain table loaded from the exported corpus (sha256 `bc411050…`, byte-identical to the DaCHS runs' corpus), pool of 8, its PostgreSQL sized by the same ¼-memory rule as egernia's.
- **Amendments before measurement** (both in `argus/PROTOCOL.md`): argus advertises default-port URLs only, so the stack maps host port 80 and the bundled `capabilities.xml` is patched to `http://localhost`; argus answers a sync POST with a 303 to the job's `run` URL, so the runner and the agreement probe follow redirects (the hop is inside argus's timed request; no effect on egernia or DaCHS).
- **Gates.** egernia taplint 0 errors; argus taplint 0 blocking / 2 total, both in the TAP_UPLOAD-by-URL stage (argus fetches the upload from its own advertised URL, which inside its container is not Tomcat's port; uploads are not in the workload); cross-server agreement 11/11 classes.
- **Verdicts.** egernia 64, argus 44, ties 12 of 120 cells. One request of 65,119 failed in one argus Q01 repetition (connection-level, 0.002%); every other cell 0% errors.
- **Where each wins, and why.** egernia leads every cell of the cone classes (Q05, Q06, Q07, Q12 — CADC's schema has no pgsphere index for the `<@` predicate, so argus scans), the DID lookup Q02, and the mix, by 6–70×. argus leads from c≥4 on the CPU-bound classes: Q01 (metadata), Q03, Q04, Q10, Q11 (10,000-row results) and Q13 (the aggregate). The resource tables explain the split: at c≥8 argus, a JVM with a thread per request, uses 7.4–7.8 of the 8 pinned cores at ~320 ms of CPU per request; egernia uses 3.2 cores — one API worker on one core plus PostgreSQL — at 21 ms of CPU per request, 15× less, with five cores idle. The protocol's "one process each" rule is even-handed against DaCHS (a single-threaded Python process) but hands a threaded Java server a seven-core advantage on CPU-bound work. The pre-registered equal-CPU variant (`benchmarks/tap-compare/argus-equal-cpu/`, tag `tap-compare-argus-equalcpu-prereg-v1`: egernia with eight workers in the same pin, argus unchanged) measures the same grid without that asymmetry.
- **Conditions.** Interleaved A/B/A/B rungs, 30.6 h (2026-09-06 14:53Z → 09-07 21:28Z), generator peak 13% of one core, nothing else running on the host (the DaCHS container was stopped, not removed). Resource sampler (`scaling/sample_resources.sh`) alongside; every rung covered.

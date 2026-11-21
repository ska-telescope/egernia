# 20261119T203938Z-19e19fcb-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: argus in `benchmarks/tap-compare/docker-compose.argus.yml` + `final/pins/argus.yml` (`cpuset` 8-15; 8 GiB split 3 Tomcat / 5 PostgreSQL; `benchmarks/tap-compare/final/PROTOCOL.md`); DaCHS in `benchmarks/tap-compare/docker-compose.dachs.yml` + `final/pins/dachs.yml` (`cpus: 8`, `cpuset` 16-23, `mem_limit: 8g`, its PostgreSQL sized to the container by the ¼ rule; `benchmarks/tap-compare/final/PROTOCOL.md`); egernia on skycell in `benchmarks/tap-compare/final-skycell/pins/egernia-w8.yml` + `skycell.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=8`, PostgreSQL parallel budget 144/152; `benchmarks/tap-compare/final-skycell/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-final | 1.1 | PASS (2 errors) | 134217728 |
| dachs-final | 1.1 | PASS (0 errors) | 20000 |
| egernia-skycell-w8 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-skycell-w8 rps | egernia-skycell-w8 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 95.7 ±7.2 | 0.012 ±0.001 | 25.5 ±0.6 | 0.121 ±0.004 | 227.4 ±4.6 | 0.005 ±0.000 | egernia-skycell-w8 |
| Q01 | 4 | 282.9 ±4.2 | 0.016 ±0.000 | 19.7 ±0.5 | 0.294 ±0.010 | 634.9 ±198.9 | 0.008 ±0.003 | egernia-skycell-w8 |
| Q01 | 8 | 430.9 ±2.5 | 0.022 ±0.000 | 18.2 ±0.3 | 0.535 ±0.015 | 799.1 ±14.2 | 0.019 ±0.000 | egernia-skycell-w8 |
| Q01 | 32 | 529.8 ±93.2 | 0.068 ±0.001 | 16.6 ±0.1 | 2.069 ±0.031 | 1054.3 ±41.0 | 0.059 ±0.017 | egernia-skycell-w8 |
| Q02 | 1 | 2.4 ±0.1 | 0.422 ±0.013 | 5.4 ±0.2 | 0.273 ±0.009 | 138.5 ±2.0 | 0.012 ±0.000 | egernia-skycell-w8 |
| Q02 | 4 | 9.1 ±0.7 | 0.512 ±0.018 | 10.6 ±0.3 | 0.491 ±0.013 | 344.1 ±65.5 | 0.018 ±0.003 | egernia-skycell-w8 |
| Q02 | 8 | 15.6 ±0.1 | 0.540 ±0.012 | 9.7 ±0.1 | 1.009 ±0.028 | 479.7 ±62.2 | 0.026 ±0.003 | egernia-skycell-w8 |
| Q02 | 32 | 15.7 ±0.2 | 2.112 ±0.049 | 9.2 ±0.1 | 3.744 ±0.057 | 645.6 ±24.7 | 0.098 ±0.017 | egernia-skycell-w8 |
| Q03 | 1 | 41.1 ±1.6 | 0.085 ±0.000 | 12.4 ±0.5 | 0.161 ±0.001 | 164.1 ±5.3 | 0.007 ±0.000 | egernia-skycell-w8 |
| Q03 | 4 | 134.4 ±0.8 | 0.095 ±0.001 | 12.9 ±0.2 | 0.432 ±0.008 | 417.2 ±35.6 | 0.013 ±0.000 | egernia-skycell-w8 |
| Q03 | 8 | 204.5 ±1.0 | 0.116 ±0.000 | 12.3 ±0.3 | 0.797 ±0.028 | 521.5 ±155.3 | 0.023 ±0.009 | egernia-skycell-w8 |
| Q03 | 32 | 244.0 ±12.6 | 0.247 ±0.022 | 11.7 ±0.1 | 2.950 ±0.020 | 767.1 ±27.8 | 0.072 ±0.016 | egernia-skycell-w8 |
| Q04 | 1 | 56.9 ±2.5 | 0.019 ±0.001 | 13.0 ±0.1 | 0.165 ±0.004 | 101.4 ±3.4 | 0.011 ±0.001 | egernia-skycell-w8 |
| Q04 | 4 | 157.4 ±0.4 | 0.031 ±0.000 | 13.1 ±0.2 | 0.420 ±0.011 | 285.9 ±12.4 | 0.018 ±0.001 | egernia-skycell-w8 |
| Q04 | 8 | 223.0 ±31.9 | 0.044 ±0.005 | 12.4 ±0.2 | 0.777 ±0.035 | 396.3 ±27.2 | 0.029 ±0.004 | egernia-skycell-w8 |
| Q04 | 32 | 281.3 ±4.9 | 0.131 ±0.001 | 11.7 ±0.3 | 2.918 ±0.053 | 545.0 ±50.6 | 0.121 ±0.094 | egernia-skycell-w8 |
| Q05 | 1 | 2.4 ±0.1 | 0.421 ±0.020 | 1.8 ±0.0 | 0.630 ±0.018 | 195.6 ±2.5 | 0.006 ±0.000 | egernia-skycell-w8 |
| Q05 | 4 | 9.6 ±0.1 | 0.439 ±0.057 | 6.1 ±0.1 | 0.798 ±0.077 | 500.4 ±124.2 | 0.011 ±0.004 | egernia-skycell-w8 |
| Q05 | 8 | 14.6 ±0.1 | 0.578 ±0.006 | 8.2 ±0.2 | 1.182 ±0.090 | 679.7 ±72.0 | 0.017 ±0.000 | egernia-skycell-w8 |
| Q05 | 32 | 14.9 ±0.0 | 2.269 ±0.019 | 8.3 ±0.2 | 4.105 ±0.052 | 864.2 ±17.4 | 0.077 ±0.026 | egernia-skycell-w8 |
| Q06 | 1 | 2.4 ±0.2 | 0.425 ±0.023 | 1.8 ±0.0 | 0.623 ±0.012 | 165.5 ±5.5 | 0.007 ±0.000 | egernia-skycell-w8 |
| Q06 | 4 | 8.5 ±1.2 | 0.550 ±0.002 | 6.0 ±0.2 | 0.827 ±0.067 | 408.0 ±85.6 | 0.013 ±0.003 | egernia-skycell-w8 |
| Q06 | 8 | 14.5 ±0.2 | 0.596 ±0.009 | 8.1 ±0.2 | 1.202 ±0.026 | 523.7 ±98.0 | 0.022 ±0.008 | egernia-skycell-w8 |
| Q06 | 32 | 14.7 ±0.2 | 2.287 ±0.018 | 8.1 ±0.2 | 4.212 ±0.100 | 700.5 ±13.1 | 0.086 ±0.011 | egernia-skycell-w8 |
| Q07 | 1 | 3.4 ±0.1 | 0.415 ±0.010 | 1.7 ±0.0 | 0.666 ±0.005 | 183.1 ±2.9 | 0.006 ±0.000 | egernia-skycell-w8 |
| Q07 | 4 | 12.5 ±1.1 | 0.482 ±0.066 | 5.7 ±0.1 | 0.853 ±0.038 | 472.5 ±84.9 | 0.011 ±0.002 | egernia-skycell-w8 |
| Q07 | 8 | 20.6 ±0.3 | 0.551 ±0.002 | 7.9 ±0.2 | 1.220 ±0.065 | 605.4 ±102.0 | 0.020 ±0.005 | egernia-skycell-w8 |
| Q07 | 32 | 21.3 ±0.1 | 1.741 ±0.035 | 7.9 ±0.1 | 4.335 ±0.151 | 808.7 ±45.9 | 0.080 ±0.049 | egernia-skycell-w8 |
| Q10 | 1 | 31.2 ±0.4 | 0.035 ±0.001 | 11.1 ±0.1 | 0.180 ±0.005 | 87.4 ±2.9 | 0.014 ±0.001 | egernia-skycell-w8 |
| Q10 | 4 | 89.1 ±7.4 | 0.052 ±0.001 | 11.4 ±0.2 | 0.471 ±0.018 | 230.8 ±12.1 | 0.023 ±0.002 | egernia-skycell-w8 |
| Q10 | 8 | 128.7 ±18.6 | 0.075 ±0.001 | 11.0 ±0.2 | 0.877 ±0.041 | 294.0 ±50.0 | 0.044 ±0.020 | egernia-skycell-w8 |
| Q10 | 32 | 147.0 ±0.9 | 0.246 ±0.001 | 10.5 ±0.3 | 3.272 ±0.086 | 390.7 ±12.6 | 0.180 ±0.080 | egernia-skycell-w8 |
| Q11 | 1 | 4.4 ±0.0 | 0.240 ±0.011 | 3.6 ±0.1 | 0.366 ±0.007 | 4.7 ±0.4 | 0.244 ±0.034 | tie |
| Q11 | 4 | 14.2 ±0.1 | 0.317 ±0.005 | 4.0 ±0.1 | 1.201 ±0.135 | 18.1 ±2.2 | 0.334 ±0.010 | egernia-skycell-w8 |
| Q11 | 8 | 20.8 ±0.2 | 0.443 ±0.005 | 4.0 ±0.2 | 2.652 ±0.342 | 29.7 ±5.5 | 0.648 ±0.490 | egernia-skycell-w8 |
| Q11 | 32 | 21.2 ±0.2 | 1.609 ±0.008 | 4.1 ±0.5 | 12.455 ±1.038 | 27.8 ±9.7 | 3.210 ±1.662 | tie |
| Q12 | 1 | 2.4 ±0.0 | 0.425 ±0.001 | 1.8 ±0.0 | 0.623 ±0.004 | 201.2 ±5.3 | 0.006 ±0.000 | egernia-skycell-w8 |
| Q12 | 4 | 9.3 ±0.4 | 0.517 ±0.132 | 6.1 ±0.1 | 0.794 ±0.055 | 514.2 ±80.3 | 0.010 ±0.000 | egernia-skycell-w8 |
| Q12 | 8 | 14.5 ±0.1 | 0.584 ±0.012 | 8.3 ±0.1 | 1.163 ±0.025 | 701.4 ±102.8 | 0.017 ±0.005 | egernia-skycell-w8 |
| Q12 | 32 | 14.5 ±0.2 | 2.293 ±0.012 | 8.3 ±0.3 | 4.103 ±0.083 | 889.4 ±20.8 | 0.064 ±0.014 | egernia-skycell-w8 |
| Q13 | 1 | 2.6 ±0.0 | 0.429 ±0.004 | 2.9 ±0.3 | 0.458 ±0.009 | 8.6 ±0.0 | 0.160 ±0.003 | egernia-skycell-w8 |
| Q13 | 4 | 10.3 ±1.3 | 0.479 ±0.138 | 8.9 ±0.2 | 0.658 ±0.020 | 19.5 ±0.1 | 0.272 ±0.006 | egernia-skycell-w8 |
| Q13 | 8 | 16.8 ±0.2 | 0.565 ±0.004 | 10.4 ±0.3 | 1.051 ±0.063 | 20.4 ±0.2 | 0.533 ±0.011 | egernia-skycell-w8 |
| Q13 | 32 | 17.1 ±0.1 | 2.035 ±0.047 | 9.8 ±0.2 | 3.591 ±0.087 | 20.9 ±0.3 (8% err) | 2.543 ±0.328 | argus-final |
| mix | 1 | 4.0 ±0.6 | 0.419 ±0.001 | 3.2 ±0.3 | 0.602 ±0.067 | 150.3 ±1.8 | 0.011 ±0.000 | egernia-skycell-w8 |
| mix | 4 | 14.3 ±1.1 | 0.533 ±0.002 | 9.2 ±0.4 | 0.820 ±0.036 | 372.3 ±61.3 | 0.017 ±0.003 | egernia-skycell-w8 |
| mix | 8 | 23.7 ±1.0 | 0.577 ±0.009 | 9.7 ±0.3 | 1.275 ±0.072 | 520.5 ±48.9 | 0.025 ±0.003 | egernia-skycell-w8 |
| mix | 32 | 24.4 ±1.2 | 1.716 ±0.077 | 9.3 ±0.0 | 3.994 ±0.079 | 687.0 ±53.7 | 0.095 ±0.073 | egernia-skycell-w8 |

## votable

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-skycell-w8 rps | egernia-skycell-w8 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 96.5 ±0.9 | 0.012 ±0.000 | 22.2 ±0.6 | 0.142 ±0.008 | 228.7 ±2.7 | 0.005 ±0.000 | egernia-skycell-w8 |
| Q01 | 4 | 275.8 ±21.9 | 0.017 ±0.001 | 17.7 ±0.1 | 0.338 ±0.009 | 548.1 ±215.9 | 0.011 ±0.005 | egernia-skycell-w8 |
| Q01 | 8 | 427.0 ±14.5 | 0.022 ±0.000 | 16.7 ±0.2 | 0.584 ±0.013 | 827.4 ±224.2 | 0.016 ±0.005 | egernia-skycell-w8 |
| Q01 | 32 | 537.0 ±56.7 | 0.069 ±0.002 | 15.1 ±0.2 | 2.287 ±0.003 | 1069.4 ±33.6 | 0.059 ±0.025 | egernia-skycell-w8 |
| Q02 | 1 | 2.4 ±0.1 | 0.420 ±0.015 | 5.2 ±0.6 | 0.320 ±0.027 | 132.3 ±2.4 | 0.012 ±0.000 | egernia-skycell-w8 |
| Q02 | 4 | 9.8 ±0.2 | 0.468 ±0.094 | 9.8 ±0.1 | 0.555 ±0.023 | 334.3 ±41.0 | 0.018 ±0.002 | egernia-skycell-w8 |
| Q02 | 8 | 15.7 ±0.0 | 0.541 ±0.020 | 9.1 ±0.1 | 1.064 ±0.012 | 478.4 ±61.5 | 0.025 ±0.005 | egernia-skycell-w8 |
| Q02 | 32 | 15.9 ±0.1 | 2.093 ±0.016 | 8.7 ±0.1 | 3.926 ±0.059 | 630.6 ±21.6 | 0.090 ±0.004 | egernia-skycell-w8 |
| Q03 | 1 | 40.9 ±0.8 | 0.084 ±0.001 | 11.1 ±0.3 | 0.214 ±0.008 | 156.9 ±0.8 | 0.008 ±0.000 | egernia-skycell-w8 |
| Q03 | 4 | 134.0 ±1.5 | 0.095 ±0.002 | 11.7 ±0.1 | 0.488 ±0.014 | 384.9 ±58.8 | 0.014 ±0.003 | egernia-skycell-w8 |
| Q03 | 8 | 202.5 ±3.3 | 0.116 ±0.001 | 11.4 ±0.2 | 0.865 ±0.007 | 538.2 ±15.3 | 0.024 ±0.004 | egernia-skycell-w8 |
| Q03 | 32 | 239.3 ±18.4 | 0.246 ±0.014 | 10.8 ±0.2 | 3.184 ±0.092 | 741.1 ±37.5 | 0.085 ±0.009 | egernia-skycell-w8 |
| Q04 | 1 | 52.5 ±9.3 | 0.022 ±0.003 | 11.7 ±0.1 | 0.215 ±0.002 | 97.9 ±2.2 | 0.012 ±0.000 | egernia-skycell-w8 |
| Q04 | 4 | 157.6 ±2.4 | 0.030 ±0.000 | 11.9 ±0.2 | 0.471 ±0.015 | 278.9 ±7.8 | 0.018 ±0.001 | egernia-skycell-w8 |
| Q04 | 8 | 225.4 ±24.8 | 0.043 ±0.001 | 11.5 ±0.1 | 0.842 ±0.021 | 349.0 ±7.7 | 0.035 ±0.001 | egernia-skycell-w8 |
| Q04 | 32 | 282.7 ±4.5 | 0.130 ±0.002 | 11.0 ±0.3 | 3.109 ±0.126 | 533.6 ±11.2 | 0.105 ±0.018 | egernia-skycell-w8 |
| Q05 | 1 | 2.4 ±0.1 | 0.425 ±0.017 | 1.8 ±0.0 | 0.684 ±0.007 | 191.7 ±1.8 | 0.006 ±0.000 | egernia-skycell-w8 |
| Q05 | 4 | 8.9 ±0.7 | 0.518 ±0.077 | 5.9 ±0.0 | 0.860 ±0.034 | 495.8 ±132.8 | 0.011 ±0.005 | egernia-skycell-w8 |
| Q05 | 8 | 14.5 ±0.1 | 0.585 ±0.004 | 7.8 ±0.2 | 1.292 ±0.028 | 680.5 ±193.7 | 0.018 ±0.007 | egernia-skycell-w8 |
| Q05 | 32 | 14.6 ±0.0 | 2.279 ±0.014 | 7.7 ±0.1 | 4.405 ±0.128 | 898.1 ±7.9 | 0.061 ±0.002 | egernia-skycell-w8 |
| Q06 | 1 | 2.4 ±0.1 | 0.428 ±0.010 | 1.8 ±0.0 | 0.692 ±0.013 | 145.4 ±23.4 | 0.009 ±0.003 | egernia-skycell-w8 |
| Q06 | 4 | 9.0 ±1.6 | 0.512 ±0.173 | 5.9 ±0.1 | 0.854 ±0.070 | 369.4 ±39.5 | 0.015 ±0.001 | egernia-skycell-w8 |
| Q06 | 8 | 14.4 ±0.2 | 0.602 ±0.013 | 7.6 ±0.1 | 1.350 ±0.072 | 486.7 ±102.3 | 0.027 ±0.014 | egernia-skycell-w8 |
| Q06 | 32 | 14.6 ±0.2 | 2.299 ±0.017 | 7.7 ±0.1 | 4.527 ±0.214 | 657.8 ±8.1 | 0.089 ±0.009 | egernia-skycell-w8 |
| Q07 | 1 | 3.5 ±0.1 | 0.409 ±0.012 | 1.7 ±0.0 | 0.712 ±0.021 | 174.4 ±3.1 | 0.007 ±0.000 | egernia-skycell-w8 |
| Q07 | 4 | 12.2 ±0.4 | 0.485 ±0.022 | 5.5 ±0.3 | 0.913 ±0.099 | 446.4 ±135.7 | 0.012 ±0.005 | egernia-skycell-w8 |
| Q07 | 8 | 20.6 ±0.3 | 0.551 ±0.004 | 7.2 ±0.3 | 1.400 ±0.099 | 554.4 ±94.4 | 0.023 ±0.009 | egernia-skycell-w8 |
| Q07 | 32 | 21.3 ±0.1 | 1.739 ±0.023 | 7.4 ±0.1 | 4.637 ±0.055 | 796.3 ±64.8 | 0.070 ±0.027 | egernia-skycell-w8 |
| Q10 | 1 | 31.5 ±1.3 | 0.035 ±0.001 | 9.9 ±1.8 | 0.229 ±0.004 | 74.3 ±2.8 | 0.016 ±0.001 | egernia-skycell-w8 |
| Q10 | 4 | 92.5 ±4.5 | 0.051 ±0.000 | 10.4 ±1.2 | 0.537 ±0.110 | 194.4 ±43.4 | 0.027 ±0.008 | egernia-skycell-w8 |
| Q10 | 8 | 129.6 ±17.3 | 0.074 ±0.001 | 10.4 ±0.2 | 0.931 ±0.015 | 262.4 ±28.5 | 0.043 ±0.007 | egernia-skycell-w8 |
| Q10 | 32 | 146.7 ±7.1 | 0.250 ±0.027 | 10.0 ±0.6 | 3.483 ±0.195 | 341.8 ±13.0 | 0.175 ±0.057 | egernia-skycell-w8 |
| Q11 | 1 | 4.7 ±0.1 | 0.226 ±0.010 | 3.6 ±0.6 | 0.420 ±0.130 | 2.4 ±0.2 | 0.586 ±0.313 | argus-final |
| Q11 | 4 | 15.0 ±0.1 | 0.303 ±0.006 | 4.4 ±0.2 | 1.133 ±0.085 | 13.3 ±1.1 | 0.449 ±0.051 | argus-final |
| Q11 | 8 | 21.4 ±0.1 | 0.431 ±0.001 | 4.3 ±0.7 | 2.426 ±0.737 | 24.2 ±1.2 | 0.815 ±0.256 | egernia-skycell-w8 |
| Q11 | 32 | 20.1 ±7.5 | 1.727 ±0.697 | 4.6 ±0.2 | 11.216 ±1.267 | 14.1 ±23.1 | 8.500 ±13.043 | tie |
| Q12 | 1 | 2.4 ±0.0 | 0.426 ±0.008 | 1.8 ±0.0 | 0.647 ±0.003 | 199.0 ±3.7 | 0.006 ±0.000 | egernia-skycell-w8 |
| Q12 | 4 | 9.3 ±0.4 | 0.543 ±0.010 | 6.0 ±0.0 | 0.817 ±0.028 | 576.7 ±79.0 | 0.009 ±0.002 | egernia-skycell-w8 |
| Q12 | 8 | 14.6 ±0.3 | 0.579 ±0.014 | 8.2 ±0.3 | 1.168 ±0.040 | 690.5 ±161.5 | 0.018 ±0.005 | egernia-skycell-w8 |
| Q12 | 32 | 14.7 ±0.2 | 2.260 ±0.015 | 8.2 ±0.1 | 4.148 ±0.066 | 900.7 ±29.3 | 0.072 ±0.041 | egernia-skycell-w8 |
| Q13 | 1 | 2.7 ±0.1 | 0.417 ±0.007 | 2.8 ±0.2 | 0.465 ±0.013 | 8.5 ±0.1 | 0.160 ±0.004 | egernia-skycell-w8 |
| Q13 | 4 | 10.6 ±0.6 | 0.462 ±0.059 | 8.9 ±0.4 | 0.671 ±0.034 | 19.4 ±0.1 | 0.273 ±0.008 | egernia-skycell-w8 |
| Q13 | 8 | 16.9 ±0.0 | 0.562 ±0.008 | 10.2 ±0.1 | 1.074 ±0.008 | 20.4 ±0.3 | 0.530 ±0.010 | egernia-skycell-w8 |
| Q13 | 32 | 17.3 ±0.1 | 2.017 ±0.028 | 9.8 ±0.1 | 3.592 ±0.041 | 20.8 ±0.5 (7% err) | 2.552 ±0.250 | argus-final |
| mix | 1 | 3.9 ±0.5 | 0.427 ±0.011 | 3.1 ±0.2 | 0.618 ±0.058 | 146.1 ±1.7 | 0.012 ±0.000 | egernia-skycell-w8 |
| mix | 4 | 14.5 ±0.6 | 0.536 ±0.025 | 8.8 ±0.3 | 0.851 ±0.041 | 391.4 ±33.0 | 0.017 ±0.001 | egernia-skycell-w8 |
| mix | 8 | 23.7 ±1.2 | 0.582 ±0.010 | 9.6 ±0.2 | 1.280 ±0.035 | 516.2 ±95.2 | 0.027 ±0.011 | egernia-skycell-w8 |
| mix | 32 | 24.3 ±1.4 | 1.725 ±0.043 | 9.2 ±0.2 | 4.016 ±0.144 | 684.0 ±16.1 | 0.095 ±0.027 | egernia-skycell-w8 |

## resources, csv

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-w8 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.70 | 7.4 ms | 1.49 | 1.52 | 0.96 | 37.4 ms | 0.83 | 0.83 | 0.78 | 3.4 ms | 1.98 | 2.00 |
| Q01 | 4 | 2.39 | 8.5 ms | 1.74 | 1.92 | 1.82 | 92.8 ms | 0.83 | 0.84 | 2.61 | 4.1 ms | 1.93 | 1.96 |
| Q01 | 8 | 4.10 | 9.5 ms | 2.11 | 2.24 | 1.99 | 109.8 ms | 0.84 | 0.84 | 3.74 | 4.7 ms | 1.88 | 1.90 |
| Q01 | 32 | 5.62 | 10.6 ms | 2.52 | 2.80 | 1.94 | 117.7 ms | 0.84 | 0.85 | 6.38 | 6.0 ms | 1.90 | 1.91 |
| Q02 | 1 | 1.00 | 414.0 ms | 2.77 | 2.77 | 2.25 | 419.7 ms | 0.84 | 0.84 | 0.93 | 6.7 ms | 1.91 | 1.92 |
| Q02 | 4 | 3.97 | 435.3 ms | 2.79 | 2.79 | 5.26 | 495.7 ms | 0.85 | 0.86 | 2.74 | 8.0 ms | 1.91 | 1.94 |
| Q02 | 8 | 7.69 | 495.5 ms | 2.78 | 2.79 | 5.24 | 542.9 ms | 0.85 | 0.87 | 4.27 | 8.9 ms | 1.89 | 1.89 |
| Q02 | 32 | 7.90 | 507.9 ms | 2.74 | 2.75 | 5.08 | 563.0 ms | 0.86 | 0.87 | 6.88 | 10.7 ms | 1.95 | 1.98 |
| Q03 | 1 | 0.88 | 21.3 ms | 2.68 | 2.70 | 1.24 | 100.4 ms | 0.84 | 0.85 | 0.90 | 5.5 ms | 1.96 | 1.98 |
| Q03 | 4 | 3.14 | 23.4 ms | 2.65 | 2.69 | 1.96 | 151.7 ms | 0.85 | 0.85 | 2.74 | 6.6 ms | 1.94 | 1.95 |
| Q03 | 8 | 5.27 | 25.8 ms | 2.81 | 2.88 | 2.17 | 177.0 ms | 0.85 | 0.86 | 3.78 | 7.2 ms | 1.91 | 1.92 |
| Q03 | 32 | 6.74 | 27.6 ms | 3.04 | 3.22 | 2.16 | 188.8 ms | 0.85 | 0.87 | 6.74 | 8.8 ms | 1.96 | 1.98 |
| Q04 | 1 | 0.83 | 14.6 ms | 3.19 | 3.21 | 0.99 | 75.6 ms | 0.84 | 0.85 | 0.99 | 9.8 ms | 1.96 | 1.98 |
| Q04 | 4 | 2.93 | 18.6 ms | 3.28 | 3.32 | 1.65 | 125.7 ms | 0.85 | 0.85 | 3.20 | 11.2 ms | 1.93 | 1.95 |
| Q04 | 8 | 4.57 | 20.5 ms | 3.43 | 3.49 | 1.87 | 151.4 ms | 0.85 | 0.86 | 4.68 | 11.8 ms | 1.91 | 1.93 |
| Q04 | 32 | 6.17 | 21.9 ms | 3.64 | 3.78 | 1.88 | 163.5 ms | 0.86 | 0.86 | 7.15 | 13.1 ms | 1.96 | 1.99 |
| Q05 | 1 | 1.00 | 414.2 ms | 3.74 | 3.74 | 1.03 | 570.2 ms | 0.87 | 0.87 | 0.82 | 4.2 ms | 1.98 | 2.00 |
| Q05 | 4 | 3.97 | 415.0 ms | 3.75 | 3.76 | 3.93 | 646.5 ms | 0.93 | 0.96 | 2.53 | 5.1 ms | 1.96 | 1.98 |
| Q05 | 8 | 7.76 | 535.5 ms | 3.75 | 3.75 | 6.26 | 768.7 ms | 0.98 | 1.04 | 3.95 | 5.8 ms | 1.94 | 1.96 |
| Q05 | 32 | 7.93 | 540.9 ms | 3.71 | 3.73 | 6.61 | 813.1 ms | 1.01 | 1.07 | 6.20 | 7.2 ms | 1.95 | 1.96 |
| Q06 | 1 | 1.00 | 411.3 ms | 3.62 | 3.64 | 1.03 | 561.9 ms | 0.87 | 0.88 | 0.94 | 5.7 ms | 1.95 | 1.96 |
| Q06 | 4 | 3.97 | 472.5 ms | 3.63 | 3.63 | 3.88 | 651.0 ms | 0.93 | 0.96 | 2.85 | 7.0 ms | 1.94 | 1.95 |
| Q06 | 8 | 7.67 | 530.3 ms | 3.62 | 3.64 | 6.11 | 764.1 ms | 0.98 | 1.04 | 4.09 | 7.8 ms | 1.92 | 1.94 |
| Q06 | 32 | 7.88 | 540.2 ms | 3.60 | 3.62 | 6.43 | 820.7 ms | 0.99 | 1.08 | 6.61 | 9.4 ms | 1.97 | 1.99 |
| Q07 | 1 | 1.00 | 293.6 ms | 3.50 | 3.52 | 1.03 | 606.6 ms | 0.88 | 0.88 | 0.87 | 4.7 ms | 1.98 | 1.99 |
| Q07 | 4 | 3.95 | 318.1 ms | 3.51 | 3.53 | 3.91 | 686.5 ms | 0.94 | 0.97 | 2.74 | 5.8 ms | 1.96 | 1.98 |
| Q07 | 8 | 7.58 | 368.6 ms | 3.49 | 3.51 | 6.28 | 805.9 ms | 0.99 | 1.06 | 3.90 | 6.4 ms | 1.94 | 1.95 |
| Q07 | 32 | 7.88 | 372.7 ms | 3.50 | 3.51 | 6.54 | 853.7 ms | 0.99 | 1.07 | 6.45 | 8.0 ms | 1.98 | 2.01 |
| Q10 | 1 | 0.93 | 29.8 ms | 3.46 | 3.47 | 0.99 | 89.3 ms | 0.86 | 0.86 | 1.18 | 13.5 ms | 1.99 | 2.00 |
| Q10 | 4 | 3.18 | 35.7 ms | 3.58 | 3.64 | 1.60 | 140.9 ms | 0.86 | 0.87 | 3.58 | 15.5 ms | 1.98 | 2.01 |
| Q10 | 8 | 5.03 | 39.1 ms | 3.74 | 3.86 | 1.83 | 167.1 ms | 0.87 | 0.87 | 4.86 | 16.5 ms | 1.96 | 1.97 |
| Q10 | 32 | 5.96 | 40.6 ms | 3.98 | 4.01 | 1.86 | 180.3 ms | 0.87 | 0.88 | 7.20 | 18.4 ms | 2.01 | 2.03 |
| Q11 | 1 | 1.03 | 236.1 ms | 3.97 | 3.97 | 1.00 | 279.5 ms | 0.88 | 0.89 | 0.46 | 96.2 ms | 2.02 | 2.05 |
| Q11 | 4 | 3.80 | 268.5 ms | 3.96 | 3.97 | 1.40 | 349.8 ms | 0.92 | 0.94 | 1.85 | 102.8 ms | 2.01 | 2.03 |
| Q11 | 8 | 6.11 | 294.3 ms | 3.94 | 3.96 | 1.48 | 368.2 ms | 0.96 | 1.00 | 3.23 | 108.6 ms | 2.01 | 2.03 |
| Q11 | 32 | 6.31 | 299.9 ms | 3.89 | 3.92 | 1.56 | 399.3 ms | 1.01 | 1.06 | 3.29 | 117.0 ms | 2.18 | 2.22 |
| Q12 | 1 | 1.00 | 418.1 ms | 3.77 | 3.80 | 1.03 | 564.7 ms | 0.98 | 0.98 | 0.82 | 4.1 ms | 2.13 | 2.13 |
| Q12 | 4 | 3.96 | 429.5 ms | 3.77 | 3.79 | 3.94 | 648.1 ms | 1.03 | 1.06 | 2.50 | 4.9 ms | 2.10 | 2.12 |
| Q12 | 8 | 7.75 | 537.9 ms | 3.77 | 3.78 | 6.31 | 766.5 ms | 1.08 | 1.15 | 3.91 | 5.6 ms | 2.08 | 2.11 |
| Q12 | 32 | 7.95 | 551.9 ms | 3.75 | 3.76 | 6.60 | 811.5 ms | 1.08 | 1.13 | 6.21 | 7.0 ms | 2.10 | 2.12 |
| Q13 | 1 | 1.00 | 383.4 ms | 3.69 | 3.70 | 1.17 | 410.2 ms | 0.94 | 0.94 | 2.77 | 321.8 ms | 2.11 | 2.12 |
| Q13 | 4 | 3.96 | 387.6 ms | 3.70 | 3.71 | 4.14 | 466.4 ms | 0.94 | 0.95 | 7.57 | 387.9 ms | 2.12 | 2.14 |
| Q13 | 8 | 7.70 | 461.4 ms | 3.71 | 3.72 | 5.61 | 543.0 ms | 0.95 | 0.97 | 7.96 | 390.3 ms | 2.14 | 2.16 |
| Q13 | 32 | 7.94 | 467.4 ms | 3.72 | 3.72 | 5.48 | 567.1 ms | 0.95 | 0.97 | 7.99 | 382.7 ms | 2.31 | 2.37 |
| mix | 1 | 0.99 | 247.9 ms | 1.39 | 1.39 | 1.14 | 361.4 ms | 0.84 | 0.85 | 0.93 | 6.2 ms | 1.92 | 1.93 |
| mix | 4 | 3.95 | 276.8 ms | 1.41 | 1.42 | 3.90 | 426.7 ms | 0.88 | 0.93 | 2.68 | 7.2 ms | 1.92 | 1.94 |
| mix | 8 | 7.52 | 317.9 ms | 1.45 | 1.46 | 4.89 | 508.1 ms | 0.90 | 0.99 | 4.17 | 8.0 ms | 1.90 | 1.90 |
| mix | 32 | 7.83 | 322.4 ms | 1.48 | 1.50 | 4.88 | 534.8 ms | 0.90 | 0.98 | 6.56 | 9.6 ms | 1.98 | 2.01 |

## resources, votable

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-skycell-w8 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.70 | 7.3 ms | 1.38 | 1.41 | 0.96 | 43.4 ms | 1.22 | 1.23 | 0.79 | 3.4 ms | 2.03 | 2.06 |
| Q01 | 4 | 2.36 | 8.6 ms | 1.59 | 1.72 | 1.77 | 100.3 ms | 1.24 | 1.24 | 2.26 | 4.1 ms | 1.97 | 2.00 |
| Q01 | 8 | 4.07 | 9.5 ms | 1.92 | 2.07 | 1.97 | 118.0 ms | 1.25 | 1.26 | 3.94 | 4.8 ms | 1.94 | 1.96 |
| Q01 | 32 | 5.74 | 10.7 ms | 2.37 | 2.57 | 1.91 | 128.1 ms | 1.25 | 1.27 | 6.46 | 6.0 ms | 1.92 | 1.94 |
| Q02 | 1 | 1.00 | 411.6 ms | 2.54 | 2.55 | 2.19 | 424.1 ms | 1.25 | 1.25 | 0.94 | 7.1 ms | 1.91 | 1.92 |
| Q02 | 4 | 3.97 | 407.1 ms | 2.55 | 2.56 | 5.02 | 512.8 ms | 1.27 | 1.28 | 2.83 | 8.5 ms | 1.91 | 1.93 |
| Q02 | 8 | 7.69 | 492.9 ms | 2.55 | 2.57 | 5.09 | 558.8 ms | 1.28 | 1.29 | 4.50 | 9.4 ms | 1.91 | 1.93 |
| Q02 | 32 | 7.91 | 504.7 ms | 2.54 | 2.56 | 4.94 | 584.5 ms | 1.29 | 1.30 | 7.04 | 11.2 ms | 1.96 | 1.98 |
| Q03 | 1 | 0.88 | 21.5 ms | 2.47 | 2.49 | 1.22 | 109.6 ms | 1.28 | 1.28 | 0.91 | 5.8 ms | 1.98 | 1.99 |
| Q03 | 4 | 3.16 | 23.6 ms | 2.49 | 2.52 | 1.89 | 162.1 ms | 1.29 | 1.30 | 2.63 | 6.8 ms | 1.96 | 1.97 |
| Q03 | 8 | 5.24 | 25.9 ms | 2.66 | 2.77 | 2.12 | 186.9 ms | 1.30 | 1.31 | 4.13 | 7.7 ms | 1.93 | 1.95 |
| Q03 | 32 | 6.68 | 27.9 ms | 2.96 | 3.10 | 2.12 | 199.1 ms | 1.31 | 1.32 | 6.74 | 9.1 ms | 1.98 | 2.00 |
| Q04 | 1 | 0.83 | 15.8 ms | 3.07 | 3.08 | 0.99 | 84.4 ms | 1.31 | 1.32 | 1.00 | 10.2 ms | 1.99 | 2.00 |
| Q04 | 4 | 2.93 | 18.6 ms | 3.15 | 3.18 | 1.61 | 135.8 ms | 1.32 | 1.33 | 3.30 | 11.8 ms | 1.96 | 1.98 |
| Q04 | 8 | 4.58 | 20.3 ms | 3.28 | 3.34 | 1.83 | 159.1 ms | 1.34 | 1.34 | 4.28 | 12.3 ms | 1.95 | 1.96 |
| Q04 | 32 | 6.19 | 21.9 ms | 3.56 | 3.66 | 1.85 | 170.8 ms | 1.34 | 1.35 | 7.39 | 13.9 ms | 1.97 | 2.00 |
| Q05 | 1 | 1.00 | 418.4 ms | 3.62 | 3.63 | 1.03 | 580.4 ms | 1.36 | 1.36 | 0.83 | 4.3 ms | 1.98 | 1.99 |
| Q05 | 4 | 3.95 | 445.0 ms | 3.62 | 3.63 | 3.86 | 661.2 ms | 1.42 | 1.44 | 2.61 | 5.3 ms | 1.96 | 1.97 |
| Q05 | 8 | 7.75 | 538.5 ms | 3.62 | 3.64 | 6.03 | 781.2 ms | 1.46 | 1.54 | 4.10 | 6.0 ms | 1.94 | 1.95 |
| Q05 | 32 | 7.94 | 550.5 ms | 3.60 | 3.61 | 6.27 | 832.2 ms | 1.48 | 1.58 | 6.68 | 7.4 ms | 1.96 | 1.98 |
| Q06 | 1 | 1.00 | 413.6 ms | 3.50 | 3.51 | 1.03 | 582.9 ms | 1.36 | 1.36 | 0.97 | 6.7 ms | 1.97 | 1.98 |
| Q06 | 4 | 3.97 | 444.7 ms | 3.51 | 3.52 | 3.85 | 659.2 ms | 1.42 | 1.44 | 2.84 | 7.7 ms | 1.95 | 1.96 |
| Q06 | 8 | 7.68 | 535.3 ms | 3.50 | 3.51 | 5.83 | 777.6 ms | 1.46 | 1.55 | 4.12 | 8.5 ms | 1.93 | 1.94 |
| Q06 | 32 | 7.87 | 543.5 ms | 3.47 | 3.50 | 6.13 | 824.8 ms | 1.47 | 1.53 | 6.73 | 10.2 ms | 1.98 | 2.00 |
| Q07 | 1 | 1.00 | 287.9 ms | 3.38 | 3.40 | 1.03 | 605.9 ms | 1.36 | 1.37 | 0.88 | 5.0 ms | 1.99 | 2.00 |
| Q07 | 4 | 3.94 | 323.3 ms | 3.39 | 3.40 | 3.81 | 699.6 ms | 1.41 | 1.45 | 2.69 | 6.0 ms | 1.97 | 2.00 |
| Q07 | 8 | 7.59 | 369.9 ms | 3.38 | 3.39 | 5.88 | 819.6 ms | 1.46 | 1.54 | 3.75 | 6.8 ms | 1.95 | 1.97 |
| Q07 | 32 | 7.89 | 373.4 ms | 3.40 | 3.41 | 6.21 | 865.0 ms | 1.47 | 1.56 | 6.58 | 8.3 ms | 2.00 | 2.03 |
| Q10 | 1 | 0.93 | 29.5 ms | 3.34 | 3.36 | 0.95 | 96.1 ms | 1.35 | 1.35 | 1.19 | 16.0 ms | 2.01 | 2.03 |
| Q10 | 4 | 3.21 | 34.7 ms | 3.44 | 3.49 | 1.54 | 147.9 ms | 1.36 | 1.36 | 3.56 | 18.3 ms | 2.00 | 2.02 |
| Q10 | 8 | 5.00 | 38.7 ms | 3.62 | 3.76 | 1.80 | 172.8 ms | 1.37 | 1.37 | 5.09 | 19.4 ms | 1.99 | 2.01 |
| Q10 | 32 | 5.90 | 40.3 ms | 3.79 | 3.81 | 1.82 | 185.0 ms | 1.37 | 1.38 | 7.44 | 21.8 ms | 2.06 | 2.10 |
| Q11 | 1 | 1.03 | 221.6 ms | 3.77 | 3.77 | 0.94 | 260.9 ms | 1.41 | 1.42 | 0.31 | 129.7 ms | 2.08 | 2.09 |
| Q11 | 4 | 3.80 | 254.0 ms | 3.77 | 3.77 | 1.41 | 318.8 ms | 1.47 | 1.50 | 1.76 | 133.4 ms | 2.06 | 2.08 |
| Q11 | 8 | 6.05 | 282.8 ms | 3.79 | 3.83 | 1.49 | 347.0 ms | 1.55 | 1.58 | 3.37 | 139.6 ms | 2.06 | 2.08 |
| Q11 | 32 | 6.34 | 325.2 ms | 2.94 | 3.77 | 1.64 | 357.6 ms | 1.39 | 1.68 | 2.11 | 154.3 ms | 2.21 | 2.24 |
| Q12 | 1 | 1.01 | 423.1 ms | 1.28 | 1.28 | 1.03 | 579.2 ms | 0.86 | 0.88 | 0.82 | 4.1 ms | 1.74 | 1.77 |
| Q12 | 4 | 3.98 | 430.1 ms | 1.31 | 1.31 | 3.89 | 650.1 ms | 0.91 | 0.94 | 2.88 | 5.0 ms | 1.73 | 1.75 |
| Q12 | 8 | 7.76 | 535.3 ms | 1.34 | 1.41 | 6.27 | 774.5 ms | 0.95 | 1.04 | 3.96 | 5.7 ms | 1.73 | 1.75 |
| Q12 | 32 | 7.94 | 545.4 ms | 1.38 | 1.38 | 6.55 | 827.0 ms | 0.96 | 1.04 | 6.50 | 7.2 ms | 1.82 | 1.84 |
| Q13 | 1 | 1.00 | 367.9 ms | 1.35 | 1.35 | 1.16 | 408.3 ms | 0.83 | 0.83 | 2.77 | 326.2 ms | 1.85 | 1.86 |
| Q13 | 4 | 3.96 | 376.4 ms | 1.37 | 1.37 | 4.11 | 466.2 ms | 0.84 | 0.85 | 7.54 | 388.7 ms | 1.85 | 1.87 |
| Q13 | 8 | 7.71 | 457.9 ms | 1.39 | 1.40 | 5.55 | 547.1 ms | 0.84 | 0.86 | 7.96 | 391.6 ms | 1.85 | 1.87 |
| Q13 | 32 | 7.92 | 462.7 ms | 1.41 | 1.42 | 5.51 | 570.2 ms | 0.85 | 0.86 | 7.99 | 385.5 ms | 2.01 | 2.08 |
| mix | 1 | 1.01 | 257.5 ms | 1.16 | 1.17 | 1.14 | 367.0 ms | 1.22 | 1.23 | 0.95 | 6.5 ms | 1.77 | 1.78 |
| mix | 4 | 3.97 | 275.7 ms | 1.19 | 1.20 | 3.79 | 436.4 ms | 1.26 | 1.32 | 2.99 | 7.6 ms | 1.76 | 1.77 |
| mix | 8 | 7.54 | 319.5 ms | 1.33 | 1.35 | 4.84 | 510.0 ms | 1.29 | 1.36 | 4.44 | 8.6 ms | 1.79 | 1.80 |
| mix | 32 | 7.83 | 324.3 ms | 1.38 | 1.39 | 4.83 | 533.8 ms | 1.29 | 1.38 | 6.96 | 10.2 ms | 1.99 | 2.05 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | argus-final | — | 4.0 | 0.99 | 4.0 | 247.9 |
| csv | 1 | dachs-final | — | 3.2 | 1.14 | 2.8 | 361.4 |
| csv | 1 | egernia-skycell-w8 | 8 | 150.3 | 0.93 | 162.3 | 6.2 |
| csv | 4 | argus-final | — | 14.3 | 3.95 | 3.6 | 276.8 |
| csv | 4 | dachs-final | — | 9.2 | 3.90 | 2.4 | 426.7 |
| csv | 4 | egernia-skycell-w8 | 8 | 372.3 | 2.68 | 138.7 | 7.2 |
| csv | 8 | argus-final | — | 23.7 | 7.52 | 3.2 | 317.9 |
| csv | 8 | dachs-final | — | 9.7 | 4.89 | 2.0 | 508.1 |
| csv | 8 | egernia-skycell-w8 | 8 | 520.5 | 4.17 | 124.9 | 8.0 |
| csv | 32 | argus-final | — | 24.4 | 7.83 | 3.1 | 322.4 |
| csv | 32 | dachs-final | — | 9.3 | 4.88 | 1.9 | 534.8 |
| csv | 32 | egernia-skycell-w8 | 8 | 687.0 | 6.56 | 104.7 | 9.6 |
| votable | 1 | argus-final | — | 3.9 | 1.01 | 3.9 | 257.5 |
| votable | 1 | dachs-final | — | 3.1 | 1.14 | 2.7 | 367.0 |
| votable | 1 | egernia-skycell-w8 | 8 | 146.1 | 0.95 | 154.4 | 6.5 |
| votable | 4 | argus-final | — | 14.5 | 3.97 | 3.6 | 275.7 |
| votable | 4 | dachs-final | — | 8.8 | 3.79 | 2.3 | 436.4 |
| votable | 4 | egernia-skycell-w8 | 8 | 391.4 | 2.99 | 130.9 | 7.6 |
| votable | 8 | argus-final | — | 23.7 | 7.54 | 3.1 | 319.5 |
| votable | 8 | dachs-final | — | 9.6 | 4.84 | 2.0 | 510.0 |
| votable | 8 | egernia-skycell-w8 | 8 | 516.2 | 4.44 | 116.3 | 8.6 |
| votable | 32 | argus-final | — | 24.3 | 7.83 | 3.1 | 324.3 |
| votable | 32 | dachs-final | — | 9.2 | 4.83 | 1.9 | 533.8 |
| votable | 32 | egernia-skycell-w8 | 8 | 684.0 | 6.96 | 98.3 | 10.2 |

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
    -f benchmarks/tap-compare/final-skycell/pins/egernia-w8.yml \
    -f benchmarks/tap-compare/final-skycell/pins/skycell.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets argus-final dachs-final egernia-skycell-w8 --scenario <scenario>
```

Environment: see `environment.json` (git 19e19fcb, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Phase B of experiment 2 of the pre-registered skycell rerun (`benchmarks/tap-compare/final-skycell/PROTOCOL.md`): **Table B, equal CPU**. egernia on skycell with **eight** uvicorn workers, one per pinned core, against the same DaCHS and argus that phase A measured (`20261117T203446Z-d360fb1e-tap-compare`). It replaces `20260912T025434Z-41bfc513-tap-compare`.
- **Provenance.** Pre-registered at `tap-compare-final-skycell-prereg-v1`; amended at `-v2` before measurement, and at `-v3` and `-v4` after it began (amendments 2 and 3, below). Measured at `19e19fcb` up to the stop and `61542dc1` after it; the two commits differ in the drivers' failure handling and in which user DaCHS serves as, and in nothing a measured request touches.
- **This run was stopped once and resumed, and an earlier attempt was abandoned.** Stated in full because it is a deviation:
  - *Attempt 1* (`20261118T163043Z-d360fb1e-tap-compare`, on disk, unpublished): DaCHS answered 500 to everything from 00:37Z on 2026-11-19 and the harness measured its error responses for hours. Abandoned; amendment 2 added a stop when a rung's error fraction passes 50%, with the server's logs kept.
  - *This run*, started under amendment 2, stopped itself at 04:59Z on 2026-11-20 on `dachs-final-votable-Q11-c32-r3` (99.5% errors), after 358 rungs. The cause is a defect in DaCHS 2.11: a sync query's job is marked EXECUTING with pid −1; when the update that ends the job times out, destroying the job calls `os.kill(-1, SIGTERM)`, which as root signals every process in the container. PostgreSQL shuts down and DaCHS, PID 1, answers 500 from then on. The image starts DaCHS as root.
  - *Amendment 3*: DaCHS serves as the unprivileged `gavo` user, as the Debian package runs it, through the image's own entrypoint with its last line changed. The project lead decided to **resume** the run rather than measure it again: rungs 1-358 keep their values, and the stopped rung and everything after it were measured from 07:08Z.
  - **Where the split falls.** Rungs are ordered VOTable first. Segment 1 (DaCHS as root, 2026-11-19 20:44Z to 11-20 04:59Z) holds VOTable Q01 to Q10 and Q11 up to egernia's c=32 repetition 3. Segment 2 (DaCHS as `gavo`, 07:08Z to 18:48Z) holds DaCHS's and argus's repetition 3 of that cell, VOTable Q12, Q13 and the mix, and **all of CSV**. All three stacks were re-created at the resume and argus's job store truncated again, so segment 2 began from the same small history as a fresh phase. The gates recorded at the start are reused. Segment 1's pin records are under `pins/segment-1/`.
- **One rung is contaminated and is kept as measured.** egernia's `votable-Q11-c32-r3`, the last rung before the stop, measured **3.5 rps** at 04:58Z against 18.2 and 20.7 for the other two repetitions. It ran in the minute in which DaCHS's own database update timed out, which points to a stall of the whole host rather than of one container. It pulls that cell's mean to 14.1 rps and widens its interval, so the cell is a tie between egernia and argus; with the two clean repetitions alone egernia's mean would be 19.5. Nothing is dropped: the verdict stands as the rule gives it.
- **Gates.** All three `taplint` PASS (egernia 0 errors, DaCHS 0, argus 0 blocking / 2 total). **Three-way agreement 11/11 classes.**
- **Verdicts: egernia 89, ties 3, argus 4, DaCHS 0, of 96 cells** (the published Table B was 83 / 11 / 2 / 0; phase A here is 75 / 10 / 11 / 0). 864 rungs, 8,095,719 requests, 72% more than phase A. No generator guard tripped (peak 0.53).
- **H1 holds in 18 of 24 cells.** Q01, Q03, Q04 and Q10 gain at c=8 and c=32 in both formats, by 1.6-3.8×, with CPU per request up by at most 22%, inside the registered ±25%. On the mix at c=32, CSV: **231.3 → 687.0 rps (×2.97)** while cores used go 1.85 → 6.56 and CPU per request 8.0 → 9.6 ms (+20%). The factor grows with load as a worker-bound ceiling predicts: ×1.00 at c=1, ×1.43 at c=4, ×2.04 at c=8, ×2.97 at c=32. The six cells that do not gain are Q13's four (ties at 0.99-1.02×: the aggregate is PostgreSQL-bound and uses 7.96 cores in both phases) and Q11 at c=32 in both formats (CSV ×1.42 with overlapping intervals; VOTable is the contaminated cell).
- **The c=1 column is the control, and it behaves**: every class is within 5% of its phase A value except Q11.
- **Q11 at c=1 is still the regression**: 13.1 → 4.7 rps in CSV and 10.3 → 2.4 in VOTable, while CPU per request barely moves (94.9 → 96.2 ms) and cores used fall from 1.24 to 0.46. The server is waiting, not computing, as in the published table. It costs egernia the VOTable cells at c=1 and c=4, which go to argus.
- **H4 fails: egernia returns errors on Q13 at c=32, and that is new.** All six Q13 rungs at c=32 are over the 1% ceiling, at 3.1-7.6%: HTTP 500s (34 to 95 per rung) and a few dropped connections. These are the only rungs of the 864 above the ceiling. The cause is in the database container's log: `could not resize shared memory segment … No space left on device`. PostgreSQL's parallel workers allocate dynamic shared memory under `/dev/shm`, the container has Docker's default 64 MiB, and 32 concurrent parallel aggregates through eight workers' pools exhaust it. Phase A, whose single worker holds eight connections, has none. Under the ceiling rule egernia cannot win those two cells, so **both go to argus** (17.1 rps against egernia's 20.9 in CSV). The published Table B had no errors anywhere: the per-query shared memory has grown since `1845521`, or the plan has changed. The remedy is a `shm_size` on the database service; it is not applied here, because the protocol measures the stack as its compose file deploys it.
- **H2 holds for DaCHS and not for argus.** DaCHS ties its phase A cell in **95 of 96** (the exception is Q01 CSV at c=1, 23.1 → 25.6 rps). argus ties in **89 of 96** and is **slower in 7, all CSV**: Q11 at every concurrency (0.72-0.76×), Q10 at c=1 and c=32 (0.82×) and Q04 at c=32 (0.91×). All seven lie in segment 2. argus's VOTable cells in segment 2 (Q12, Q13, mix) tie, and its job store was smaller during this phase's CSV rungs than during phase A's, so neither the resume nor its job history explains it; it is unexplained. What it bounds: egernia's CSV gains on Q10 and Q11 against argus in this table are partly argus's loss, and are read against egernia's own phase A value, not against argus.
- **H3′ holds**: egernia wins every cell of Q05, Q06, Q07, Q12 and the mix, 40 of 40. **H5 holds**, as in phase A.
- **Where argus still wins**: four cells. Q11 in VOTable at c=1 and c=4 (the single-client regression), and Q13 at c=32 in both formats (the shed load). All eleven cells argus held in phase A changed hands.
- **Resources.** Mixed workload, c=32, CSV: egernia 687.0 rps on 6.56 cores at 9.6 ms per request; argus 24.4 rps on 7.83 cores at 322.4 ms; DaCHS 9.3 rps on 4.88 cores at 534.8 ms.

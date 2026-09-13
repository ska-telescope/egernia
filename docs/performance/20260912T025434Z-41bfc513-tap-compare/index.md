# 20260912T025434Z-41bfc513-tap-compare

Same-hardware TAP-server comparison: identical logical corpus, each
server deployed per its own documentation, one target under load at
a time (all stacks stay up so repetitions interleave), the identical
seeded query stream, MAXREC pinned on every request. Every target
stack is pinned to the same 8 CPU / 8 GiB budget: argus in `benchmarks/tap-compare/docker-compose.argus.yml` + `final/pins/argus.yml` (`cpuset` 8-15; 8 GiB split 3 Tomcat / 5 PostgreSQL; `benchmarks/tap-compare/final/PROTOCOL.md`); DaCHS in `benchmarks/tap-compare/docker-compose.dachs.yml` + `final/pins/dachs.yml` (`cpus: 8`, `cpuset` 16-23, `mem_limit: 8g`, its PostgreSQL sized to the container by the ¼ rule; `benchmarks/tap-compare/final/PROTOCOL.md`); egernia in `benchmarks/tap-compare/final/pins/egernia-w8.yml` (`cpuset` 0-7; 8 GiB split 4 db / 2 api / 2 executor; `TAP_API_WORKERS=8`, PostgreSQL parallel budget 144/152; `benchmarks/tap-compare/final/PROTOCOL.md`).
See `benchmarks/tap-compare/README.md` for the protocol.

## Gates

| target | TAP | taplint | maxrec default |
| --- | --- | --- | --- |
| argus-final | 1.1 | PASS (2 errors) | 134217728 |
| dachs-final | 1.1 | PASS (0 errors) | 20000 |
| egernia-final-w8 | 1.1 | PASS (0 errors) | 10000 |

Agreement gate: **11 classes agree**, none disagree.

## csv

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-final-w8 rps | egernia-final-w8 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 89.4 ±11.3 | 0.012 ±0.000 | 23.4 ±0.1 | 0.158 ±0.003 | 187.1 ±2.5 | 0.006 ±0.000 | egernia-final-w8 |
| Q01 | 4 | 244.1 ±59.5 | 0.016 ±0.000 | 18.8 ±0.7 | 0.327 ±0.008 | 462.8 ±180.1 | 0.013 ±0.008 | tie |
| Q01 | 8 | 389.7 ±86.8 | 0.022 ±0.000 | 17.4 ±0.3 | 0.560 ±0.015 | 590.5 ±273.9 | 0.024 ±0.020 | tie |
| Q01 | 32 | 566.3 ±27.9 | 0.065 ±0.000 | 16.1 ±0.1 | 2.136 ±0.021 | 800.1 ±13.4 | 0.080 ±0.022 | egernia-final-w8 |
| Q02 | 1 | 2.6 ±0.1 | 0.394 ±0.008 | 5.5 ±0.4 | 0.298 ±0.023 | 123.9 ±1.8 | 0.009 ±0.000 | egernia-final-w8 |
| Q02 | 4 | 9.0 ±1.0 | 0.497 ±0.006 | 10.3 ±0.1 | 0.533 ±0.016 | 293.4 ±113.0 | 0.020 ±0.010 | egernia-final-w8 |
| Q02 | 8 | 15.8 ±0.0 | 0.538 ±0.016 | 9.5 ±0.1 | 1.027 ±0.009 | 393.3 ±22.2 | 0.034 ±0.014 | egernia-final-w8 |
| Q02 | 32 | 16.0 ±0.1 | 2.087 ±0.016 | 8.9 ±1.0 | 4.757 ±4.156 | 541.5 ±20.3 | 0.113 ±0.051 | egernia-final-w8 |
| Q03 | 1 | 42.1 ±2.4 | 0.080 ±0.003 | 11.9 ±0.3 | 0.193 ±0.003 | 137.4 ±2.0 | 0.008 ±0.000 | egernia-final-w8 |
| Q03 | 4 | 138.2 ±2.6 | 0.093 ±0.001 | 12.5 ±0.2 | 0.463 ±0.010 | 353.5 ±7.2 | 0.016 ±0.000 | egernia-final-w8 |
| Q03 | 8 | 210.4 ±4.2 | 0.114 ±0.001 | 12.0 ±0.2 | 0.814 ±0.020 | 459.5 ±104.2 | 0.027 ±0.011 | egernia-final-w8 |
| Q03 | 32 | 251.0 ±11.9 | 0.237 ±0.009 | 11.4 ±0.2 | 3.010 ±0.050 | 593.7 ±48.1 | 0.102 ±0.037 | egernia-final-w8 |
| Q04 | 1 | 55.0 ±4.6 | 0.020 ±0.001 | 12.6 ±0.1 | 0.198 ±0.004 | 90.6 ±2.6 | 0.012 ±0.000 | egernia-final-w8 |
| Q04 | 4 | 164.0 ±1.3 | 0.029 ±0.000 | 12.7 ±0.2 | 0.448 ±0.010 | 236.7 ±41.6 | 0.022 ±0.005 | egernia-final-w8 |
| Q04 | 8 | 246.3 ±1.9 | 0.040 ±0.000 | 12.1 ±0.1 | 0.800 ±0.015 | 322.2 ±92.2 | 0.037 ±0.017 | tie |
| Q04 | 32 | 272.4 ±75.2 | 0.122 ±0.001 | 11.3 ±0.1 | 2.976 ±0.041 | 458.5 ±4.7 | 0.117 ±0.031 | egernia-final-w8 |
| Q05 | 1 | 2.4 ±0.0 | 0.415 ±0.002 | 1.9 ±0.0 | 0.654 ±0.008 | 163.0 ±1.8 | 0.007 ±0.000 | egernia-final-w8 |
| Q05 | 4 | 8.8 ±0.2 | 0.534 ±0.028 | 6.0 ±0.1 | 0.824 ±0.049 | 401.4 ±137.7 | 0.015 ±0.007 | egernia-final-w8 |
| Q05 | 8 | 14.6 ±0.1 | 0.573 ±0.004 | 8.0 ±0.1 | 1.267 ±0.099 | 503.7 ±78.5 | 0.024 ±0.007 | egernia-final-w8 |
| Q05 | 32 | 14.7 ±0.4 | 2.252 ±0.014 | 8.2 ±0.1 | 4.164 ±0.053 | 692.4 ±18.0 | 0.080 ±0.016 | egernia-final-w8 |
| Q06 | 1 | 2.5 ±0.1 | 0.414 ±0.008 | 1.9 ±0.0 | 0.657 ±0.009 | 138.2 ±3.0 | 0.009 ±0.000 | egernia-final-w8 |
| Q06 | 4 | 9.2 ±1.3 | 0.536 ±0.273 | 6.0 ±0.1 | 0.842 ±0.037 | 325.5 ±55.1 | 0.017 ±0.000 | egernia-final-w8 |
| Q06 | 8 | 14.7 ±0.1 | 0.588 ±0.006 | 7.9 ±0.1 | 1.271 ±0.058 | 410.4 ±91.9 | 0.035 ±0.017 | egernia-final-w8 |
| Q06 | 32 | 14.8 ±0.1 | 2.270 ±0.024 | 8.0 ±0.2 | 4.285 ±0.106 | 552.8 ±41.7 | 0.113 ±0.015 | egernia-final-w8 |
| Q07 | 1 | 3.5 ±0.1 | 0.408 ±0.010 | 1.7 ±0.0 | 0.691 ±0.021 | 150.0 ±5.8 | 0.008 ±0.000 | egernia-final-w8 |
| Q07 | 4 | 13.0 ±1.7 | 0.442 ±0.111 | 5.7 ±0.1 | 0.869 ±0.072 | 380.9 ±145.5 | 0.016 ±0.009 | egernia-final-w8 |
| Q07 | 8 | 20.7 ±0.1 | 0.548 ±0.011 | 7.6 ±0.1 | 1.299 ±0.019 | 469.8 ±96.7 | 0.027 ±0.006 | egernia-final-w8 |
| Q07 | 32 | 21.4 ±0.2 | 1.738 ±0.039 | 7.7 ±0.1 | 4.428 ±0.092 | 634.8 ±43.4 | 0.086 ±0.020 | egernia-final-w8 |
| Q10 | 1 | 36.2 ±1.2 | 0.031 ±0.001 | 10.8 ±0.0 | 0.214 ±0.002 | 75.5 ±1.3 | 0.016 ±0.000 | egernia-final-w8 |
| Q10 | 4 | 98.0 ±28.5 | 0.044 ±0.001 | 11.1 ±0.2 | 0.502 ±0.011 | 164.7 ±107.3 | 0.034 ±0.021 | tie |
| Q10 | 8 | 129.6 ±109.2 | 0.149 ±0.379 | 10.6 ±0.2 | 0.909 ±0.032 | 252.2 ±40.1 | 0.048 ±0.018 | tie |
| Q10 | 32 | 178.5 ±12.5 | 0.200 ±0.002 | 10.2 ±0.2 | 3.336 ±0.071 | 318.3 ±1.0 | 0.166 ±0.039 | egernia-final-w8 |
| Q11 | 1 | 6.1 ±0.1 | 0.171 ±0.008 | 3.6 ±0.1 | 0.397 ±0.002 | 4.7 ±0.2 | 0.244 ±0.006 | argus-final |
| Q11 | 4 | 19.2 ±0.0 | 0.232 ±0.006 | 4.0 ±0.1 | 1.241 ±0.077 | 18.3 ±4.6 | 0.314 ±0.029 | tie |
| Q11 | 8 | 27.6 ±0.2 | 0.333 ±0.005 | 4.0 ±0.1 | 2.697 ±0.473 | 34.7 ±3.3 | 0.357 ±0.082 | egernia-final-w8 |
| Q11 | 32 | 28.3 ±0.1 | 1.208 ±0.010 | 4.2 ±0.1 | 11.550 ±1.130 | 38.8 ±4.5 | 1.639 ±0.483 | egernia-final-w8 |
| Q12 | 1 | 2.5 ±0.0 | 0.412 ±0.006 | 1.9 ±0.0 | 0.651 ±0.005 | 166.7 ±0.6 | 0.007 ±0.000 | egernia-final-w8 |
| Q12 | 4 | 8.7 ±1.5 | 0.540 ±0.007 | 6.1 ±0.2 | 0.847 ±0.033 | 441.3 ±3.3 | 0.013 ±0.000 | egernia-final-w8 |
| Q12 | 8 | 14.7 ±0.2 | 0.572 ±0.007 | 8.0 ±0.1 | 1.235 ±0.035 | 521.9 ±108.4 | 0.026 ±0.007 | egernia-final-w8 |
| Q12 | 32 | 14.8 ±0.1 | 2.243 ±0.014 | 8.1 ±0.1 | 4.199 ±0.183 | 665.5 ±128.8 | 0.097 ±0.021 | egernia-final-w8 |
| Q13 | 1 | 2.8 ±0.0 | 0.399 ±0.010 | 2.9 ±0.2 | 0.480 ±0.068 | 7.6 ±0.2 | 0.175 ±0.008 | egernia-final-w8 |
| Q13 | 4 | 10.5 ±0.8 | 0.463 ±0.055 | 8.8 ±0.3 | 0.684 ±0.027 | 17.1 ±0.3 | 0.307 ±0.013 | egernia-final-w8 |
| Q13 | 8 | 17.4 ±0.2 | 0.546 ±0.001 | 10.0 ±0.3 | 1.124 ±0.094 | 17.6 ±0.2 | 0.603 ±0.007 | tie |
| Q13 | 32 | 17.8 ±0.4 | 1.949 ±0.028 | 9.6 ±0.1 | 3.669 ±0.040 | 17.6 ±0.2 | 2.386 ±0.061 | tie |
| mix | 1 | 4.2 ±0.6 | 0.407 ±0.005 | 3.2 ±0.2 | 0.602 ±0.081 | 130.4 ±0.1 | 0.012 ±0.000 | egernia-final-w8 |
| mix | 4 | 15.2 ±3.2 | 0.483 ±0.140 | 9.0 ±0.5 | 0.836 ±0.013 | 344.1 ±40.8 | 0.018 ±0.003 | egernia-final-w8 |
| mix | 8 | 23.9 ±1.1 | 0.574 ±0.004 | 9.6 ±0.4 | 1.305 ±0.016 | 455.3 ±60.9 | 0.029 ±0.000 | egernia-final-w8 |
| mix | 32 | 24.7 ±1.2 | 1.709 ±0.059 | 9.1 ±0.1 | 4.047 ±0.051 | 557.1 ±33.3 | 0.116 ±0.033 | egernia-final-w8 |

## votable

| class | c | argus-final rps | argus-final p95 (s) | dachs-final rps | dachs-final p95 (s) | egernia-final-w8 rps | egernia-final-w8 p95 (s) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 97.2 ±0.6 | 0.012 ±0.000 | 22.9 ±0.3 | 0.128 ±0.011 | 185.7 ±1.3 | 0.006 ±0.000 | egernia-final-w8 |
| Q01 | 4 | 273.1 ±22.5 | 0.016 ±0.001 | 18.2 ±0.5 | 0.325 ±0.019 | 501.8 ±10.6 | 0.012 ±0.000 | egernia-final-w8 |
| Q01 | 8 | 427.2 ±39.7 | 0.022 ±0.000 | 17.3 ±0.1 | 0.566 ±0.012 | 702.5 ±17.6 | 0.020 ±0.000 | egernia-final-w8 |
| Q01 | 32 | 566.3 ±26.8 | 0.065 ±0.001 | 15.6 ±0.1 | 2.199 ±0.032 | 776.8 ±66.8 | 0.085 ±0.043 | egernia-final-w8 |
| Q02 | 1 | 2.6 ±0.0 | 0.398 ±0.002 | 5.3 ±0.4 | 0.302 ±0.029 | 119.1 ±1.3 | 0.009 ±0.000 | egernia-final-w8 |
| Q02 | 4 | 9.4 ±1.5 | 0.473 ±0.108 | 10.2 ±0.1 | 0.539 ±0.032 | 319.2 ±33.1 | 0.017 ±0.003 | egernia-final-w8 |
| Q02 | 8 | 15.8 ±0.1 | 0.537 ±0.006 | 9.4 ±0.1 | 1.039 ±0.014 | 383.2 ±70.2 | 0.034 ±0.014 | egernia-final-w8 |
| Q02 | 32 | 16.0 ±0.1 | 2.092 ±0.055 | 9.0 ±0.1 | 3.812 ±0.032 | 524.9 ±29.5 | 0.118 ±0.040 | egernia-final-w8 |
| Q03 | 1 | 41.4 ±2.4 | 0.080 ±0.002 | 11.5 ±0.2 | 0.197 ±0.006 | 131.9 ±3.1 | 0.009 ±0.000 | egernia-final-w8 |
| Q03 | 4 | 133.1 ±8.5 | 0.093 ±0.001 | 12.1 ±0.3 | 0.474 ±0.019 | 307.3 ±118.1 | 0.019 ±0.009 | egernia-final-w8 |
| Q03 | 8 | 203.6 ±5.8 | 0.115 ±0.001 | 11.8 ±0.2 | 0.833 ±0.025 | 436.6 ±110.8 | 0.031 ±0.009 | egernia-final-w8 |
| Q03 | 32 | 249.1 ±3.8 | 0.237 ±0.005 | 11.2 ±0.3 | 3.055 ±0.100 | 566.1 ±45.6 | 0.115 ±0.053 | egernia-final-w8 |
| Q04 | 1 | 53.0 ±1.9 | 0.021 ±0.001 | 11.9 ±1.0 | 0.202 ±0.002 | 85.5 ±1.0 | 0.013 ±0.000 | egernia-final-w8 |
| Q04 | 4 | 146.0 ±23.8 | 0.034 ±0.008 | 12.3 ±0.5 | 0.453 ±0.022 | 224.0 ±27.1 | 0.024 ±0.003 | egernia-final-w8 |
| Q04 | 8 | 220.9 ±15.6 | 0.045 ±0.002 | 11.2 ±0.1 | 0.882 ±0.032 | 300.4 ±56.0 | 0.039 ±0.010 | egernia-final-w8 |
| Q04 | 32 | 270.0 ±56.4 | 0.131 ±0.000 | 10.8 ±0.5 | 3.176 ±0.229 | 431.0 ±4.9 | 0.123 ±0.014 | egernia-final-w8 |
| Q05 | 1 | 2.4 ±0.0 | 0.415 ±0.004 | 1.8 ±0.0 | 0.657 ±0.010 | 161.1 ±6.3 | 0.007 ±0.000 | egernia-final-w8 |
| Q05 | 4 | 9.0 ±1.3 | 0.543 ±0.009 | 6.0 ±0.3 | 0.834 ±0.089 | 408.9 ±154.7 | 0.013 ±0.005 | egernia-final-w8 |
| Q05 | 8 | 14.7 ±0.3 | 0.577 ±0.012 | 7.9 ±0.2 | 1.284 ±0.093 | 548.7 ±150.3 | 0.023 ±0.001 | egernia-final-w8 |
| Q05 | 32 | 14.8 ±0.1 | 2.250 ±0.020 | 8.0 ±0.3 | 4.289 ±0.145 | 681.1 ±11.0 | 0.085 ±0.012 | egernia-final-w8 |
| Q06 | 1 | 2.5 ±0.1 | 0.419 ±0.001 | 1.8 ±0.0 | 0.661 ±0.011 | 128.3 ±1.0 | 0.010 ±0.000 | egernia-final-w8 |
| Q06 | 4 | 9.0 ±1.1 | 0.547 ±0.012 | 5.9 ±0.1 | 0.835 ±0.077 | 282.8 ±89.6 | 0.022 ±0.008 | egernia-final-w8 |
| Q06 | 8 | 14.6 ±0.1 | 0.591 ±0.018 | 7.8 ±0.2 | 1.302 ±0.058 | 438.2 ±10.7 | 0.029 ±0.005 | egernia-final-w8 |
| Q06 | 32 | 14.7 ±0.1 | 2.288 ±0.010 | 7.9 ±0.3 | 4.345 ±0.117 | 529.7 ±7.7 | 0.112 ±0.014 | egernia-final-w8 |
| Q07 | 1 | 3.4 ±0.2 | 0.411 ±0.004 | 1.7 ±0.0 | 0.695 ±0.013 | 144.1 ±1.8 | 0.008 ±0.000 | egernia-final-w8 |
| Q07 | 4 | 12.3 ±0.2 | 0.488 ±0.018 | 5.5 ±0.1 | 0.900 ±0.064 | 312.2 ±258.1 | 0.018 ±0.016 | egernia-final-w8 |
| Q07 | 8 | 20.7 ±0.1 | 0.550 ±0.012 | 7.5 ±0.1 | 1.310 ±0.024 | 432.3 ±77.7 | 0.033 ±0.009 | egernia-final-w8 |
| Q07 | 32 | 21.3 ±0.2 | 1.740 ±0.005 | 7.6 ±0.1 | 4.519 ±0.132 | 592.4 ±60.7 | 0.101 ±0.010 | egernia-final-w8 |
| Q10 | 1 | 30.9 ±2.9 | 0.035 ±0.003 | 10.7 ±0.1 | 0.214 ±0.001 | 64.7 ±0.5 | 0.018 ±0.000 | egernia-final-w8 |
| Q10 | 4 | 89.6 ±13.2 | 0.050 ±0.001 | 11.1 ±0.1 | 0.493 ±0.015 | 160.1 ±41.2 | 0.033 ±0.012 | egernia-final-w8 |
| Q10 | 8 | 127.2 ±12.9 | 0.072 ±0.001 | 10.8 ±0.1 | 0.901 ±0.031 | 210.8 ±31.7 | 0.054 ±0.012 | egernia-final-w8 |
| Q10 | 32 | 146.8 ±22.0 | 0.239 ±0.005 | 10.4 ±0.2 | 3.279 ±0.077 | 276.3 ±9.5 | 0.199 ±0.024 | egernia-final-w8 |
| Q11 | 1 | 4.8 ±0.0 | 0.218 ±0.005 | 3.9 ±0.1 | 0.376 ±0.004 | 2.5 ±0.1 | 0.526 ±0.009 | argus-final |
| Q11 | 4 | 15.3 ±0.2 | 0.295 ±0.004 | 4.4 ±0.3 | 1.212 ±0.335 | 14.8 ±0.9 | 0.406 ±0.032 | tie |
| Q11 | 8 | 22.0 ±0.1 | 0.420 ±0.005 | 4.5 ±0.1 | 2.363 ±0.531 | 27.1 ±2.1 | 0.496 ±0.132 | egernia-final-w8 |
| Q11 | 32 | 22.4 ±0.1 | 1.521 ±0.006 | 4.6 ±0.1 | 10.982 ±0.343 | 31.9 ±2.2 | 2.020 ±0.095 | egernia-final-w8 |
| Q12 | 1 | 2.5 ±0.0 | 0.412 ±0.006 | 1.8 ±0.0 | 0.654 ±0.009 | 163.9 ±3.4 | 0.007 ±0.000 | egernia-final-w8 |
| Q12 | 4 | 8.9 ±0.5 | 0.531 ±0.038 | 6.0 ±0.2 | 0.832 ±0.055 | 448.6 ±180.5 | 0.012 ±0.004 | egernia-final-w8 |
| Q12 | 8 | 14.7 ±0.0 | 0.574 ±0.011 | 7.9 ±0.1 | 1.284 ±0.009 | 548.8 ±195.9 | 0.025 ±0.014 | egernia-final-w8 |
| Q12 | 32 | 14.8 ±0.1 | 2.249 ±0.004 | 8.1 ±0.0 | 4.206 ±0.082 | 690.4 ±31.8 | 0.109 ±0.031 | egernia-final-w8 |
| Q13 | 1 | 2.8 ±0.1 | 0.395 ±0.001 | 2.9 ±0.2 | 0.472 ±0.046 | 7.6 ±0.3 | 0.176 ±0.003 | egernia-final-w8 |
| Q13 | 4 | 10.5 ±0.9 | 0.472 ±0.115 | 8.6 ±0.0 | 0.710 ±0.022 | 17.0 ±0.1 | 0.312 ±0.003 | egernia-final-w8 |
| Q13 | 8 | 17.3 ±0.3 | 0.548 ±0.006 | 9.9 ±0.0 | 1.122 ±0.015 | 17.7 ±0.5 | 0.604 ±0.021 | tie |
| Q13 | 32 | 17.7 ±0.0 | 1.957 ±0.006 | 9.5 ±0.1 | 3.706 ±0.038 | 17.6 ±0.3 | 2.387 ±0.083 | tie |
| mix | 1 | 4.1 ±0.6 | 0.413 ±0.003 | 3.2 ±0.2 | 0.619 ±0.004 | 125.0 ±4.2 | 0.014 ±0.001 | egernia-final-w8 |
| mix | 4 | 15.2 ±2.3 | 0.462 ±0.144 | 9.1 ±0.3 | 0.834 ±0.020 | 310.6 ±68.8 | 0.021 ±0.005 | egernia-final-w8 |
| mix | 8 | 23.7 ±1.2 | 0.579 ±0.008 | 9.8 ±0.6 | 1.273 ±0.051 | 394.8 ±109.8 | 0.035 ±0.017 | egernia-final-w8 |
| mix | 32 | 24.5 ±1.3 | 1.710 ±0.046 | 9.4 ±0.5 | 3.914 ±0.058 | 540.7 ±11.8 | 0.127 ±0.066 | egernia-final-w8 |

## resources, csv

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-final-w8 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.65 | 7.3 ms | 3.50 | 3.54 | 0.96 | 40.8 ms | 1.07 | 1.07 | 0.88 | 4.7 ms | 2.41 | 2.44 |
| Q01 | 4 | 2.05 | 8.4 ms | 3.71 | 3.84 | 1.77 | 94.3 ms | 1.08 | 1.09 | 2.62 | 5.7 ms | 2.29 | 2.32 |
| Q01 | 8 | 3.50 | 9.0 ms | 4.09 | 4.19 | 1.93 | 110.7 ms | 1.09 | 1.09 | 3.86 | 6.6 ms | 2.21 | 2.24 |
| Q01 | 32 | 5.80 | 10.2 ms | 4.31 | 4.42 | 1.88 | 118.7 ms | 1.09 | 1.10 | 6.54 | 8.2 ms | 2.20 | 2.23 |
| Q02 | 1 | 1.00 | 387.6 ms | 4.39 | 4.39 | 2.21 | 405.4 ms | 1.09 | 1.09 | 0.97 | 7.9 ms | 2.17 | 2.19 |
| Q02 | 4 | 3.97 | 441.9 ms | 4.40 | 4.41 | 5.18 | 501.5 ms | 1.10 | 1.11 | 2.72 | 9.3 ms | 2.15 | 2.16 |
| Q02 | 8 | 7.72 | 491.0 ms | 4.39 | 4.41 | 5.16 | 546.4 ms | 1.10 | 1.11 | 4.03 | 10.2 ms | 2.12 | 2.13 |
| Q02 | 32 | 7.91 | 498.6 ms | 4.34 | 4.36 | 4.89 | 561.7 ms | 1.10 | 1.12 | 6.70 | 12.4 ms | 2.18 | 2.21 |
| Q03 | 1 | 0.87 | 20.6 ms | 4.20 | 4.28 | 1.23 | 103.6 ms | 1.08 | 1.09 | 0.96 | 7.0 ms | 2.19 | 2.20 |
| Q03 | 4 | 3.15 | 22.8 ms | 4.16 | 4.18 | 1.93 | 154.5 ms | 1.07 | 1.08 | 2.91 | 8.2 ms | 2.16 | 2.17 |
| Q03 | 8 | 5.24 | 24.9 ms | 4.24 | 4.28 | 2.13 | 178.3 ms | 1.08 | 1.09 | 4.24 | 9.2 ms | 2.15 | 2.16 |
| Q03 | 32 | 6.81 | 27.2 ms | 4.38 | 4.50 | 2.11 | 189.7 ms | 1.08 | 1.09 | 6.51 | 11.0 ms | 2.19 | 2.22 |
| Q04 | 1 | 0.83 | 15.1 ms | 4.46 | 4.47 | 0.98 | 77.7 ms | 1.07 | 1.07 | 1.02 | 11.3 ms | 2.20 | 2.21 |
| Q04 | 4 | 2.90 | 17.7 ms | 4.48 | 4.50 | 1.62 | 127.8 ms | 1.08 | 1.08 | 3.06 | 12.9 ms | 2.17 | 2.17 |
| Q04 | 8 | 4.66 | 18.9 ms | 4.56 | 4.59 | 1.83 | 151.1 ms | 1.08 | 1.09 | 4.51 | 14.0 ms | 2.14 | 2.15 |
| Q04 | 32 | 5.58 | 20.5 ms | 4.75 | 4.92 | 1.84 | 163.9 ms | 1.09 | 1.09 | 7.23 | 15.8 ms | 2.18 | 2.20 |
| Q05 | 1 | 1.00 | 410.0 ms | 4.89 | 4.89 | 1.05 | 562.5 ms | 1.10 | 1.10 | 0.90 | 5.5 ms | 2.20 | 2.21 |
| Q05 | 4 | 3.97 | 453.3 ms | 4.90 | 4.91 | 3.94 | 654.8 ms | 1.16 | 1.19 | 2.66 | 6.6 ms | 2.17 | 2.19 |
| Q05 | 8 | 7.75 | 533.2 ms | 4.88 | 4.91 | 6.09 | 770.3 ms | 1.20 | 1.27 | 3.84 | 7.6 ms | 2.15 | 2.15 |
| Q05 | 32 | 7.95 | 545.1 ms | 4.85 | 4.88 | 6.55 | 824.9 ms | 1.23 | 1.32 | 6.46 | 9.3 ms | 2.20 | 2.23 |
| Q06 | 1 | 1.00 | 402.4 ms | 4.75 | 4.76 | 1.05 | 563.4 ms | 1.10 | 1.11 | 1.01 | 7.3 ms | 2.21 | 2.22 |
| Q06 | 4 | 3.87 | 421.6 ms | 4.74 | 4.75 | 3.90 | 653.5 ms | 1.16 | 1.19 | 2.84 | 8.7 ms | 2.17 | 2.18 |
| Q06 | 8 | 7.70 | 526.5 ms | 4.72 | 4.74 | 6.02 | 767.3 ms | 1.21 | 1.28 | 3.99 | 9.7 ms | 2.15 | 2.17 |
| Q06 | 32 | 7.90 | 539.1 ms | 4.68 | 4.71 | 6.30 | 817.2 ms | 1.22 | 1.29 | 6.43 | 11.6 ms | 2.21 | 2.22 |
| Q07 | 1 | 1.00 | 286.8 ms | 4.58 | 4.60 | 1.04 | 607.1 ms | 1.10 | 1.11 | 0.93 | 6.2 ms | 2.22 | 2.23 |
| Q07 | 4 | 3.95 | 304.5 ms | 4.58 | 4.60 | 3.92 | 695.6 ms | 1.16 | 1.19 | 2.80 | 7.4 ms | 2.18 | 2.21 |
| Q07 | 8 | 7.61 | 369.7 ms | 4.55 | 4.57 | 6.10 | 814.8 ms | 1.21 | 1.28 | 3.96 | 8.4 ms | 2.17 | 2.18 |
| Q07 | 32 | 7.90 | 372.6 ms | 4.50 | 4.56 | 6.42 | 859.3 ms | 1.21 | 1.31 | 6.47 | 10.2 ms | 2.23 | 2.26 |
| Q10 | 1 | 0.92 | 25.3 ms | 4.37 | 4.40 | 0.98 | 91.1 ms | 1.09 | 1.09 | 1.21 | 16.0 ms | 2.24 | 2.26 |
| Q10 | 4 | 2.85 | 29.1 ms | 4.46 | 4.52 | 1.58 | 142.1 ms | 1.09 | 1.10 | 2.99 | 18.1 ms | 2.21 | 2.22 |
| Q10 | 8 | 4.11 | 31.4 ms | 4.58 | 4.63 | 1.77 | 168.0 ms | 1.10 | 1.10 | 4.98 | 19.8 ms | 2.18 | 2.19 |
| Q10 | 32 | 5.84 | 32.8 ms | 4.78 | 4.82 | 1.81 | 180.8 ms | 1.10 | 1.11 | 7.04 | 22.1 ms | 2.23 | 2.25 |
| Q11 | 1 | 1.04 | 170.4 ms | 4.78 | 4.78 | 0.99 | 279.5 ms | 1.11 | 1.12 | 0.47 | 99.4 ms | 2.24 | 2.25 |
| Q11 | 4 | 3.78 | 196.6 ms | 4.78 | 4.79 | 1.38 | 344.6 ms | 1.13 | 1.15 | 1.91 | 104.4 ms | 2.21 | 2.23 |
| Q11 | 8 | 5.85 | 212.8 ms | 4.74 | 4.76 | 1.46 | 367.4 ms | 1.16 | 1.20 | 3.83 | 110.6 ms | 2.20 | 2.21 |
| Q11 | 32 | 6.11 | 217.1 ms | 4.70 | 4.71 | 1.59 | 390.2 ms | 1.20 | 1.24 | 4.69 | 121.0 ms | 2.35 | 2.40 |
| Q12 | 1 | 1.00 | 405.8 ms | 4.62 | 4.63 | 1.05 | 561.8 ms | 1.15 | 1.16 | 0.90 | 5.4 ms | 2.30 | 2.31 |
| Q12 | 4 | 3.96 | 459.3 ms | 4.61 | 4.62 | 3.92 | 650.3 ms | 1.20 | 1.23 | 2.84 | 6.4 ms | 2.27 | 2.28 |
| Q12 | 8 | 7.76 | 528.4 ms | 4.61 | 4.63 | 6.11 | 767.8 ms | 1.23 | 1.31 | 3.85 | 7.4 ms | 2.25 | 2.26 |
| Q12 | 32 | 7.95 | 544.9 ms | 4.58 | 4.59 | 6.47 | 813.0 ms | 1.24 | 1.32 | 6.04 | 9.1 ms | 2.29 | 2.31 |
| Q13 | 1 | 1.00 | 353.7 ms | 4.53 | 4.54 | 1.18 | 406.7 ms | 1.11 | 1.12 | 2.81 | 370.6 ms | 2.31 | 2.32 |
| Q13 | 4 | 3.96 | 377.5 ms | 4.54 | 4.55 | 4.09 | 469.4 ms | 1.12 | 1.13 | 7.72 | 452.4 ms | 2.31 | 2.31 |
| Q13 | 8 | 7.71 | 444.3 ms | 4.54 | 4.55 | 5.38 | 540.9 ms | 1.13 | 1.14 | 7.97 | 453.3 ms | 2.30 | 2.31 |
| Q13 | 32 | 7.94 | 446.7 ms | 4.56 | 4.56 | 5.36 | 565.8 ms | 1.13 | 1.15 | 7.99 | 455.3 ms | 2.46 | 2.49 |
| mix | 1 | 1.00 | 239.7 ms | 3.37 | 3.38 | 1.15 | 359.0 ms | 1.08 | 1.09 | 0.98 | 7.5 ms | 2.25 | 2.27 |
| mix | 4 | 3.94 | 261.5 ms | 3.40 | 3.41 | 3.84 | 430.5 ms | 1.13 | 1.17 | 3.05 | 8.9 ms | 2.27 | 2.29 |
| mix | 8 | 7.56 | 318.1 ms | 3.43 | 3.43 | 4.82 | 507.8 ms | 1.15 | 1.25 | 4.52 | 9.9 ms | 2.27 | 2.31 |
| mix | 32 | 7.87 | 320.6 ms | 3.45 | 3.47 | 4.80 | 535.5 ms | 1.14 | 1.21 | 6.54 | 11.7 ms | 2.41 | 2.46 |

## resources, votable

| class | c | argus-final cores | CPU s/req | mem mean GiB | mem peak GiB | dachs-final cores | CPU s/req | mem mean GiB | mem peak GiB | egernia-final-w8 cores | CPU s/req | mem mean GiB | mem peak GiB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | 1 | 0.69 | 7.1 ms | 1.20 | 1.23 | 0.95 | 41.6 ms | 0.79 | 0.80 | 0.88 | 4.7 ms | 2.12 | 2.17 |
| Q01 | 4 | 2.24 | 8.2 ms | 1.41 | 1.53 | 1.77 | 97.3 ms | 0.81 | 0.82 | 2.84 | 5.7 ms | 2.02 | 2.05 |
| Q01 | 8 | 3.86 | 9.0 ms | 1.74 | 1.90 | 1.96 | 113.9 ms | 0.83 | 0.83 | 4.54 | 6.5 ms | 1.95 | 1.99 |
| Q01 | 32 | 5.69 | 10.0 ms | 2.21 | 2.41 | 1.91 | 123.6 ms | 0.84 | 0.85 | 6.34 | 8.2 ms | 1.94 | 1.95 |
| Q02 | 1 | 1.00 | 390.9 ms | 2.38 | 2.38 | 2.20 | 417.7 ms | 0.84 | 0.84 | 0.99 | 8.3 ms | 1.92 | 1.95 |
| Q02 | 4 | 3.96 | 422.2 ms | 2.40 | 2.40 | 5.13 | 505.9 ms | 0.85 | 0.86 | 3.10 | 9.7 ms | 1.92 | 1.93 |
| Q02 | 8 | 7.71 | 489.8 ms | 2.39 | 2.41 | 5.17 | 549.4 ms | 0.86 | 0.87 | 4.13 | 10.8 ms | 1.90 | 1.92 |
| Q02 | 32 | 7.90 | 499.8 ms | 2.39 | 2.40 | 5.03 | 575.3 ms | 0.86 | 0.88 | 6.79 | 12.9 ms | 1.96 | 1.98 |
| Q03 | 1 | 0.87 | 21.0 ms | 2.32 | 2.35 | 1.22 | 105.8 ms | 0.85 | 0.85 | 0.96 | 7.3 ms | 1.98 | 2.00 |
| Q03 | 4 | 3.10 | 23.3 ms | 2.35 | 2.40 | 1.92 | 158.8 ms | 0.85 | 0.86 | 2.67 | 8.7 ms | 1.96 | 1.97 |
| Q03 | 8 | 5.15 | 25.3 ms | 2.53 | 2.63 | 2.13 | 181.6 ms | 0.86 | 0.87 | 4.22 | 9.7 ms | 1.95 | 1.96 |
| Q03 | 32 | 6.79 | 27.3 ms | 2.81 | 2.95 | 2.12 | 192.2 ms | 0.86 | 0.87 | 6.45 | 11.4 ms | 1.98 | 1.99 |
| Q04 | 1 | 0.83 | 15.8 ms | 2.92 | 2.94 | 0.96 | 80.5 ms | 0.85 | 0.85 | 1.02 | 11.9 ms | 1.98 | 1.99 |
| Q04 | 4 | 2.77 | 19.0 ms | 3.00 | 3.05 | 1.59 | 129.6 ms | 0.86 | 0.86 | 3.08 | 13.7 ms | 1.93 | 1.95 |
| Q04 | 8 | 4.44 | 20.1 ms | 3.13 | 3.20 | 1.74 | 156.2 ms | 0.86 | 0.87 | 4.52 | 15.1 ms | 1.92 | 1.94 |
| Q04 | 32 | 5.83 | 21.6 ms | 3.37 | 3.47 | 1.77 | 167.2 ms | 0.87 | 0.87 | 7.29 | 16.9 ms | 1.96 | 2.00 |
| Q05 | 1 | 1.00 | 410.9 ms | 3.43 | 3.43 | 1.05 | 569.0 ms | 0.88 | 0.88 | 0.90 | 5.6 ms | 1.98 | 1.99 |
| Q05 | 4 | 3.96 | 441.9 ms | 3.44 | 3.44 | 3.92 | 661.0 ms | 0.93 | 0.96 | 2.78 | 6.8 ms | 1.97 | 1.99 |
| Q05 | 8 | 7.75 | 529.9 ms | 3.44 | 3.45 | 6.02 | 775.0 ms | 0.98 | 1.06 | 4.27 | 7.8 ms | 1.94 | 1.97 |
| Q05 | 32 | 7.94 | 542.4 ms | 3.41 | 3.42 | 6.42 | 827.3 ms | 1.00 | 1.10 | 6.51 | 9.6 ms | 1.98 | 1.99 |
| Q06 | 1 | 1.00 | 407.9 ms | 3.32 | 3.34 | 1.05 | 568.0 ms | 0.88 | 0.89 | 1.03 | 8.0 ms | 1.98 | 1.99 |
| Q06 | 4 | 3.97 | 445.7 ms | 3.33 | 3.34 | 3.88 | 659.4 ms | 0.94 | 0.97 | 2.68 | 9.5 ms | 1.94 | 1.96 |
| Q06 | 8 | 7.68 | 530.1 ms | 3.33 | 3.33 | 5.94 | 772.3 ms | 0.98 | 1.06 | 4.68 | 10.7 ms | 1.93 | 1.95 |
| Q06 | 32 | 7.88 | 539.8 ms | 3.31 | 3.32 | 6.29 | 814.4 ms | 1.00 | 1.10 | 6.70 | 12.7 ms | 2.01 | 2.03 |
| Q07 | 1 | 1.00 | 289.1 ms | 3.22 | 3.24 | 1.04 | 611.6 ms | 0.88 | 0.89 | 0.94 | 6.5 ms | 2.02 | 2.03 |
| Q07 | 4 | 3.96 | 323.8 ms | 3.23 | 3.24 | 3.89 | 708.6 ms | 0.95 | 0.97 | 2.47 | 8.0 ms | 1.99 | 2.00 |
| Q07 | 8 | 7.59 | 368.8 ms | 3.23 | 3.25 | 6.08 | 815.4 ms | 0.99 | 1.07 | 3.79 | 8.8 ms | 1.97 | 1.98 |
| Q07 | 32 | 7.88 | 371.9 ms | 3.25 | 3.26 | 6.35 | 868.4 ms | 1.00 | 1.10 | 6.30 | 10.6 ms | 2.02 | 2.06 |
| Q10 | 1 | 0.91 | 29.3 ms | 3.20 | 3.22 | 0.98 | 92.3 ms | 0.87 | 0.88 | 1.19 | 18.5 ms | 2.04 | 2.07 |
| Q10 | 4 | 3.04 | 34.0 ms | 3.29 | 3.33 | 1.58 | 142.3 ms | 0.88 | 0.88 | 3.42 | 21.3 ms | 2.02 | 2.04 |
| Q10 | 8 | 4.71 | 37.0 ms | 3.46 | 3.58 | 1.79 | 166.4 ms | 0.89 | 0.89 | 4.89 | 23.2 ms | 2.00 | 2.01 |
| Q10 | 32 | 5.71 | 38.9 ms | 3.58 | 3.61 | 1.84 | 179.5 ms | 0.90 | 0.91 | 7.14 | 25.9 ms | 2.07 | 2.10 |
| Q11 | 1 | 1.03 | 213.4 ms | 3.57 | 3.57 | 1.00 | 256.6 ms | 0.93 | 0.95 | 0.32 | 125.4 ms | 2.08 | 2.10 |
| Q11 | 4 | 3.78 | 247.2 ms | 3.58 | 3.59 | 1.39 | 315.0 ms | 1.00 | 1.02 | 1.94 | 130.6 ms | 2.06 | 2.08 |
| Q11 | 8 | 6.01 | 274.0 ms | 3.57 | 3.58 | 1.51 | 339.0 ms | 1.05 | 1.08 | 3.78 | 139.7 ms | 2.05 | 2.07 |
| Q11 | 32 | 6.21 | 279.6 ms | 3.53 | 3.54 | 1.63 | 350.9 ms | 1.15 | 1.20 | 4.91 | 154.2 ms | 2.22 | 2.27 |
| Q12 | 1 | 1.00 | 404.8 ms | 3.44 | 3.45 | 1.05 | 566.4 ms | 1.12 | 1.13 | 0.90 | 5.5 ms | 2.15 | 2.16 |
| Q12 | 4 | 3.96 | 443.9 ms | 3.44 | 3.45 | 3.90 | 657.8 ms | 1.16 | 1.19 | 2.95 | 6.6 ms | 2.13 | 2.15 |
| Q12 | 8 | 7.77 | 532.0 ms | 3.44 | 3.44 | 6.04 | 771.8 ms | 1.19 | 1.29 | 4.14 | 7.6 ms | 2.10 | 2.12 |
| Q12 | 32 | 7.94 | 541.2 ms | 3.43 | 3.45 | 6.47 | 825.3 ms | 1.20 | 1.30 | 6.35 | 9.2 ms | 2.15 | 2.16 |
| Q13 | 1 | 1.00 | 351.5 ms | 3.37 | 3.38 | 1.18 | 409.5 ms | 1.08 | 1.08 | 2.81 | 371.1 ms | 2.16 | 2.18 |
| Q13 | 4 | 3.95 | 376.5 ms | 3.38 | 3.39 | 4.05 | 471.5 ms | 1.07 | 1.09 | 7.70 | 453.5 ms | 2.17 | 2.19 |
| Q13 | 8 | 7.69 | 445.8 ms | 3.41 | 3.41 | 5.37 | 546.2 ms | 1.08 | 1.09 | 7.97 | 452.0 ms | 2.15 | 2.18 |
| Q13 | 32 | 7.93 | 451.2 ms | 3.41 | 3.42 | 5.34 | 569.3 ms | 1.09 | 1.10 | 7.99 | 454.3 ms | 2.34 | 2.38 |
| mix | 1 | 1.01 | 247.3 ms | 1.06 | 1.07 | 1.16 | 366.7 ms | 0.79 | 0.80 | 0.99 | 7.9 ms | 1.86 | 1.88 |
| mix | 4 | 3.99 | 263.3 ms | 1.09 | 1.12 | 3.87 | 430.2 ms | 0.84 | 0.88 | 2.94 | 9.5 ms | 1.84 | 1.85 |
| mix | 8 | 7.53 | 318.8 ms | 1.15 | 1.17 | 4.93 | 507.0 ms | 0.86 | 0.94 | 4.17 | 10.6 ms | 1.88 | 1.91 |
| mix | 32 | 7.85 | 321.7 ms | 1.20 | 1.22 | 4.97 | 532.6 ms | 0.87 | 0.95 | 6.74 | 12.5 ms | 2.10 | 2.16 |

## throughput vs CPU cores used (mix)

| format | c | target | API workers | rps | cores | rps per core | CPU ms/req |
| --- | --- | --- | --- | --- | --- | --- | --- |
| csv | 1 | argus-final | — | 4.2 | 1.00 | 4.2 | 239.7 |
| csv | 1 | dachs-final | — | 3.2 | 1.15 | 2.8 | 359.0 |
| csv | 1 | egernia-final-w8 | 8 | 130.4 | 0.98 | 133.3 | 7.5 |
| csv | 4 | argus-final | — | 15.2 | 3.94 | 3.9 | 261.5 |
| csv | 4 | dachs-final | — | 9.0 | 3.84 | 2.3 | 430.5 |
| csv | 4 | egernia-final-w8 | 8 | 344.1 | 3.05 | 112.9 | 8.9 |
| csv | 8 | argus-final | — | 23.9 | 7.56 | 3.2 | 318.1 |
| csv | 8 | dachs-final | — | 9.6 | 4.82 | 2.0 | 507.8 |
| csv | 8 | egernia-final-w8 | 8 | 455.3 | 4.52 | 100.8 | 9.9 |
| csv | 32 | argus-final | — | 24.7 | 7.87 | 3.1 | 320.6 |
| csv | 32 | dachs-final | — | 9.1 | 4.80 | 1.9 | 535.5 |
| csv | 32 | egernia-final-w8 | 8 | 557.1 | 6.54 | 85.2 | 11.7 |
| votable | 1 | argus-final | — | 4.1 | 1.01 | 4.1 | 247.3 |
| votable | 1 | dachs-final | — | 3.2 | 1.16 | 2.7 | 366.7 |
| votable | 1 | egernia-final-w8 | 8 | 125.0 | 0.99 | 126.8 | 7.9 |
| votable | 4 | argus-final | — | 15.2 | 3.99 | 3.8 | 263.3 |
| votable | 4 | dachs-final | — | 9.1 | 3.87 | 2.3 | 430.2 |
| votable | 4 | egernia-final-w8 | 8 | 310.6 | 2.94 | 105.7 | 9.5 |
| votable | 8 | argus-final | — | 23.7 | 7.53 | 3.1 | 318.8 |
| votable | 8 | dachs-final | — | 9.8 | 4.93 | 2.0 | 507.0 |
| votable | 8 | egernia-final-w8 | 8 | 394.8 | 4.17 | 94.6 | 10.6 |
| votable | 32 | argus-final | — | 24.5 | 7.85 | 3.1 | 321.7 |
| votable | 32 | dachs-final | — | 9.4 | 4.97 | 1.9 | 532.6 |
| votable | 32 | egernia-final-w8 | 8 | 540.7 | 6.74 | 80.2 | 12.5 |

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
    -f benchmarks/tap-compare/final/pins/egernia-w8.yml up -d
uv run --group tap-compare python benchmarks/tap-compare compare \
    --targets argus-final dachs-final egernia-final-w8 --scenario <scenario>
```

Environment: see `environment.json` (git 41bfc513, seed 424242, corpus 9f9da00f45f1…).

## Run notes

- **What this is.** Phase B of the pre-registered final three-way comparison (`benchmarks/tap-compare/final/PROTOCOL.md`): **Table B — equal CPU**. egernia with **eight** uvicorn workers, one per pinned core, against **the same** GAVO DaCHS and the same CADC argus that phase A measured, unchanged in every respect. All three up at once on disjoint cpusets (egernia 0-7, argus 8-15, DaCHS 16-23, generator 24-29), interleaved A,B,C inside every cell. Together with phase A (`20260911T065452Z-41bfc513-tap-compare`) these two tables replace every earlier performance table.
- **Provenance.** Pre-registered at tag `tap-compare-final-prereg-v1` = `dbff366`; measured at `41bfc513`, the same commit phase A was measured at. The commits between tag and measurement touch only `final/PROTOCOL.md` (prose and amendment 1), `final/run.sh` (the pre-measurement verification and refusal path) and `tests/test_final.py`: `git diff dbff366..41bfc513` restricted to `final/scenarios.yaml`, `final/targets.yaml`, `final/pins/` and the frozen `config/` is **empty**. The workload, grid, windows, repetitions, gate criteria, statistics, tie rule, error ceiling, generator guard and every pin are byte-identical to the pre-registration, and identical between the two phases.
- **The only difference between the phases**, as registered: `TAP_API_WORKERS` 1 → 8, and PostgreSQL's parallel budget re-derived by `docs/postgres-performance.md`'s rule for the resulting pool total ((8 × 8) + 8 = 72 connections < `max_connections` 100, so `max_parallel_workers` 144 and `max_worker_processes` 152). The memory split (4 db / 2 api / 2 executor), the cpuset, the pool size per worker, DaCHS and argus are all unchanged.
- **Gates.** All three `taplint` PASS — egernia 0 errors, DaCHS 0, argus 0 blocking / 2 total (the TAP_UPLOAD-by-URL stage, exactly as in phase A). **Three-way agreement 11/11 classes**, so Table B carries the same twelve rows as Table A and the two are comparable cell for cell.
- **Verdicts: egernia 83, ties 11, argus 2, DaCHS 0 — of 96 cells** (phase A was 66 / 12 / 18 / 0). **No rung invalidated, no generator guard tripped (peak 0.52), not one rung of 864 above 1% errors**, across 6,794,712 requests — 75% more than phase A pushed through the same hardware.
- **H1 holds, and the mechanism is visible.** On the registered set (Q01, Q03, Q04, Q10, Q11, Q13 at c ≥ 8, both formats) eight workers beat one in **20 of 24 cells**; the four that do not are Q13, which ties. On the mixed workload at c=32, CSV: throughput **167.7 → 557.1 rps (×3.32)** while **cores used go 1.75 → 6.54** and **CPU per request goes 10.4 → 11.7 ms** — a 12.5% rise, inside the ±25% the protocol registered. Capacity tracked the cores the workers could reach; it was not bought with extra CPU per request. The gain grows with offered load exactly as a worker-bound ceiling predicts: ×1.00 at c=1, ×1.80 at c=4, ×2.48 at c=8, ×3.32 at c=32.
- **The c=1 column is the control, and it behaves.** Every class ties at c=1 (0.99–1.02×): one client can occupy one worker, so seven more buy nothing. That the entire difference between the tables appears only where there is concurrency to exploit is what rules out the worker count having changed anything else.
- **Q13 ties at every concurrency** (0.98–1.00×), as H1 allowed: the workload's one aggregate is PostgreSQL-bound, and it uses 7.99 cores at 455 ms of CPU per request in both phases. Workers cannot help a query whose cost is in the database.
- **One regression, reported as prominently as the gains: Q11 at c=1 falls from 13.9 to 4.7 rps (0.34×)**, the single cell in either table where phase A beats phase B. The resource data says what it is *not*: CPU per request is essentially unchanged (93.1 → 99.4 ms), while cores used **fall** from 1.29 to 0.47 — the server is waiting, not computing, so this is latency on a single wide-result request, not parallel overhead burning CPU. Two candidates remain: the raised parallel budget changing the plan's worker allocation for one large scan, and eight workers' resident memory (~1.28 GiB documented floor) leaving less room in the API's unchanged 2 GiB for a 10,000-row response. The protocol predicted nothing about c=1 — H1 is about c ≥ 8, where Q11 does gain (×1.62 at c=8, ×1.76 at c=32) — so this is a finding, not a failed hypothesis, and it is the natural next experiment.
- **H2 holds perfectly, and it is what makes the rest trustworthy.** DaCHS reproduces itself in **96 of 96 cells** and argus in **96 of 96 cells** — every single cell a tie by the pre-registered rule between the two phases, measured 20 hours apart. Host drift over the window is therefore below the tie rule's resolution everywhere, so every egernia delta between Table A and Table B is the worker count and nothing else. On the mix at c=32, CSV, both opponents are indistinguishable across phases: DaCHS 4.86 → 4.80 cores at 534 → 536 ms per request, argus 7.88 → 7.87 cores at 322 → 321 ms.
- **H4 holds**: zero shed load in either phase, at any concurrency, with 64 pooled connections for at most 32 clients.
- **argus's job store, stated precisely.** It is truncated when the stack comes up, before the gates — so each phase's grid actually begins on the few hundred UWS rows the agreement gate's 165 probes and the 45 s warm pass leave behind, not on an empty table. Both phases run identical gates and one warm pass each, so both begin from the same small history and H2 compares the server rather than its history. (The pre-registration for the three-server scaling run, where nine blocks would otherwise accumulate *different* histories, truncates again immediately before each measured block.)
- **Where argus still wins.** Two cells, both Q11 — the 10,000-row result, where a JVM streaming from a thread pool still leads. Phase A gave it eighteen.
- **Conditions.** 864 rungs interleaved A,B,C, 19.9 h (2026-09-12 02:58Z → 22:51Z), four concurrencies {1, 4, 8, 32}, 20 s warm-up and 60 s windows, six generator processes pinned to cores 24-29, an untimed 45 s warm pass per server. Resource telemetry covered every rung. The driver verified, before timing anything: 500,096 rows and `relkind = 'r'` on egernia, 500,096 on DaCHS, `caom2.obscore` on argus, every cpuset, every promised PostgreSQL setting via `SHOW`, `TAP_API_WORKERS=8` in the container environment *and* ten python processes (the uvicorn supervisor, eight workers and the multiprocessing resource tracker), and the absence of `TAP_QUERY_DATABASE_URL` in both query-serving containers. Host state in `pins/b-host.txt`; nothing else ran on the box.

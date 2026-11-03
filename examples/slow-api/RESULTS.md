# Application screens and evidence

Replacement screens ran on 2026-11-03 against committed source `b8401e1` with a
clean working tree. The [manifest](evidence.json) records exact commands, source
and protocol hashes, dataset identity, environment and raw-artifact checksums.
The matching source snapshot is included in the local archive. A hash alone is
not treated as a source snapshot.

The primary metric is server CPU milliseconds per successful request. Positive
percentages below mean lower CPU/request. The frozen rule requires a median
reduction above 8% and above the baseline relative range. Error budget is zero;
p95 and p99 regression budget is 25%; true peak RSS regression budget is 16 MiB.
These provisional fixture budgets were unchanged before replacement measurements.
Paired reduction is 100*(1-candidate_CPU/baseline_CPU). Baseline relative range
is 100*(maximum_CPU-minimum_CPU)/median_CPU.

| Screen | All paired CPU reductions (%) | Median (%) | Baseline relative range (%) | Worst p95/p99 regression (%) |
|---|---|---:|---:|---:|
| mode1 | +15.06, +1.83, +9.50 | +9.50 | 6.47 | +37.11 |
| mode2 | +8.31, +15.04, +8.71 | +8.71 | 6.59 | -8.81 |
| mode3-pressure | -11.87, -8.66, -10.27, -13.88, -12.36 | -11.87 | 7.76 | +17.68 |
| mode3-target | +32.70, +34.15, +28.92, +41.98, +25.98 | +32.70 | 14.04 | -18.04 |

Modes 1 and 2 used three alternating pairs. Mode 3 used five per regime. Each
trial used 0.5 seconds of warmup and two seconds of measurement, 12000 rows,
limit 1000, seed 17. Target policy: two workers, 40 req/s pacing ceiling.
Pressure policy: four unpaced workers. CPython 3.14.4 and SQLite 3.46.1 ran on
an i5-1235U Linux host. CPU quota and cgroup memory limits were unavailable.
Server and generator shared the host. This is a synthetic read-only loopback
fixture, not production, challenge scoring or an open-loop capacity guarantee.

All 32 trials and 3590 measured requests completed without recorded HTTP, timeout
or semantic failures. Raw samples, warmups, errors and resource observations
remain in the local archive. Percentiles were not averaged.

## Decisions

- Mode 1 removes one redundant serialization. Its CPU screen passes, but one
  tail comparison exceeds the 25% budget. Reject this screen. True peak RSS is
  also unavailable.
- Incremental Mode 2 builds a request-local membership set, including construction
  cost. It is compared with the original baseline because Mode 1 has no accepted
  winner. Its CPU screen passes; complete acceptance remains inconclusive.
- Mode 3 adds only the persistent ordering index to the original baseline. Its
  target CPU screen is promising. The pressure screen is rejected for higher
  CPU/request. Its tails remain within the provisional budget in these new runs.
  The index consumes extra storage and requires write maintenance. It does not
  receive credit for other candidates.
- The retained implementation is the original baseline. No original-to-final
  gain is accepted. No candidate passed every screening gate, so no five-minute
  hold or fifteen-minute finalist soak was warranted or run. All gain claims
  remain **UNVERIFIED**. Light, skew and size measurements were not repeated in
  this rejected Mode 3 experiment. Old measurements remain historical only.

The baseline still pays for sorting, duplicate encoding and linear membership.
Pressure contention needs profiling. Correctness, external-write freshness,
rollback and relevant storage faults remain covered by executable tests.
No contract or durability setting was weakened. Instruction tests and application
screens do not establish agent behavior. Model evaluations remain unrun.

## Historical limits and availability

Historical raw files were copied byte-for-byte before untracking. Checksums were
verified. Old ru_maxrss values can inherit the parent's high water and must not
support RSS conclusions. This does not automatically invalidate CPU or latency.
Several early Mode 1/2 app.py and bench.py versions exist only as hashes, not
source bytes. The archive's source audit identifies the missing snapshots;
those runs cannot be fully reconstructed. Replacement runs repair this gap.

The portable archive and per-file manifest are local and unpublished. Their
checksums identify evidence only for readers who possess the archive. The public
source tree does not provide independent access to those raw trials. No download
URL or release asset exists. Untracking files does not erase earlier Git commits.

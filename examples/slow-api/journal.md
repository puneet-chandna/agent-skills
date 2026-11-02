# Project technique journal

Educational, synthetic, loopback application experiments. These are not agent
behavior evaluations. Entries use the existing technique-catalog.md template.
The primary metric and budgets were frozen in protocol.json before candidate
measurements. Raw source hashes identify dirty fixture drafts where a committed
revision alone would be insufficient. All trial values are listed below.

## Measurement correction

The initial `baseline-check.json` and `mode1-screen.json` ended the paced elapsed
denominator at the last response instead of the full admission window. This
slightly inflated reported req/s. They remain intact as superseded runs; they
do not establish throughput gains. `mode1-screen-v2.json` and later artifacts
use `max(configured_duration, actual_elapsed_including_drain)`. CPU/request and
raw latencies in the original files remain observations, not acceptance evidence.
The first longer Mode 1 pair briefly overlapped fast test execution on this
shared host. No trial was removed. Host activity/quota isolation is a limitation.

## 2026-11-02 / duplicate serialization / T02

Mode / production-or-challenge / boundaries: Mode 1; educational local context;
unchanged architecture, algorithm, query and data representation.

Hypothesis and measured bottleneck: `profile-baseline.json` records 200 encodes
for 100 requests, 0.140 seconds in encode out of 0.564 total profiled seconds.
One encoding only exists to calculate the response byte length. Preserve the
body and compute length from the one byte string.

Baseline / candidate / artifacts: baseline.py -> tune.py; source hashes and
commands in [raw results](results/). Profile measurements are diagnostic and
not substitutes for end-to-end paired measurements.

Workload/environment: 12,000 seeded rows, limit 1000, 256 selected entries with
duplicates, Unicode titles and tied scores; two workers, 40 req/s closed-loop
pacing ceiling; loopback HTTP/1.1. New DB/process per trial; 0.5 second warmup
and 2 second screen, then 1 second warmup and 10 second comparisons. Environment
is recorded in every artifact; unavailable cgroup limits are unknown.

Expected work removed: one O(output bytes) JSON encode; same asymptotic complexity.

Correctness/oracle: independent golden/differential outputs, limits/errors,
ties/duplicates/Unicode, concurrent reads and external commit/rollback checks.

Paired CPU reductions in corrected screen: 1.14%, 8.48%, 18.00%; longer pairs:
4.57%, 6.84%, 9.90%. Longer median 6.84% fails the frozen 8% minimum and is below
the observed baseline relative range. No errors were observed in these runs.
Full trial tails/resources remain in raw artifacts and the report below.

Result: **inconclusive; performance gain UNVERIFIED**, no accepted Mode 1 gain. No expensive
finalist hold was warranted. Keep the original baseline for the next mode.
Mode 2 opportunity: repeated membership is algorithmic and is outside this pass.
Rollback: select baseline.py. Revisit with better environmental control or a
representative workload where serialization is a larger measured share.

## 2026-11-02 / membership structure / T06

Mode / context / boundaries: Mode 2, local educational context; schema, database,
transport, query and architecture unchanged. Predecessor is baseline.py because
Tune was inconclusive. optimize.py only converts selected to a request-local
set, then calls the original renderer. It retains duplicate serialization.

Hypothesis/bottleneck: baseline payload building consumed 0.097 profiled seconds
per 100 requests. Expected O(K*M) membership becomes expected O(K+M) including
set construction, using O(M) extra memory. No cache/invalidation responsibility
is added. K=1000 returned rows; M=256 selected entries including duplicates.

Workload/environment/correctness: same as Mode 1, same seed/checksum, with all
oracle, ordering, duplicates, Unicode, error, transaction and concurrency checks.
Source identities and actual commands are in mode2-screen.json and
mode2-confirm.json. profile-optimize-v2.json identifies the measured candidate.
Earlier profile-optimize.json was a draft layered on Tune, before Tune's
selection decision; it is retained as a superseded diagnostic, not this pass.

All short paired CPU reductions: +7.79%, +5.34%, -0.72%; longer pairs: -2.88%,
+11.38%, +1.39%. Longer median +1.39%, baseline relative range 5.64%. No errors
were observed. Tails and resources are listed for every trial below.

Result: **inconclusive; performance gain UNVERIFIED**. The candidate misses the
frozen minimum effect and variation gate. It is not retained; a five-minute
finalist hold was not warranted and was not run. No accepted incremental Mode 2
gain exists. Rollback/next predecessor is the original baseline. Revisit when
representative membership cardinalities, profiles or environmental control change.

## 2026-11-02 / persistent ordering index / T02, Mode 3 boundary

Mode / context: Mode 3 local storage-layout experiment, not a transport rewrite.
The [brief](mode3-brief.md) was written before implementation. Both earlier
candidates were inconclusive, so rebuild.py calls baseline.render unchanged and
adds only the persistent ordering index. Earlier gains are not attributed here.

Bottleneck/alternatives/work removed: original profile reads cost 0.326/0.564
seconds per 100 requests. SQLite scans and builds a temporary ordering B-tree.
The candidate uses feed_order instead, preserving SQLite-owned transactions,
ordering and external-write maintenance. Cross-request caching and a transport
rewrite were rejected for the reasons in the brief. No mode requires a rewrite.

Correctness/integration/fault checks: independent golden/differential checks,
including indexed reads at 0, 16, 12000 and 100000 rows with score skew; JSON
semantics and length; concurrent HTTP reads; external commit/read-after-write
and rollback; DB-unavailable JSON followed by recovery. Setup is idempotent;
writer-lock failure occurs before serving; a real SQLITE_FULL from a constrained
page budget leaves no partial index; integrity_check and subsequent setup/read
succeed. Drop-index rollback twice is safe and restores the original plan and
outputs. Processes start and stop across every benchmark trial. These are
functional recovery checks, not a measured recovery-time SLO.

Five pairs per screen, with full values below:

- Light, one worker/5 req/s ceiling: median CPU reduction 30.68%; baseline relative
  range 16.32%. This is a screening observation, not an accepted gain.
- Target, two workers/40 req/s ceiling: median reduction 30.94%; baseline relative
  range 13.19%. All trials completed about 40 req/s with zero errors.
- Unpaced four-worker pressure: CPU/request increased in all five pairs, median
  12.00%; baseline relative range 12.46%. Worst p95/p99 regression exceeds the
  provisional 25% budget. Throughput also fell in each pair. Magnitudes remain
  workload/host observations, not a universal index regression.
- Tiny, 16 rows at target policy: median reduction -1.58%; no supported benefit.
- Large/skew, 100000 tied-score rows: median reduction 63.28%; baseline relative
  range 4.99%. This does not override the failed pressure screen.

Resource tradeoffs: the index adds 151552 database bytes at 12000 rows and
1249280 at 100000 rows. Setup time, process peak RSS and per-trial tails are
recorded in every Mode 3 raw artifact. SQLite must maintain the persistent index
on external writes; correctness was tested, write-maintenance performance was
not quantified. No durability setting was relaxed. Final diagnostic profiles
record journal_mode=delete and synchronous=2; defaults and plans are in the
profile JSON. Mode 1/2 do not change database size or persistent representation.

Additional one-pair concurrency probes are diagnostics only. Baseline/candidate
req/s were 131.12/225.29 at one worker, 202.38/157.94 at two, and 60.89/62.43 at
eight. These reveal sensitivity/overload rather than a confirmed capacity limit.
The four-worker regime is an unpaced pressure point past the observed peak,
not a five-minute capacity confirmation. Generator CPU stayed below the runner's
0.8-core warning threshold. CPU quota and cgroup memory limits remain unknown;
generator and server share the host. The cause of contention needs more profiling.

Result: **candidate rejected after screening; claimed gain UNVERIFIED**. It
fails the all-regime selection gate. No finalist was selected, so five-minute
holds and the fifteen-minute finalist soak were not run. Do not advertise the
light/target/large reductions as validated application speedups. Cold setup is
recorded but no long-term lifecycle or capacity claim is established. Low-level
transport fault suites and power-loss tests were not run: the transport and sync
contract did not change, and no power-loss guarantee is claimed.

Decision/rollback: retain baseline.py and regenerate its disposable database.
The tested alternative is rebuild.rollback(path), then restart with baseline.
Revisit only with new profiling and a new separately frozen experiment. Adjusting
concurrency while adding the index would combine mechanisms and is not credited
in this experiment.

## Original to final and remaining limit

The final retained implementation is the original baseline. There is no accepted
Mode 1, incremental Mode 2, Mode 3 or original-to-final speedup. The separate
baseline-check control showed ordinary run variation and has the superseded
throughput denominator; it is not an improvement. No gains are summed or counted
twice. All four source modules remain available for review and future experiments.

The retained baseline still spends most profiled application time reading and
sorting; duplicate encoding and membership remain candidates, without supported
end-to-end acceptance. The rejected index profile shifts work toward encoding
and membership. Pressure-regime costs need separate profiling. These findings
apply only to this synthetic read-only workload and host.

Application trials, instruction/packaging tests and agent evaluations are separate:
25 fast tests passed at this stage; final output is in the hardening report.
Agent A/B/C evaluations are prepared but **not run**; behavioral improvement
remains **unmeasured**. No installed skill was changed by these project experiments.

## Complete application trial ledger
Each trial is reported separately. CPU is process ms/success; RSS is lifetime peak MiB.
Latencies are successful-response nearest-rank p50/p95/p99 in ms. A/C/S means
attempted/completed/successful; U is unfinished at deadline (all drain to zero).
Percentiles below are never averaged. Positive paired effects mean reduced CPU/request.

### baseline-check.json
Command and provenance: [baseline-check.json](results/baseline-check.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 1.0s; warmup 0.5s.
- Pair 1 baseline: A/C/S 40/40/40; 40.74 req/s; CPU 6.805; p50/p95/p99 6.594/9.445/9.563; errors 0.0000; timeouts 0; U 0; RSS 35.84.
- Pair 1 baseline: A/C/S 40/40/40; 40.73 req/s; CPU 6.710; p50/p95/p99 6.488/9.887/10.369; errors 0.0000; timeouts 0; U 0; RSS 37.16.
Paired CPU reductions: +1.39%; median +1.39%; range +1.39% to +1.39%; baseline relative range 0.00%; worst p95/p99 regression +8.43%; largest paired RSS increase +1.32 MiB.

### mode1-confirm.json
Command and provenance: [mode1-confirm.json](results/mode1-confirm.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 10.0s; warmup 1.0s.
- Pair 1 baseline: A/C/S 400/400/400; 40.00 req/s; CPU 7.418; p50/p95/p99 6.888/10.413/12.937; errors 0.0000; timeouts 0; U 0; RSS 35.67.
- Pair 1 tune: A/C/S 400/400/400; 40.00 req/s; CPU 7.079; p50/p95/p99 6.924/9.637/11.211; errors 0.0000; timeouts 0; U 0; RSS 37.64.
- Pair 2 tune: A/C/S 400/400/400; 40.00 req/s; CPU 6.628; p50/p95/p99 6.199/9.109/10.857; errors 0.0000; timeouts 0; U 0; RSS 37.77.
- Pair 2 baseline: A/C/S 400/400/400; 40.00 req/s; CPU 7.115; p50/p95/p99 6.745/9.880/11.310; errors 0.0000; timeouts 0; U 0; RSS 37.96.
- Pair 3 baseline: A/C/S 400/400/400; 40.00 req/s; CPU 6.621; p50/p95/p99 6.467/9.449/10.532; errors 0.0000; timeouts 0; U 0; RSS 38.14.
- Pair 3 tune: A/C/S 400/400/400; 40.00 req/s; CPU 5.965; p50/p95/p99 5.787/8.510/9.049; errors 0.0000; timeouts 0; U 0; RSS 38.25.
Paired CPU reductions: +4.57%, +6.84%, +9.90%; median +6.84%; range +4.57% to +9.90%; baseline relative range 11.21%; worst p95/p99 regression -4.01%; largest paired RSS increase +1.97 MiB.

### mode1-screen-v2.json
Command and provenance: [mode1-screen-v2.json](results/mode1-screen-v2.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 7.393; p50/p95/p99 7.145/9.525/9.974; errors 0.0000; timeouts 0; U 0; RSS 35.68.
- Pair 1 tune: A/C/S 80/80/80; 40.00 req/s; CPU 7.309; p50/p95/p99 8.181/9.419/10.367; errors 0.0000; timeouts 0; U 0; RSS 37.17.
- Pair 2 tune: A/C/S 80/80/80; 40.00 req/s; CPU 6.378; p50/p95/p99 6.037/8.450/9.970; errors 0.0000; timeouts 0; U 0; RSS 37.21.
- Pair 2 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 6.969; p50/p95/p99 6.571/10.022/11.680; errors 0.0000; timeouts 0; U 0; RSS 37.27.
- Pair 3 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 7.233; p50/p95/p99 6.658/9.862/12.785; errors 0.0000; timeouts 0; U 0; RSS 37.32.
- Pair 3 tune: A/C/S 80/80/80; 40.00 req/s; CPU 5.931; p50/p95/p99 5.759/8.463/8.729; errors 0.0000; timeouts 0; U 0; RSS 37.34.
Paired CPU reductions: +1.14%, +8.48%, +18.00%; median +8.48%; range +1.14% to +18.00%; baseline relative range 5.87%; worst p95/p99 regression +3.94%; largest paired RSS increase +1.48 MiB.

### mode1-screen.json
Command and provenance: [mode1-screen.json](results/mode1-screen.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 80/80/80; 40.36 req/s; CPU 6.637; p50/p95/p99 6.440/9.350/10.792; errors 0.0000; timeouts 0; U 0; RSS 35.80.
- Pair 1 tune: A/C/S 80/80/80; 40.37 req/s; CPU 6.281; p50/p95/p99 5.948/8.762/13.462; errors 0.0000; timeouts 0; U 0; RSS 37.02.
- Pair 2 tune: A/C/S 80/80/80; 40.38 req/s; CPU 6.519; p50/p95/p99 6.094/8.704/9.462; errors 0.0000; timeouts 0; U 0; RSS 37.15.
- Pair 2 baseline: A/C/S 80/80/80; 40.33 req/s; CPU 7.610; p50/p95/p99 7.451/10.136/10.538; errors 0.0000; timeouts 0; U 0; RSS 37.28.
- Pair 3 baseline: A/C/S 80/80/80; 40.29 req/s; CPU 7.087; p50/p95/p99 6.759/9.735/10.826; errors 0.0000; timeouts 0; U 0; RSS 37.34.
- Pair 3 tune: A/C/S 80/80/80; 40.35 req/s; CPU 7.140; p50/p95/p99 7.123/9.644/10.934; errors 0.0000; timeouts 0; U 0; RSS 37.38.
Paired CPU reductions: +5.35%, +14.33%, -0.75%; median +5.35%; range -0.75% to +14.33%; baseline relative range 13.73%; worst p95/p99 regression +24.74%; largest paired RSS increase +1.23 MiB.

### mode2-confirm.json
Command and provenance: [mode2-confirm.json](results/mode2-confirm.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 10.0s; warmup 1.0s.
- Pair 1 baseline: A/C/S 400/400/400; 40.00 req/s; CPU 7.445; p50/p95/p99 6.720/10.613/12.696; errors 0.0000; timeouts 0; U 0; RSS 35.65.
- Pair 1 optimize: A/C/S 400/400/400; 40.00 req/s; CPU 7.659; p50/p95/p99 8.192/10.301/13.226; errors 0.0000; timeouts 0; U 0; RSS 37.09.
- Pair 2 optimize: A/C/S 400/400/400; 40.00 req/s; CPU 6.639; p50/p95/p99 6.206/9.070/10.133; errors 0.0000; timeouts 0; U 0; RSS 37.12.
- Pair 2 baseline: A/C/S 400/400/400; 40.00 req/s; CPU 7.492; p50/p95/p99 7.144/9.991/11.076; errors 0.0000; timeouts 0; U 0; RSS 37.34.
- Pair 3 baseline: A/C/S 400/400/400; 40.00 req/s; CPU 7.073; p50/p95/p99 6.722/9.837/10.415; errors 0.0000; timeouts 0; U 0; RSS 37.40.
- Pair 3 optimize: A/C/S 400/400/400; 40.00 req/s; CPU 6.975; p50/p95/p99 6.809/9.846/11.950; errors 0.0000; timeouts 0; U 0; RSS 37.48.
Paired CPU reductions: -2.88%, +11.38%, +1.39%; median +1.39%; range -2.88% to +11.38%; baseline relative range 5.64%; worst p95/p99 regression +14.74%; largest paired RSS increase +1.45 MiB.

### mode2-screen.json
Command and provenance: [mode2-screen.json](results/mode2-screen.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 6.563; p50/p95/p99 6.468/8.239/9.815; errors 0.0000; timeouts 0; U 0; RSS 35.72.
- Pair 1 optimize: A/C/S 80/80/80; 40.00 req/s; CPU 6.051; p50/p95/p99 5.834/8.122/10.047; errors 0.0000; timeouts 0; U 0; RSS 37.41.
- Pair 2 optimize: A/C/S 80/80/80; 40.00 req/s; CPU 6.774; p50/p95/p99 6.982/8.665/9.695; errors 0.0000; timeouts 0; U 0; RSS 37.43.
- Pair 2 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 7.156; p50/p95/p99 6.613/9.446/10.856; errors 0.0000; timeouts 0; U 0; RSS 37.50.
- Pair 3 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 6.657; p50/p95/p99 6.470/8.330/10.656; errors 0.0000; timeouts 0; U 0; RSS 37.55.
- Pair 3 optimize: A/C/S 80/80/80; 40.00 req/s; CPU 6.705; p50/p95/p99 6.521/8.635/9.602; errors 0.0000; timeouts 0; U 0; RSS 37.58.
Paired CPU reductions: +7.79%, +5.34%, -0.72%; median +5.34%; range -0.72% to +7.79%; baseline relative range 8.91%; worst p95/p99 regression +3.66%; largest paired RSS increase +1.69 MiB.

### mode3-large-skew.json
Command and provenance: [mode3-large-skew.json](results/mode3-large-skew.json). Rows 100000; limit 1000; concurrency 2; pacing ceiling 40; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 10.931; p50/p95/p99 10.230/15.306/15.591; errors 0.0000; timeouts 0; U 0; RSS 97.70.
- Pair 1 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 5.020; p50/p95/p99 5.212/7.447/11.128; errors 0.0000; timeouts 0; U 0; RSS 99.28.
- Pair 2 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 4.205; p50/p95/p99 4.456/5.735/6.630; errors 0.0000; timeouts 0; U 0; RSS 99.28.
- Pair 2 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 10.743; p50/p95/p99 10.096/14.805/16.466; errors 0.0000; timeouts 0; U 0; RSS 99.28.
- Pair 3 baseline: A/C/S 80/80/80; 39.99 req/s; CPU 10.718; p50/p95/p99 10.404/14.450/15.676; errors 0.0000; timeouts 0; U 0; RSS 99.55.
- Pair 3 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 3.910; p50/p95/p99 3.788/5.309/6.598; errors 0.0000; timeouts 0; U 0; RSS 99.55.
- Pair 4 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 3.817; p50/p95/p99 3.643/5.333/6.747; errors 0.0000; timeouts 0; U 0; RSS 99.55.
- Pair 4 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 10.395; p50/p95/p99 10.079/13.001/18.985; errors 0.0000; timeouts 0; U 0; RSS 99.55.
- Pair 5 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 10.901; p50/p95/p99 10.207/15.088/16.818; errors 0.0000; timeouts 0; U 0; RSS 99.55.
- Pair 5 rebuild: A/C/S 80/80/80; 39.99 req/s; CPU 3.938; p50/p95/p99 3.755/5.311/7.276; errors 0.0000; timeouts 0; U 0; RSS 99.55.
Paired CPU reductions: +54.08%, +60.86%, +63.52%, +63.28%, +63.88%; median +63.28%; range +54.08% to +63.88%; baseline relative range 4.99%; worst p95/p99 regression -28.63%; largest paired RSS increase +1.58 MiB.

### mode3-light.json
Command and provenance: [mode3-light.json](results/mode3-light.json). Rows 12000; limit 1000; concurrency 1; pacing ceiling 5.0; duration 4.0s; warmup 0.5s.
- Pair 1 baseline: A/C/S 20/20/20; 5.00 req/s; CPU 8.657; p50/p95/p99 8.008/10.264/11.268; errors 0.0000; timeouts 0; U 0; RSS 36.07.
- Pair 1 rebuild: A/C/S 20/20/20; 5.00 req/s; CPU 5.992; p50/p95/p99 5.184/6.563/7.256; errors 0.0000; timeouts 0; U 0; RSS 37.51.
- Pair 2 rebuild: A/C/S 20/20/20; 5.00 req/s; CPU 6.471; p50/p95/p99 6.368/7.147/7.165; errors 0.0000; timeouts 0; U 0; RSS 37.66.
- Pair 2 baseline: A/C/S 20/20/20; 5.00 req/s; CPU 8.472; p50/p95/p99 7.086/11.090/11.379; errors 0.0000; timeouts 0; U 0; RSS 37.76.
- Pair 3 baseline: A/C/S 20/20/20; 5.00 req/s; CPU 8.329; p50/p95/p99 6.545/10.584/11.625; errors 0.0000; timeouts 0; U 0; RSS 37.80.
- Pair 3 rebuild: A/C/S 20/20/20; 5.00 req/s; CPU 5.691; p50/p95/p99 4.772/6.816/7.415; errors 0.0000; timeouts 0; U 0; RSS 37.84.
- Pair 4 rebuild: A/C/S 20/20/20; 5.00 req/s; CPU 6.540; p50/p95/p99 5.807/7.081/7.105; errors 0.0000; timeouts 0; U 0; RSS 37.86.
- Pair 4 baseline: A/C/S 20/20/20; 5.00 req/s; CPU 7.657; p50/p95/p99 6.332/8.347/10.394; errors 0.0000; timeouts 0; U 0; RSS 37.88.
- Pair 5 baseline: A/C/S 20/20/20; 5.00 req/s; CPU 9.039; p50/p95/p99 8.982/10.427/10.908; errors 0.0000; timeouts 0; U 0; RSS 37.89.
- Pair 5 rebuild: A/C/S 20/20/20; 5.00 req/s; CPU 6.266; p50/p95/p99 4.929/7.443/8.617; errors 0.0000; timeouts 0; U 0; RSS 37.91.
Paired CPU reductions: +30.78%, +23.62%, +31.67%, +14.59%, +30.68%; median +30.68%; range +14.59% to +31.67%; baseline relative range 16.32%; worst p95/p99 regression -15.17%; largest paired RSS increase +1.44 MiB.

### mode3-near.json
Command and provenance: [mode3-near.json](results/mode3-near.json). Rows 12000; limit 1000; concurrency 4; pacing ceiling 0.0; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 232/232/232; 114.89 req/s; CPU 20.103; p50/p95/p99 32.782/53.921/55.667; errors 0.0000; timeouts 0; U 4; RSS 35.74.
- Pair 1 rebuild: A/C/S 195/195/195; 96.47 req/s; CPU 22.515; p50/p95/p99 37.308/62.720/69.977; errors 0.0000; timeouts 0; U 4; RSS 39.28.
- Pair 2 rebuild: A/C/S 195/195/195; 95.94 req/s; CPU 22.610; p50/p95/p99 40.551/62.507/68.855; errors 0.0000; timeouts 0; U 4; RSS 39.38.
- Pair 2 baseline: A/C/S 231/231/231; 114.47 req/s; CPU 20.135; p50/p95/p99 29.709/58.413/68.176; errors 0.0000; timeouts 0; U 4; RSS 39.46.
- Pair 3 baseline: A/C/S 211/211/211; 104.22 req/s; CPU 22.208; p50/p95/p99 35.560/62.998/70.311; errors 0.0000; timeouts 0; U 4; RSS 39.52.
- Pair 3 rebuild: A/C/S 180/180/180; 88.64 req/s; CPU 24.717; p50/p95/p99 43.271/65.892/71.823; errors 0.0000; timeouts 0; U 4; RSS 39.58.
- Pair 4 rebuild: A/C/S 166/166/166; 82.22 req/s; CPU 26.421; p50/p95/p99 48.734/70.844/75.703; errors 0.0000; timeouts 0; U 4; RSS 39.64.
- Pair 4 baseline: A/C/S 205/205/205; 100.82 req/s; CPU 22.775; p50/p95/p99 35.628/64.269/73.915; errors 0.0000; timeouts 0; U 4; RSS 39.70.
- Pair 5 baseline: A/C/S 218/218/218; 107.60 req/s; CPU 21.441; p50/p95/p99 33.440/60.502/68.978; errors 0.0000; timeouts 0; U 4; RSS 39.73.
- Pair 5 rebuild: A/C/S 188/188/188; 92.81 req/s; CPU 23.657; p50/p95/p99 38.990/69.023/77.743; errors 0.0000; timeouts 0; U 4; RSS 39.73.
Paired CPU reductions: -12.00%, -12.29%, -11.30%, -16.01%, -10.33%; median -12.00%; range -16.01% to -10.33%; baseline relative range 12.46%; worst p95/p99 regression +25.71%; largest paired RSS increase +3.54 MiB.

### mode3-pressure-c1.json
Command and provenance: [mode3-pressure-c1.json](results/mode3-pressure-c1.json). Rows 12000; limit 1000; concurrency 1; pacing ceiling 0.0; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 263/263/263; 131.12 req/s; CPU 7.369; p50/p95/p99 7.067/10.354/14.813; errors 0.0000; timeouts 0; U 1; RSS 35.73.
- Pair 1 rebuild: A/C/S 451/451/451; 225.29 req/s; CPU 4.217; p50/p95/p99 4.234/5.813/7.040; errors 0.0000; timeouts 0; U 1; RSS 37.40.
Paired CPU reductions: +42.78%; median +42.78%; range +42.78% to +42.78%; baseline relative range 0.00%; worst p95/p99 regression -43.86%; largest paired RSS increase +1.67 MiB.

### mode3-pressure-c2.json
Command and provenance: [mode3-pressure-c2.json](results/mode3-pressure-c2.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 0.0; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 406/406/406; 202.38 req/s; CPU 8.614; p50/p95/p99 9.682/12.981/14.530; errors 0.0000; timeouts 0; U 2; RSS 35.96.
- Pair 1 rebuild: A/C/S 317/317/317; 157.94 req/s; CPU 8.623; p50/p95/p99 12.359/17.286/20.756; errors 0.0000; timeouts 0; U 2; RSS 38.15.
Paired CPU reductions: -0.10%; median -0.10%; range -0.10% to -0.10%; baseline relative range 0.00%; worst p95/p99 regression +42.85%; largest paired RSS increase +2.20 MiB.

### mode3-pressure-c8.json
Command and provenance: [mode3-pressure-c8.json](results/mode3-pressure-c8.json). Rows 12000; limit 1000; concurrency 8; pacing ceiling 0.0; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 127/127/127; 60.89 req/s; CPU 49.869; p50/p95/p99 132.312/153.366/156.620; errors 0.0000; timeouts 0; U 8; RSS 41.71.
- Pair 1 rebuild: A/C/S 129/129/129; 62.43 req/s; CPU 45.764; p50/p95/p99 128.778/145.266/154.264; errors 0.0000; timeouts 0; U 8; RSS 40.87.
Paired CPU reductions: +8.23%; median +8.23%; range +8.23% to +8.23%; baseline relative range 0.00%; worst p95/p99 regression -1.50%; largest paired RSS increase -0.84 MiB.

### mode3-target.json
Command and provenance: [mode3-target.json](results/mode3-target.json). Rows 12000; limit 1000; concurrency 2; pacing ceiling 40; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 7.283; p50/p95/p99 6.774/9.980/10.652; errors 0.0000; timeouts 0; U 0; RSS 36.14.
- Pair 1 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 4.690; p50/p95/p99 4.368/6.991/8.016; errors 0.0000; timeouts 0; U 0; RSS 37.93.
- Pair 2 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 4.808; p50/p95/p99 4.378/6.858/7.932; errors 0.0000; timeouts 0; U 0; RSS 38.02.
- Pair 2 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 6.944; p50/p95/p99 6.606/9.718/11.645; errors 0.0000; timeouts 0; U 0; RSS 38.07.
- Pair 3 baseline: A/C/S 80/80/80; 39.99 req/s; CPU 7.054; p50/p95/p99 6.668/9.615/9.969; errors 0.0000; timeouts 0; U 0; RSS 38.20.
- Pair 3 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 5.447; p50/p95/p99 6.313/6.853/8.199; errors 0.0000; timeouts 0; U 0; RSS 38.23.
- Pair 4 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 4.994; p50/p95/p99 4.909/6.838/7.335; errors 0.0000; timeouts 0; U 0; RSS 38.39.
- Pair 4 baseline: A/C/S 80/80/80; 39.99 req/s; CPU 7.230; p50/p95/p99 6.852/9.781/11.256; errors 0.0000; timeouts 0; U 0; RSS 38.43.
- Pair 5 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 7.897; p50/p95/p99 8.005/9.990/12.101; errors 0.0000; timeouts 0; U 0; RSS 38.43.
- Pair 5 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 4.378; p50/p95/p99 4.278/6.857/7.411; errors 0.0000; timeouts 0; U 0; RSS 38.49.
Paired CPU reductions: +35.61%, +30.75%, +22.79%, +30.94%, +44.57%; median +30.94%; range +22.79% to +44.57%; baseline relative range 13.19%; worst p95/p99 regression -17.76%; largest paired RSS increase +1.79 MiB.

### mode3-tiny.json
Command and provenance: [mode3-tiny.json](results/mode3-tiny.json). Rows 16; limit 1000; concurrency 2; pacing ceiling 40; duration 2s; warmup 0.5s.
- Pair 1 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 0.690; p50/p95/p99 0.881/1.005/1.301; errors 0.0000; timeouts 0; U 0; RSS 28.29.
- Pair 1 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 0.701; p50/p95/p99 0.879/1.083/1.314; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 2 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 0.677; p50/p95/p99 0.873/1.119/1.404; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 2 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 0.700; p50/p95/p99 0.880/1.094/1.370; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 3 baseline: A/C/S 80/80/80; 39.99 req/s; CPU 0.708; p50/p95/p99 0.899/1.087/1.447; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 3 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 0.753; p50/p95/p99 0.904/1.126/1.198; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 4 rebuild: A/C/S 80/80/80; 40.00 req/s; CPU 0.746; p50/p95/p99 0.909/1.153/1.349; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 4 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 0.715; p50/p95/p99 0.896/1.050/1.444; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 5 baseline: A/C/S 80/80/80; 40.00 req/s; CPU 0.754; p50/p95/p99 0.900/1.168/1.593; errors 0.0000; timeouts 0; U 0; RSS 28.91.
- Pair 5 rebuild: A/C/S 80/80/80; 39.99 req/s; CPU 0.731; p50/p95/p99 0.895/1.225/1.492; errors 0.0000; timeouts 0; U 0; RSS 28.91.
Paired CPU reductions: -1.58%, +3.30%, -6.45%, -4.28%, +2.96%; median -1.58%; range -6.45% to +3.30%; baseline relative range 9.05%; worst p95/p99 regression +9.81%; largest paired RSS increase +0.62 MiB.

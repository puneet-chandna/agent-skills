# Measurement and acceptance

## Reproducible comparison

Record revision/dirty diff, dependency/build versions and flags, dataset checksum/schema/pragmas, CPU model/quota/architecture, cgroup memory/swap, kernel/fd limits, workers, TLS/proxy, tool/version, generator hosts/IPs, workload/mix, concurrency/arrival model, warmup/ramp/hold/drain, seed reset, UTC time and raw artifacts. Exclude credentials. Use a complete consistent DB snapshot or SQLite backup API, not a live .db copy without its WAL.

Follow modes.md: use at least three balanced/interleaved baseline/candidate pairs in Tune/Optimize and five in Rebuild, at identical offered load; add its sustained/fault/soak checks for the changed layer. Keep failures and report paired median/range; do not average percentiles or choose only the best. Investigate noisy-neighbor/CPU-steal variation. Verify realistic data/skew and per-route outcomes, especially rare writes.

## Challenge protocol snapshot

Researched 2026-10-31 UTC (2026-11-01 India); main 4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0:

- Current board: Synteq Xeon Platinum 8260, 1 vCPU, 1,967 MB RAM, no swap, Ubuntu 24.04/kernel 6.8, separate same-datacenter generators. Original DigitalOcean scores are not directly comparable; reruns finished Oct 27.
- Root install, unprivileged source build/runtime, LimitNOFILE=65535, bind capability for direct port 80, fresh seed per probe, 42-check suite. Fixed schema; no cross-request data/JWT caches or host tuning/affinity. Prepared plans, SQLite page cache/mmap, committed group writes allowed.
- User loop: feed; think 3–7s; one feed post; think 3–8s; 15% chance of like; 2% chance of post; idle 5–15s. Probabilities are per loop, not percentages of all requests. VUs are not req/s.
- Original README describes 1k warmup and search to 250-user resolution. Current leaderboard describes 2-minute doubling/bisection to ~5%, then 5-minute confirmation stepping down 5%. Preserve which protocol a result uses.
- README names k6; current scorer describes the bench/load.js user model and notes also mention mload. Verify actual driver/version/aggregation for the scored run; don't silently equate custom replay with unchanged k6.
- Transport gates: p95 <500ms, p99 <1000ms, errors <1%. A short probe is not a five-minute pass. Separate hold-only from whole-run ramp/hold/drain statistics.
- Older SPEC connection-scale examples (~15k) are not the current hundreds-of-thousands frontier.

Example from challenge root, with a prepared disposable server and a separate generator:

```bash
bash test/run.sh submissions/YOUR_SUBMISSION
# That script stops its own server. Start a fresh disposable server separately.
k6 run -e BASE_URL=http://YOUR_TEST_SERVER -e VUS=1000 -e DURATION=2m \
  --summary-trend-stats='avg,med,p(95),p(99),max' \
  --summary-export=warmup.json bench/load.js
k6 run -e BASE_URL=http://YOUR_TEST_SERVER -e VUS=YOUR_FIXED_LOAD -e DURATION=5m \
  --summary-trend-stats='avg,med,p(95),p(99),max' \
  --summary-export=candidate.json bench/load.js
python3 /PATH/TO/SKILL/scripts/check_k6_summary.py candidate.json
```

Warmup then hold is a fixed-load confirmation, not a maximum-capacity search. Reset seed consistently between comparisons. Outside challenge mode use the project's harness/SLOs. Label ARM/loopback/affinity/custom-driver results as a different environment from official scoring.

## Helper limits

check_k6_summary.py accepts legacy metrics and metrics nested under values. It requires duration p95/p99 in milliseconds, http_req_failed as a fraction and a positive http_reqs count. It reports tagged duration/failure metrics and checks when present. Default gates match the challenge; customize:

```bash
python3 /PATH/TO/SKILL/scripts/check_k6_summary.py run.json \
  --p95-ms 200 --p99-ms 500 --max-error-rate 0.001
```

Exit 0 means transport gates pass; 1 means a gate fails; 2 means invalid/missing data. Missing p99 is unverified, never inferred. This does not establish duration, correct load, API semantics, resource compliance, source revision, durability or official score. Add explicit per-endpoint thresholds/checks in the harness and verify committed writes separately.

## Required acceptance by changed behavior

- API: fresh counts, order/ties, sparse rows, auth-first errors, Unicode/control escapes, required JWT expiry and exact contract.
- DB: duplicate races, commit/busy/disk errors, rollback, no early success, restart/read-after-write; distinguish process crash from power loss.
- Transport: fragmented input, partial sends, mixed pipelining/order, half-close, cancellation, slow clients, recycled slots and exhaustion.
- Sustained load: stable memory after load drop, bounded WAL/progress, checkpoint/GC p99 spikes, no masked OOM/restarts, per-route failure rates.
- Generator: CPU/memory/ports/NIC and dropped iterations; low app CPU plus rising connect failures may be an infrastructure ceiling.
- Build: clean install/build as correct users inside resource budget.

Report remaining bottleneck and rollback. Do not extrapolate local/hot-route/allocation measurements into product-wide gains.

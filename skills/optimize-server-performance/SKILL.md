---
name: optimize-server-performance
description: Improve backend, HTTP server, database, and networking performance through profiling, controlled experiments, and correctness checks. Use for slow APIs, high p95/p99, low throughput, excessive CPU/memory, SQLite/WAL contention, many connections, algorithm/data-structure bottlenecks, or $12 Server Challenge submissions. Select Mode 1 Tune for small fixes, Mode 2 Optimize for application algorithms/data structures, or Mode 3 Rebuild for architectural experiments with strict verification. Default to Mode 1.
---

# Optimize Server Performance

Deliver measured improvements. Preserve required behavior, security, durability and operations. Another implementation's score supplies hypotheses, not a promised multiplier.

## Select the change budget

Accept `mode 1`/`Tune`, `mode 2`/`Optimize`, and `mode 3`/`Rebuild`, case-insensitively. Default to 1. An explicit all-out architectural request selects 3; a bare “make it faster” does not. State the mode/boundaries once, then execute authorized work without reconfirming routine edits.

| Mode | Allowed changes | Boundary |
|---|---|---|
| **1 — Tune** | Small bottleneck fixes, redundant work/copy removal, reuse, existing query/pool/worker/buffer tuning | Keep algorithms, data representation, feature architecture and stack |
| **2 — Optimize** | Tune + application algorithms/data structures, eliminate brute force, layout/pipeline refactors, supported-API batching/concurrency | Keep language, DB engine/schema/indexes, framework, library feature architecture, transport/runtime/kernel and native dependencies |
| **3 — Rebuild** | All layers available: feature/library rebuilds, dependencies/frameworks, native/SIMD, io_uring/kernel-facing code, storage/schema/DB engine, language/runtime | Preserve required contracts; pass strict validation |

Read [modes.md](references/modes.md) for precise boundaries/examples and the validation ladder. A mode is a ceiling, not a rewrite quota. Never auto-escalate, including in subtasks. Complete useful in-budget work and identify higher-mode experiments when needed. Narrower user constraints prevail. Mode 3 authorizes reversible local architectural experiments, not destructive migrations, live deployment or machine-wide kernel changes.

Keep **production/challenge context** separate from the numbered mode. Production uses product requirements/SLOs. Even Mode 3 must obey contest rules when entering the contest.

## 1. Inspect the actual project

Read applicable AGENTS.md, git status, manifests, hot paths, deployment, tests and existing performance records. Never mistake a downloaded reference repo for the target. If the target is missing, prepare analysis and request its path/URL without claiming improvements.

Record bottleneck candidates, traffic/access patterns, data sizes/skew, concurrency, hardware/resource budget and required semantics. Preserve auth/tenant isolation, input validation, parameterization, ordering/idempotency, transaction isolation, acknowledged-write durability, TLS/proxy responsibilities and observability. Do not make less-correct work look faster.

## 2. Load only relevant references

- Start with the selected [mode](references/modes.md), relevant [playbook section](references/optimization-playbook.md), and [measurement protocol](references/measurement.md).
- Consult matching [technique entries](references/technique-catalog.md) to choose experiments. Open [case studies](references/case-studies.md) for relevant Lean/Rust/assembly/other rationale, outcomes, pros/cons and rejected attempts.
- Use [challenge research](references/challenge-research.md) for rules/freshness/latest PRs. Query [submission catalog](references/submission-catalog.json) for specific entries; don't load all 157 rows by default.

For “latest”/contest work, refresh upstream rules, SPEC/schema/tests/load script, leaderboard, PRs by creation **and update**, and relevant rulings. Record retrieval time/main SHA, PR head, scored revision and status. Inspect relevant source. Separate official scores, local experiments, unscored revisions and projections; label a stale snapshot when refresh is unavailable.

## 3. Establish the baseline and limiting resource

Run relevant correctness checks and smoke load on disposable local/staging data. Match release build, dataset, protocol/TLS/proxy, load model, CPU/RAM and connection reuse. Keep generator CPU outside the server quota; don't stress a public endpoint merely because its URL appears in config.

Measure per-route throughput/latency/errors and committed outcomes, CPU/request, allocations, queues/fds/connections, cgroup memory and relevant DB/WAL/lock/I/O counters. Profile actual CPU, off-CPU waits, query plans/counts or event-loop lag. Distinguish RSS from kernel/socket/page-cache memory and app limits from generator CPU/ports/NIC/dropped work.

## 4. Run controlled, in-budget experiments

Rank at most five hypotheses by evidence, impact, effort and risk. Change one mechanism at a time; preserve a baseline and rollback. In Modes 2/3 compare algorithm complexity, data access/locality, construction/update/invalidation cost, memory and crossover sizes. A hash map, lock-free design or better Big-O is not automatically faster.

Use the playbook/catalog to select the smallest justified intervention. Existing resource reuse may fit 1; new application structures/batching fit 2; custom HTTP/crypto, DB internals/plugins, new native/SIMD, io_uring/runtime/kernel, toolchain/PGO or stack replacement require 3. In Mode 3 pursue a profiled architectural bottleneck directly; don't require a cosmetic tuning phase first.

Map techniques to the project: an HTTP client needs pooling/streaming/cancellation/TLS work, not a transplanted SQLite server. PostgreSQL/MySQL need their own tools, not SQLite pragmas. Retain general oracles/fallbacks for specialized plans and test preconditions instead of assuming seed properties. Contest WAL/NORMAL does not guarantee every commit survives power loss; preserve the production durability contract.

## 5. Prove the result

Follow modes.md: at least three matched interleaved pairs in 1/2, five in 3; relevant size/skew regimes, sustained holds/soak and fault tests according to the changed layer. Screen quickly first; apply expensive validation to finalists. Stateless Mode 1/2 microbenchmarks need adequate repeated samples, not artificial server holds.

Use differential/property tests for changed algorithms; commit/rollback/race/restart tests for writes; fragmentation, partial sends, pipeline order, cancellation, ownership/stale completion and exhaustion tests for transports. Preserve API/security checks. Record unrun tests; tooling cannot prove an absence of bugs.

Report all trials, paired effects/variation, per-route writes/errors and resource/tail tradeoffs. Never average percentiles, cherry-pick, equate VUs with req/s, or extrapolate local ratios into official capacity. Search/confirm capacity separately from same-load improvements. An aggregate error allowance must not hide a failing rare endpoint.

`scripts/check_k6_summary.py SUMMARY.json` checks common k6 summary formats against transport gates only; missing data is UNVERIFIED. It does not validate semantics, duration, resources or official capacity. Use product thresholds and the full measurement protocol.

Revert losers; retain the smallest supported winner and reproducible commands/artifacts. Append meaningful wins, rejections and inconclusive results to the project technique journal using the catalog template; read it on future runs. Never claim universal success or silently mutate the installed skill during a project run.

## Deliver

State mode/context, bottleneck/evidence, changed files/reason, matched baseline/candidate results and noise, checks/unrun checks, tradeoffs, remaining limit and rollback. When measurements are incomplete, label performance UNVERIFIED instead of lowering the acceptance bar. Creating a skill alone does not improve a repo.

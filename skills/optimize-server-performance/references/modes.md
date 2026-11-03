# Change budgets and validation

Read this before planning edits. The selected mode limits how far changes may go; validation strength also follows the actual changed behavior. No mode promises a speedup.

## Selecting a mode

- Accept numbers and names: Mode 1/Tune; Mode 2/Optimize; Mode 3/Rebuild. Use 1 when unspecified. A bare number only selects a mode when clearly attached to this skill, not when it could be a count/metric.
- Treat an explicit “go all out, architectural/language changes allowed” as 3. If wording names a mode and gives narrower constraints, obey those constraints. Keep mode selection visible in the brief and final report.
- Execute authorized local changes within the budget without repeatedly asking for approval. A candidate idea outside the budget becomes a concrete recommendation, not an excuse to stop all useful work or an automatic escalation. Ask about moving modes only when necessary to continue beyond the budget.
- Keep a production/challenge context independently. Production defaults to product contracts/SLOs; contest runs must follow their current rules even in Mode 3. Architecture freedom never permits fabricated results, disabled auth, lost acknowledged writes or omitted failing trials.

## Mode 1 — Tune

Goal: remove measured waste with a small, easy-to-review patch while preserving the design.

Allow localized removal of redundant queries/conversions/copies/log work, reuse of existing statements/connections/objects, existing pool/worker/buffer configuration, prepared-query parameterization, query shape improvements using current indexes and supported runtime settings that preserve semantics. Bound buffer retention and fix existing resource leaks. Small source changes are fine; a low line count alone does not qualify a risky change.

Keep feature architecture, algorithms/data representation, public contract, dependencies/toolchain, runtime/transport, schema/indexes and DB engine intact. Do not hide a new global cache, writer queue or event loop inside “tuning.” Preserve freshness and cache/authorization isolation. If the bottleneck requires a different algorithm, report it as a Mode 2 candidate while completing measurable in-budget improvements.

Example: reuse an existing prepared lookup and remove a duplicate serialization. Replacing all-pairs matching with a new index belongs in Mode 2, even if it is a short patch.

## Mode 2 — Optimize

Goal: optimize how the application computes and organizes data without rebuilding its infrastructure.

Inherit Mode 1's semantic, freshness, ownership and security requirements, but
replace its algorithm/data-representation ceiling with this section's budget.

Allow Mode 1 plus algorithms, data structures, internal application modules, contiguous/hot-cold layouts, bounded work queues, supported-API batching and application-level concurrency. Compare complexity, constants, working-set size, skew, mutation/read ratio and invalidation cost. Choose a structure for the workload, not for theoretical elegance.

Examples: repeated linear membership to a request-local set; all-pairs join to a hash or sort/merge join; full sort to bounded top-k; FIFO array shifts to a deque; overlapping interval scans to an appropriate sorted/indexed representation. A new application representation may require construction/memory/invalidation work that belongs in the benchmark. Keep output ordering, duplicates, ties, Unicode, adversarial input and error behavior.

Keep language, database engine/schema/indexes, framework, transport/runtime/kernel implementation, native dependencies and core library feature architecture unchanged. Use supported public APIs of existing dependencies; no dependency source forks, custom protocol/crypto, database internals, new native/FFI backends, io_uring or toolchain changes. If the target itself is a library, optimizing a contained existing algorithm is allowed; replacing a feature's architecture or I/O backend belongs to Mode 3. A DB migration or new persistent index is Mode 3 under this budget, even if normally routine elsewhere.

Add application caches only in production context where freshness/invalidation rules permit them, with bounded memory, tenant-safe keys and equivalence tests. Challenge context forbids cross-request data/JWT-result caches. Request-local reuse is not permission to return stale cross-request data.

Example: improve candidate deduplication with an order-preserving hash set and benchmark total build+lookup time. Reimplementing a network library's send path or replacing PostgreSQL with SQLite is Mode 3.

## Mode 3 — Rebuild

Goal: maximize performance under the real resource budget and product contract, with every architectural layer available for experiments.

Inherit Modes 1/2's correctness and evidence requirements, not their architectural
ceilings. Read those requirements as well as this section and the validation ladder.

Allow application/library feature rebuilds, framework/dependency replacement or forks, new native/FFI/SIMD paths, language/runtime changes, io_uring/kernel-facing implementation, database engine/schema/index redesign and deployment architecture alternatives. The mode authorizes reversible implementation and experiments in isolated branches/worktrees; do not reconfirm routine architectural edits already inside this scope. It does not authorize destructive data migration, changes to a live kernel or production deployment merely to obtain a benchmark.

Start from profiling and the actual highest-impact hypothesis; a rewrite is optional. Keep a functioning baseline, a slow correct reference/oracle, testable toggles where useful, a feature-equivalent candidate and rollback. Preserve security, API semantics, durability, compatibility/platform requirements and operational responsibilities unless the user explicitly changes them. Replace responsibilities when replacing a component; a removed proxy's TLS/auth/limits cannot disappear.

Write a compact architecture experiment brief before implementing: bottleneck; alternatives; expected removed work; changed boundaries; retained contracts; target metric/resource/SLO; test matrix; benchmark protocol; rollback. Perform it without a new permission gate for reversible authorized work. When replacing storage, compare complete product behavior, not an in-memory or less-durable substitute.

## Validation ladder

Freeze the primary metric, acceptable minimum effect and regression/resource budgets **before** running a candidate. Use the product's SLOs; when none exist, label a proposed provisional budget instead of inventing business requirements. Require semantic correctness regardless of the measured speed. Treat improvements smaller than observed variation as inconclusive; do not demand that every noisy pair be positive or select only favorable pairs.

| Requirement | Tune | Optimize | Rebuild |
|---|---|---|---|
| Release baseline and matching environment/workload | Required | Required | Required |
| Correctness | Existing relevant checks + targeted regressions | Tune + differential/property tests for changed algorithms | Optimize + whole-feature/integration and changed-layer fault tests |
| Interleaved baseline/candidate pairs for a claimed gain | At least 3 | At least 3; cover representative sizes/skew | At least 5; repeat for representative workload regimes |
| Realistic mixed traffic | Required if it serves mixed traffic | Required; include construction/update/invalidation cost | Required, including cold/warm and light/target/near-saturation regimes |
| Sustained confirmation | Long enough for changed behavior/cycles | At least a 5-minute target-load hold per version for a serving-path change | At least a 5-minute target-load hold per version, plus finalist soak |
| Scaling | Relevant operating sizes | Tiny/typical/large, skew and churn | Same + capacity/resource ceilings and overload/recovery |
| Rollback and source/result provenance | Required | Required | Required; include migration/compatibility path if relevant |

Use short screening runs to reject candidates first. Apply the full expensive ladder to finalists, not every leaf edit. A serving-path Mode 3 finalist soak lasts at least 15 minutes and long enough to cover several relevant GC/checkpoint/compaction/expiry cycles; increase duration if the cycles demand it. For a stateless Mode 1/2 function or CLI algorithm, use sufficiently long repeated samples across representative sizes/skew; do not impose a server five-minute hold. Require sustained operation streams when the changed library/CLI behavior has long-lived state, resource retention or a runtime/transport backend, especially in Mode 3; use the corresponding hold/soak durations and verify output equivalence. Do not force HTTP thresholds onto a library benchmark.

Fault tests follow the changed layer: algorithm edge cases/overflow/duplicate order; cache invalidation; SQL concurrency and failed commits; transport fragmentation/half-close/partial sends/pipeline ordering/stale completions/resource exhaustion; storage restart/rollback/integrity/durability as required. Use fuzzing, sanitizers, race tooling or property tests when supported and relevant to the changed code. Stronger tooling is evidence, not a proof of no bugs. State unsupported/unrun checks.

For capacity claims, separately search the load limit and confirm it with a full five-minute hold at that load with fixed SLO/error/resource gates. Keep same-load latency/efficiency comparisons distinct from capacity changes. Include all failed probes, per-route failures, committed writes, generator health, dropped work, kernel/cgroup memory and sustained stability. Do not just copy the challenge's permissive aggregate <1% error budget into production.

When time, hardware or tools prevent the ladder, complete useful implementation and executable checks, then label performance **UNVERIFIED** with exactly which evidence is missing. Do not claim an accepted speedup, silently lower the bar or automatically launch long jobs after the session ends.

## Usage examples

`Use $optimize-server-performance mode 1 on this repo.`

`Use $optimize-server-performance mode 2. Optimize hot algorithms and data structures; keep the stack and infrastructure.`

`Use $optimize-server-performance mode 3. Rebuild any necessary layer and verify every claimed improvement with the strict benchmark protocol.`

Produce: selected mode/context; actual bottleneck; compared alternatives; smallest retained change; semantic checks; matched-load results and noise; resource/tail tradeoffs; remaining limit; rollback; local technique-journal entry.

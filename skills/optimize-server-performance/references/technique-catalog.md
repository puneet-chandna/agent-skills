# Technique catalog and evidence journal

Checked 2026-11-01. Contents: evidence policy; common patterns; algorithm/data-layout choices; less-obvious techniques; local journal; primary sources.

## Read evidence before applying a technique

No technique has always improved every system. Use these evidence labels:

- **Repeated challenge pattern:** appears in several studied successful entries; often bundled with other changes. This is observational evidence, not an isolated causal estimate or a guarantee for this repo.
- **Documented mechanism:** official documentation establishes behavior/complexity, not a measured gain for this workload.
- **Author experiment:** a submission reports a local before/after result; retain hardware, revision, methodology and caveats. Do not turn it into an independent reproduction.
- **Local verified / local rejected / inconclusive / untested:** reserve these labels for the target repo's own measurements under the modes.md acceptance ladder.

Each entry below has a minimum change mode, mechanism, applicability, failure case and validation. Scope depends on implementation: changing a supported setting differs from replacing an implementation. Respect contest restrictions separately. Avoid “unheard of” claims; the less-obvious entries are established techniques that are easy to overlook.

## Repeatedly useful patterns

### T01 — Reuse setup, still perform current work (Mode 1)

**Evidence:** repeated challenge pattern (#82, #153, #230, #233); SQLite preparation API [S1]. Reuse prepared statements, existing connections and immutable key setup instead of repeating initialization. Query current data and verify each token. Test parameter rebinding, expiry/key rotation and connection ownership; pools can cost more than they save at low volume. Measure prepares, query/handshake counts and CPU/request, not only the number of allocations.

### T02 — Remove redundant work and narrow what is fetched (Mode 1; new computation plan 2)

**Evidence:** repeated challenge pattern; planner mechanisms [S2,S3]. Eliminate duplicate validation/conversion/scans where semantics permit, fetch only needed fields, limit before expensive enrichment, and use existing indexed order. Construction of a tiny projection can still dominate tiny inputs; changed JOIN/LIMIT placement can change results. Compare query count/rows visited and full endpoint output, including ordering and missing rows. New schema/indexes require Mode 3 and may be forbidden by the contest.

### T03 — Batch across an expensive boundary (Mode 2; replacement transport 3)

**Evidence:** repeated challenge pattern (#82, #153, #224, #230). Amortize driver/FFI/syscall or transaction setup with bounded batches. Good for repeated fixed overhead; bad when queue delay, cancellation, contention or head-of-line blocking dominates. Benchmark light and saturated traffic, batch residence time, per-route p99, commits and fairness. Preserve commit-before-success and each connection's response order. Never treat throughput alone as acceptance.

### T04 — Bound retained memory and allocate on demand (Mode 1; new ownership model 2/3)

**Evidence:** repeated challenge pattern; #224 lifecycle defects. Idle work should not retain peak-size buffers; cap pools/queues and construct partial-input buffers only when necessary. Pool contention and retained bursts can regress memory/CPU. Measure allocation rate and total cgroup memory across ramp, hold and load drop. For async I/O, no reused/freed/moved send buffer before its final completion.

### T05 — Eliminate the actual resource ceiling (Mode depends on the fix)

**Evidence:** official board fd/OOM/generator footnotes. A low-CPU server can be limited by fds, queues, sockets, DB locks, disk or the generator. Existing configuration/resource leak fixes can fit 1; new queueing design fits 2; transport/runtime replacement fits 3. Check refused/connect vs response errors, process exits, CPU steal, kernel memory and per-route writes. More concurrency may lower throughput.

## Algorithm and data-structure choices (Mode 2 minimum)

### T06 — Replace repeated linear search with an appropriate lookup structure

**Evidence:** documented collection behavior [S4]; workload hypothesis until measured. Repeated membership or joins may benefit from a hash set/map; ordered/range queries may fit a sorted vector or tree. Include building, hashing, equality, memory, invalidation and mutation cost. Keep first-seen order with a separate output sequence when required. Test duplicate policy and adversarial keys; do not disable collision-attack protection for untrusted input. For tiny collections, a linear scan may win.

### T07 — Compute top-k without sorting everything

**Evidence:** heap/selection APIs and complexities [S4,S5]. A bounded heap uses O(n log k) work; selection plus sorting just k elements can avoid a full O(n log n) sort. Test comparator consistency, ties, stable ordering, NaNs and n<k. If the API requires all results ordered, this is not equivalent. Benchmark tiny k, typical k, k≈n and total output preparation. In-place selection may be inappropriate when the input must remain unchanged.

### T08 — Choose a queue, dense array or bitset for its access pattern

**Evidence:** documented collection tradeoffs [S4]; workload hypothesis. A deque avoids repeated front shifting; dense bounded ids can support direct indexing/bitsets; sparse ids may need mapping. Include range/cardinality, memory initialization, resize and id reuse costs. Bitsets lose ordered payload information and can waste memory on sparse huge domains. Test bounds/overflow, reset and concurrency semantics. Do not assume challenge ids are always dense.

### T09 — Replace all-pairs work with a join/sweep or compact layout

**Evidence:** algorithmic mechanism; no repo-specific measurement yet. For repeated matching/interval operations compare hash join, sort/merge or sweep-based processing; for repeated field scans compare contiguous hot fields with pointer-heavy records. Account for sorting/index construction, updates, output size and the small-input crossover. Preserve equal-key behavior, interval boundaries, stable ids and reference lifetimes. Better asymptotics may lose on small inputs or mutation-heavy workloads; measure realistic skew.

## Less-obvious, potentially high-leverage techniques

### T10 — Inspect hash-map capacity, not just length (Mode 1 diagnostics; representation change 2)

**Evidence:** Rust's current HashMap iteration is O(capacity), visiting empty buckets [S6]. An oversized mostly-empty map repeatedly scanned can be expensive. Compare bounded capacity, shrinking outside the hot path, or a dense iteration representation. Shrinking/rehashing every request is likely harmful; growth bursts and stable-reference requirements matter. Measure capacity/len, iteration time, resize work and memory. This behavior is implementation-specific; verify the actual container/version.

### T11 — Look for automatic SQL reprepares (Mode 1)

**Evidence:** SQLITE_STMTSTATUS_REPREPARE records plan regeneration from schema/binding changes [S7]; Cider #234 reports a local binding-clear fix. A statement stored in a cache may still regenerate. Measure REPREPARE/RUN, VM steps, full scans and sorts before changing binding lifecycle. Always rebind every required parameter; never retain stale bindings just to lower a counter. Prepared-statement caching does not imply caching query results.

### T12 — Bind a batch as data, not generated SQL text (Mode 2 if already exposed; new native extension 3)

**Evidence:** SQLite carray binds a C array into a table-valued function [S8]. For large variable id batches, compare it with existing parameter binding rather than building many SQL shapes. Availability/compile flags and driver exposure vary; new native plumbing belongs to 3. Test input ownership/lifetime, duplicates, order, empty batches and query plans. Parameter count or parsing savings do not ensure better execution. Never replace safe binding with string concatenation.

### T13 — Separate search metadata from heavyweight payloads (Mode 2; dependency replacement 3)

**Evidence:** SwissTable uses compact metadata to filter candidates before equality checks [S9]; this documents a mechanism, not a blanket container win. For hot lookup/scan paths compare existing compact containers or a hot/cold application layout. Node/flat choices affect stable references and moves. Benchmark actual key/value sizes, hits/misses, mutations and load factor; memory overhead/rehash costs can reverse gains. Do not reimplement a hash table merely because it is sophisticated.

### T14 — Measure SQLite page cache vs mmap and checkpoint placement (1 for existing safe settings; new checkpoint architecture 3)

**Evidence:** successful entries disagree; #233/#224 author experiments favor mmap=0 for their WAL-heavy hot set while #82/#153 use mmap. Read hit/miss counters [S10], resident/cgroup memory, WAL size/progress and p99. A bigger cache per connection can exhaust memory. Moving checkpoint work off-loop needs a replacement policy, bounded WAL and durability/error testing. Never recommend disabling mmap or checkpoints universally.

### T15 — Guard a specialized fast path with an oracle and fallback (Mode 2; DB internals 3)

**Evidence:** repeated challenge pattern (#153, #224, #230, #233). Exploit checked workload invariants, retain a general correct path, and disable the shortcut on violation. Use differential tests on randomized/mutated data, external writes and boundary cases. Check cost and drift detection can exceed the saved work. Do not assume a theorem about an abstract plan proves the emitted machine code or I/O. Benchmark both fast and fallback paths and their switching overhead.

### T16 — Use io_uring as a completion design, not an epoll rename (Mode 3)

**Evidence:** liburing maintainer documentation describes submission/completion batching, multishot and provided buffers [S11]; challenge entries apply them. Merely swapping notification calls misses much of the mechanism. Verify kernel/seccomp support, slot limits, buffer ownership, partial sends, CQE flags/rearming, cancellation and exhaustion. Compare against the existing supported transport; SQPOLL may compete for the only CPU. No kernel-independent speedup is established.

### T17 — Train specialization, measure it, retain the simpler loser/winner record (Mode 3)

**Evidence:** challenge PGO entries and Cider's rejected AVX-512 experiment. Synthetic representative PGO, narrower SIMD or precomputed immutable dispatch/schema metadata may remove repeated work. Compare on target CPU with an unoptimized control; no benchmark detection or hard-coded data. Include cold/error paths and build cost; preserve hardening/security. Wider SIMD or native compilation can regress. Record rejected variants so later agents do not retry them without new evidence.

### T18 — Distinguish served latency from unoffered/dropped work (Mode 1 diagnostics)

**Evidence:** k6 documents dropped_iterations from configuration or inability to sustain arrivals [S12]. Low latency on completed requests can hide unsent work; closed-loop tests can also reduce request rate as latency rises. Record intended/actual arrival rate, completed throughput, dropped iterations, generator health and timeout/error accounting. Compare open-loop rate and realistic user-model workloads separately when appropriate, never silently change the scoring driver. A passing aggregate latency graph is insufficient.

## Project-owned technique journal

After a meaningful completed experiment, append to the repo's existing performance record, or create `docs/performance/technique-journal.md` when none exists. Do not log every trivial edit. Read relevant previous entries on future runs. Keep wins, regressions, rejected attempts and inconclusive results; this prevents repeated failed experiments and preserves local evidence.

Use this entry structure:

```text
Date / experiment / technique id:
Mode / production-or-challenge / boundaries:
Hypothesis and measured bottleneck:
Baseline revision / candidate revision / raw artifact paths:
Workload: sizes, skew, read/write mix, target load, cold/warm:
Environment: CPU, RAM, build/runtime, DB, transport, generator:
Expected work removed; time/space complexity before -> after:
Correctness/oracle/fault checks; unrun checks:
Paired trials: all values, median/range/variation; SLO/per-route errors:
CPU/request, peak memory, throughput and p95/p99 tradeoffs:
Result: local verified | local rejected | inconclusive | untested
Decision/rollback; conditions where result applies or fails:
Source/provenance and reason to revisit:
```

Promote an entry to a reusable lesson only with supported conditions and evidence, not because one metric improved once. “Repeated local win” means multiple complete comparable experiments in named environments, not a universal property. If asked to update this skill, incorporate well-supported lessons with sources/counterexamples; project runs must not silently alter the installed skill.

## Primary sources

Challenge references/experiment caveats are in challenge-research.md and the pinned submission catalog. Documentation establishes mechanisms rather than a measured gain in the target repo. Verify docs against deployed versions before implementation.

- S1: https://www.sqlite.org/cintro.html
- S2: https://www.sqlite.org/queryplanner.html
- S3: https://www.postgresql.org/docs/current/using-explain.html
- S4: https://doc.rust-lang.org/std/collections/index.html
- S5: https://doc.rust-lang.org/std/primitive.slice.html#method.select_nth_unstable
- S6: https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.iter
- S7: https://www.sqlite.org/c3ref/c_stmtstatus_counter.html
- S8: https://www.sqlite.org/carray.html
- S9: https://abseil.io/about/design/swisstables ; https://abseil.io/about/design/btree
- S10: https://www.sqlite.org/c3ref/c_dbstatus_options.html ; https://www.sqlite.org/wal.html
- S11: https://github.com/axboe/liburing/wiki/io_uring-and-networking-in-2023
- S12: https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/

# Optimization experiments

## Find the resource first

Decompose latency into queueing, CPU, DB/lock/I/O waits and network time using profiles/counters. Keep CPU time/request separate from elapsed latency and virtual users thinking between requests. Estimate whole-request benefit before optimizing a tiny leaf function.

## SQL and SQLite

1. Count statements/prepares per endpoint; run EXPLAIN QUERY PLAN on real distributions. Reuse prepared statements per owning connection; reset/rebind correctly. Avoid unnecessary clearing that causes reprepares, but never leak a previous binding. Measure reprepare/full-scan/sort counters where exposed.
2. Fetch limited ids via the ordering index before expensive joins/counts. Aggregate likes over a bounded range only while filtering back to the selected ids and restoring timestamp/id order. Fall back on broad spans. Test sparse ids, ties, reordered timestamps and absent join rows. Use a coherent snapshot where required.
3. A duplicate-like read can avoid a write, but uniqueness/conflict handling must still enforce correctness under racing requests. Determine first-time/repeated status from the actual committed outcome.
4. Measure writer serialization before increasing connection counts. A bounded owner/queue can reduce scheduling/locking on one CPU but needs deadlines/backpressure. Never use NOMUTEX/THREADSAFE=0 with concurrent SQLite entry; a checkpoint thread changes the analysis.
5. Bound group commit by count and time. Execute writes, release active statements as needed, COMMIT, then send success. Rollback replaces tentative successes with errors. Preserve per-connection order and prevent reads from exposing writes that later roll back. Contest batch semantics do not override production isolation/read-after-write contracts.
6. Measure WAL frames/bytes, checkpoint progress, oldest read transaction, commit time and write-gate latency. A PASSIVE worker on its own attached connection may move stalls off the loop. Background copying alone need not reset a continuously growing WAL. Add bounded reset/restart management; journal_size_limit alone does not bound an active WAL. Never disable autocheckpoints without a replacement.
7. Compare mmap=0 plus a modest page cache against mmap on this workload. Both appear in fast entries. Negative cache_size is KiB, cache budget is per connection, mmap length is not resident memory. Inspect misses and cgroup memory, leaving room for kernel sockets and OS.
8. Preserve sync/integrity settings. WAL/NORMAL can lose recent commits on power failure; FULL is stronger. SIGKILL/restart/integrity_check do not simulate OS/power loss. Do not disable constraints/foreign keys as a shortcut.

## CPU, auth and allocations

- Distinguish SQL VM, driver/FFI, framework middleware, JSON objects, UTF conversion, hashing, logging and syscalls in a profile; language names are not a diagnosis.
- Remove redundant copies/conversions; pool bounded buffers. Allocate partial-input/send storage on demand. Keep output stable until the final send completion; cap retained pool capacity after spikes.
- Preserve escaping, Unicode/length semantics, errors, key order, content length and validation order when specializing serialization. Use differential tests on adversarial inputs.
- Reuse immutable HMAC key setup, not authentication results in challenge mode. Verify signatures/allow-listed algorithm, required future exp, malformed claims, positive string ids and authorization. Prefer mature crypto; test tenant boundaries where applicable.
- Retain product observability requirements when changing logs/sampling.

## Connections and networking

- Budget process fds, listener/backlog, per-ring slots, source ports/IPs on generators, kernel socket memory, application state and in-flight buffers. Idle users still consume sockets.
- Test EMFILE/ENFILE/ENOBUFS, full queues, accept rearming and disconnects. Bound retries; do not busy-spin, exit, or mask restarts. Check process/cgroup logs to distinguish OOM, crash and refusal.
- A plateau near 71k can be 65,535 fds plus tolerated timeouts, not a CPU limit. Report failures by route and phase; do not optimize around an error allowance.
- Measure response coalescing/TCP_NODELAY; account for TLS and proxy upstream keep-alive. Removing Nginx can remove important product functions.
- Advanced Linux: multiple rings with direct descriptors, multishot accept/receive and provided buffers can reduce syscalls/idle memory. Tables still have kernel/RLIMIT constraints. Size/roll rings before exhaustion; test exact kernel/seccomp and keep a portable path.
- Under DEFER_TASKRUN, drain pending work and ensure waits wake. Preserve SQE/CQE ownership, recycling, send lifetime, generation counters, cancellation and response order. Test low traffic and bursts. Do not copy a kernel-specific workaround universally.
- SQPOLL consumes CPU. Bounded batching delays can reduce saturation cost while hurting low-load latency; compare both regimes.

## Specialized read plans and plugins

SQLite B-tree/cursor internals are not a stable public application API, even though the organizer allows them. Pin the version; retain SQLite's pager/WAL/locking/transactions; close cursors before their snapshot ends; keep SQL fallback.

Prefer traversing posts_created_at_id_idx to assuming rowid order. For an invariant-based plan, check all preconditions at startup and after every mutation, detect external writers/layout changes and disable the path on violation. Differentially test mutated/randomized data, overflow records and rollback. A theorem about a model does not prove emitted C, transport or record decoding.

Public PCACHE/VFS plugins still need tests for short writes, sync order, truncate, file lifecycle, checkpoint transitions, allocation failure and error propagation. Contest acceptance is not production validation. Confirm backup/migration/other-process requirements before exclusive ownership such as unix-excl. Never substitute a private SQLite file-format engine in challenge mode.

## Builds and runtime choices

- Tune the current framework's queries/pools/worker counts first. Compare proxy/direct only with equivalent responsibilities.
- Measure release flags, LTO, architecture targets and PGO independently. Train on disposable synthetic data covering success/errors; record provenance and retain a non-PGO control.
- Wider SIMD need not win: Cider measured/rejected AVX-512 in favor of SSE2. Keep bounds checks and portable fallback; test the target CPU.
- Test root install, unprivileged build and runtime on a clean resource-limited machine. A fast app that cannot build is unusable. Pin versions/checksums. Keep foreground execution; do not execute downloaded installers just to study them. Preserve production compiler hardening.

## Stack mapping

| Stack | Investigate first | Escalate only with evidence |
|---|---|---|
| FastAPI/Python | Blocking event-loop work, workers, DB lifecycle, queries, model/serializer cost | Native leaf functions or alternative server |
| Node/TS | Event-loop stalls, objects, prepared DB access, pools, serializer/logging | Native binding/transport or framework replacement |
| Go | Idle goroutine/stack cost, pools, cgo, GC, mutexes | Custom event loop/io_uring |
| Rust | Task/buffer ownership, blocking DB, copies, contention, tracing | Unsafe transport/parser/FFI |
| JVM/.NET | Per-connection state, GC, DB call overhead, thread pools | Native AOT/FFM/custom transport |
| HTTP client | Pooling, DNS/TLS, retries, streaming/cancellation, bounded queues | Platform I/O while retaining TLS/proxy/portability |

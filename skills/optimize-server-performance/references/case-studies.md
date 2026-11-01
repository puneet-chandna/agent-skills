# Comparative implementation studies

Snapshot: main `4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0`, rechecked 2026-11-01. Contents: measured outcomes; causal limits; Lean; Rust; assembly; other designs; negative experiments; source map.

Load only the cases relevant to the measured bottleneck. **Rust #82 is the highest-scoring Rust entry in this snapshot, not the overall leader**: Lean and Mojo tie above it. These are application/workload results, not a language ranking. Official score source is the pinned board; design source is the pinned source tree. A current README/local experiment can describe a revision different from the scored build.

## Official outcomes and tradeoffs

All rows below held for five minutes on the board's Synteq 1-vCPU/2GB environment. Errors were 0.00% except #207 at 0.61%. Read the board's generator/resource notes before comparison.

| Case | VUs / req/s | p95 / p99 ms | CPU µs/request / peak RAM MB | Main reusable lesson | Main cost or limitation |
|---|---|---|---|---|---|
| Lean #153 | 280k / 26,683 | 141 / 316 | 31 / 836 | Derived specialized plans + checked invariants + fallback | Toolchain/proof/FFI maintenance; model proof does not prove executable |
| Rust #82 | 264k / 25,147 | 259 / 499 | 30 / 630 | Compact ownership, bounded retries, prepared/range queries, I/O batching | Unsafe/kernel lifecycle; expanded generator setup needed |
| Assembly #206 | 250k / 24,053 | 141 / 397 | 34 / 1,486 | Accept-ramp budget + batching/direct descriptors | CPU-bound after fix; high maintenance/memory |
| Assembly #152 | 240k / 22,985 | 366 / 633 | 33 / 545 | Reduce reconnect churn and kernel crossings | Kernel-specific close/wake/buffer behavior; tail-limited |
| Assembly #86 | 171k / 16,777 | 87 / 142 | 43 / 358 | Controlled variants and extensive boundary/fault tests | Local newer 275k hold does not replace official 171k |
| Assembly #207 | 160k / 15,682 | 291 / 757 | 56 / 1,307 | Forked workers extend per-process fd capacity | 0.61% overall errors hide roughly 8% failures on each write route |
| C #230 | 270k / 25,873 | 87 / 251 | 29 / 1,006 | Efficient ordinary SQL + bounded loop + checkpoint placement | Checkpoint/write-gate complexity; CPU/tail near ceiling |
| C #233 | 270k / 25,889 | 14 / 43 | 25 / 790 | B-tree plans, batched author seeks, public VFS/PCACHE hooks | Refusals at higher load despite CPU headroom; specialized DB internals |
| Mojo #224 | 280k / 26,489 | 366 / 556 | 29 / 1,597 | Shared buffers, lazy rings, guarded plans, WAL management | Memory grew across revisions; lifecycle defects beyond functional suite |
| F# #201 | 247k / 23,884 | 14 / 72 | 27 / 750 | Custom transport/application boundary removes general overhead | Not stock Kestrel HTTP-path performance; transport portability burden |

Sources: [board](https://github.com/arjaythedev/twelve-dollar-server-challenge/blob/4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0/LEADERBOARD.md), scored PR comments and source map below. Absolute memory/CPU reflects the recorded configuration, not a complete causal comparison. Do not attribute a bundled change's whole gain to one trick.

## Lean #153: specialize only what can be checked

**Reasoning:** the workload is known, so derive routing, JSON and read plans from a compact specification instead of repeatedly paying general-purpose costs. Dense ids plus nondecreasing timestamps permit a reverse-rowid feed. SQLite B-tree cursors still use its pager/WAL/transactions, bypassing VDBE interpretation; writes remain SQL.

**Evidence:** scored `fd2c149` at 280k; author reports feed 16.7→5.4µs locally, not an independent end-to-end speedup. Startup/per-insert checks and external-writer detection select SQL fallback. The Lean model/plan theorems are checked; emitted C and runtime are tested, not fully proved. Higher probes failed through refusals; one run froze with host memory pressure outside the app cgroup.

**Pros/cons and transfer:** guarded specialization can remove real work with a reference oracle, but adds invariants, codegen/build and upgrade obligations. Test clock rollback, gaps/ties, external writes and fallback. Generic checked fast paths can fit Mode 2; B-tree/codegen core rebuilding fits 3. Do not recommend Lean or private DB calls merely because the entry leads.

## Rust #82: ownership and experiment discipline

**Reasoning:** stable send storage, generation-tagged slots, on-demand input, bounded ENOBUFS retries and batch completion handling reduce allocation/lifecycle overhead. Prepared queries and bounded range scans reduce pager/driver work without caching data. Serialized DB access/group commit amortize setup while preserving acknowledged-write ordering.

**Evidence:** 240k initially hit source-port/generator capacity; expanded target/source IPs and generators confirmed 264k. 293k/278k full holds failed p99; 360k/480k OOMed. Follow-up #141 scored 230k in its recorded standard setup; a local improvement did not become a higher official capacity result. #238's ~299k remains a projection in the snapshot.

**Pros/cons and transfer:** compact state and bounded queues are broadly testable; custom unsafe I/O, scheduling and SQLite ownership require edge/failure tests. Use query/copy fixes in 1, app structures/batching in 2, and custom transport/native internals in 3. The research's retained rejected variants are as useful as its selected winner; examples below.

## Assembly #206: fix admission throughput before optimizing instructions

**Reasoning:** bounded single-shot accepts avoid taking a socket when a direct-file table cannot hold it. Raising accepts in flight to 256 lets the server admit a fast ramp. Grouped completions/commits amortize work; cancellation by operation tag avoids scanning all pending I/O on each close.

**Evidence:** benchmark comment records `bf5cc2f` improving official held users from 125k on its old head to 250k; the formerly failing 160k ramp passed. At 260k it failed p99 at 96% CPU. The author measured cancellation CPU around 300→20µs on related C/Zig implementations, **not this assembly binary**. Keep that attribution.

**Pros/cons and transfer:** removing a connection-admission ceiling is valuable; writing assembly is not necessary to apply it. Same-author C #184 and assembly #206 both hold 250k at 34µs/request; assembly records higher RAM (1,486 vs 985MB) and p99 (397 vs 294ms). This is an observational contrast, not a controlled proof that assembly is slower or faster. Custom transport is Mode 3.

## Assembly #152: transport design, then kernel lifecycle

**Reasoning:** old epoll design shed sockets near the fd cap, forcing repeated connections. io_uring fixed-file rings retain keep-alives; batching combines submission/wait, provided buffers remove idle allocation, and bounded passes avoid delaying every response behind huge batches.

**Evidence:** official `ad7a72c` holds 240k vs its earlier #117's 155k. On the author's different Ryzen KVM setup, CPU/request fell 40–52→16–19µs and syscalls >3→0.9–1.1; those local numbers are not the official Xeon gain. 250k/260k official probes failed latency with zero errors.

**Pros/cons and transfer:** reducing reconnect churn beats shaving individual instructions, but the rewrite encountered delayed FIN without shutdown, buffer-registration differences, stale task flags, ENOBUFS and multi-second oversized passes. Do not copy race-prone kernel workarounds blindly. Test burst admission, low-load wakeups, partial sends, close/cancel and exhausted rings in Mode 3.

## Assembly #86: use negative results and independent oracles

**Reasoning:** retain switches for transaction scope, query/JSON strategy, receive mode, batching, literal copying and retry policy; test each against reference SQL and protocol invariants. Freeze a batch before opening its transaction instead of waiting for future traffic under a DB lock.

**Evidence:** official board 171k; newer local source documentation reports a 275k five-minute hold on Threadripper/loopback with different kernel and revisions. The README alone cannot rescore the official result. Its multishot receive screen raised saturation throughput but failed high-load p99; range-query and literal-copy experiments were also rejected/inconclusive. See original test artifacts before reproducing.

**Pros/cons and transfer:** differential fixtures, failed-COMMIT injection, sparse/reordered data, guard pages, canaries and ABI checks detect bugs outside 42 checks. C sanitizers do not automatically instrument hand-written assembly. Keep tiny controllable experiments and their provenance; don't keep every experimental variant in a production path indefinitely. Algorithm switches may fit 2; assembly/native I/O work fits 3.

## Contrasts worth keeping

- **Assembly #207:** cascading forked workers extend fd capacity without io_uring, but multiple SQLite writers add contention. The official 0.61% total errors were rolled-back POST batches (about 8% of each write route). Keep nonblocking lock retry bounded and verify committed outcomes; clearing the fd ceiling alone is insufficient.
- **C #230 vs #233:** both hold 270k; #230 uses prepared SQL/range scans, #233 uses B-tree/public plugins. The latter's 25 vs 29µs/request and 43 vs 251ms p99 do not prove a universal B-tree win: methods, memory and other mechanisms differ, and its next limit is refusals. Keep supported SQL until profiles justify Mode 3 internals.
- **Mojo #224:** official comments show 290k at `1f4eb0b`, 280k at `29024f3`, and current 280k at `ef45beb`. Final batch-forming wait did not raise the held-user ceiling; RAM rose 1,042→1,597MB between the latter two scored runs. Guarded state/compliance and lifecycle fixes matter even when throughput does not improve. Six reported parser/queue/arena/pipeline defects demonstrate why a functional pass is insufficient.
- **F# #201:** custom transport invokes handlers without the usual Kestrel HTTP layer; no per-connection pipes/send task in the hot path. Transfers to specialized backend boundaries, not claims about stock framework throughput. It scored lower than its earlier #142's 260k; retain revisions and tail/memory tradeoffs.
- **Cider #234:** author headline/local result is 250k; official row is 228k. B-tree reads and SSE2 helpers are not permission to advertise local capacity as an official score. AVX-512 lost to SSE2 in the author's measurement; wider vectors are not intrinsically better.

## Retained experiment outcomes: reasons to accept or reject

Rust RESEARCH.md uses WSL2/i9, one server logical CPU, 2GiB, separate generator logical CPUs, fresh seed, balanced trial order and pinned comparison builds. These are author-local comparisons. Record the workload and paired statistic, not just a rounded percentage.

| Experiment | Recorded outcome | Decision and transferable lesson |
|---|---|---|
| Rust checkpoint trigger 1,000→4,096 frames, normal-build 64-connection mixed | Six pairs: 75,526→82,182 median req/s; paired geometric gain +7.96%, 95% interval +6.04…+9.89%; CPU/request higher; median p99 22.42→27.65ms | Accepted with explicit throughput/tail/resource tradeoff; not “everything faster” |
| Rust fixed-archive 1,024-connection mixed confirmation | Six pairs: paired gain +14.46%, 95% interval +13.01…+15.70%; p99 37.02→43.53ms; cgroup peak 56.94→70.83MiB | Distinguish from normal-production build; roughly 14MiB extra memory and worse tail |
| Rust GROUP BY like-count rewrite | Four pairs: feed −16.36%, mixed −9.16% | Rejected: fewer FFI calls did not offset SQL aggregation cost |
| Rust process/thread checkpointer variants | Some create-throughput gains ~30–35%, but ~20%+ extra mixed CPU and weaker/uncertain mixed gain | Rejected/not selected: a write-only win need not improve the real mix |
| Rust remove App mutex via one issuer | Feed −8.13%, mixed −9.07% in screen | Rejected: removing a lock is not automatically an end-to-end improvement |
| Rust batch target 32→64 | Four longer pairs: feed loses all; mixed +6.47%, +0.58%, −0.72%, −1.17% | Rejected: larger batches are not a default improvement |
| Assembly #86 multishot receive | Better saturation CPU throughput; fails 275k p99 target | Rejected as default: throughput cannot override tail acceptance |
| Assembly #86 inline fixed literal copies | Two short saturation screens favor +3.3%/+2.3% per CPU-second; unchanged-k6 reverse-order screens do not repeat a gain | Remains opt-in/inconclusive; no capacity claim, no five-minute confirmation |
| Cider AVX-512 vs SSE2 | Author local ~27.06 vs 26.10µs CPU/request | AVX-512 rejected; target-specific instruction/cache/frequency effects matter |

Use these as hypotheses/anti-hypotheses, not universal bans. Revisit a rejected technique when the workload, bottleneck, implementation or hardware changes; explain why the old evidence no longer applies. The project technique journal records the new test.

## Source map and provenance

Every path below is relative to `submissions/` at the pinned main SHA. Treat files as design/local-measurement evidence unless an exact scored SHA is identified separately. Preserve MIT notices if copying code. No implementations are bundled in this skill.

| Case | Read for rationale/results | Inspect for the mechanism | Scored evidence |
|---|---|---|---|
| Lean | lean-derive-hargup/README.md | spec/Feed/{Invariant,Plan,Emit}.lean; runtime/{db,uring}.c | PR #153 benchmark comment `fd2c149` |
| Rust | rust-epoll-scooter1337/{README,RESEARCH,IO_URING,LUFP}.md | src/ and tests/ | PR #82 benchmark comment; board footnote for #141 |
| Assembly #206 | asm-iouring-unorig-username/README.md | server.asm: flush_batch, cancellation, accept credits | PR #206 comment `bf5cc2f` |
| Assembly #152 | asm-epoll-umitaltintas/README.md | src/{server.asm,uring.inc,json.inc} | PR #152 comment `ad7a72c` |
| Assembly #86 | asm-nasm-melroy89/{README,PERFORMANCE}.md; research/literal-copy-results.md | src/{uring,ranges,sql}.inc; tests/{faults,matrix,pressure}.py | PR #86 benchmark comment; local identities in PERFORMANCE.md |
| C #230/#233 | their README.md files | #230 src/; #233 src/{db,btree}.h | Board `b32c4ee` / #233 `3f5c305` |
| Mojo | mojo-iouring-oh-meh/README.md | src/{server,db}.mojo; src/shim.c | PR #224 benchmark comments: use current `ef45beb` |
| F#/Cider | fsharp-kestrel-delneg/README.md; cider-iouring-pomilon-v3/README.md | F# Uring.fs/Transport.fs; Cider src/{btree,fast}.c | Board #201 `a8bf27f`; PR #234/board |

Pinned source root: https://github.com/arjaythedev/twelve-dollar-server-challenge/tree/4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0/submissions

Scored comments: https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/153#issuecomment-6478291046 ; https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/82#issuecomment-6370978458 ; https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/206#issuecomment-6519607807 ; https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/152#issuecomment-6474563666 ; https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/86#issuecomment-6370979545 ; https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/224#issuecomment-6544744857

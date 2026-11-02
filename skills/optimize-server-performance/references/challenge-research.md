# $12 Server Challenge: evidence and transferable lessons

Snapshot checked 2026-10-31 UTC / 2026-11-01 India. Main: `4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0`. Newest PR returned by the creation-sorted API: **#241**, created 2026-10-31 21:10:20Z, head `c5fe04487d68e3eb7c07b6543f564984081e3d37`. This is a researched snapshot, not a promise that #241 remains newest.

Contents: scope; results; deep dives; latest PRs; rules; failure lessons; application; sources.

## Scope and evidence quality

Read current API/schema/load script/build-test harness, leaderboard and rule notes; catalog all its result/failure rows. Surveyed README patterns across 127 merged submission directories (132 README files, including nested docs); this is breadth coverage, not an independent code audit or benchmark of every entry. Deep-read selected architectures below, including source hot paths for Lean, C #233, Mojo, and open PRs #240/#241. Inspected PR metadata/bodies #222–#241 and pulled exact heads #238/#240/#241. Do not describe this as running those servers.

Use official results for capacity, author READMEs for claimed design/local measurements, and source for implementation. Read each result's notes: passing 42 checks does not establish every rule, concurrency edge case or production property. Some high-scoring rows have open auth/build questions. The web frontend may be cached or gated; the public repository supplies the board, per-entry notes and source. No subscription access is needed for this workflow.

## Current official frontier (same leaderboard environment)

| Submission | PR | Users held 5m | req/s | p95/p99 ms | CPU | Peak RAM MB | Score date UTC |
|---|---|---:|---:|---:|---:|---:|---|
| Lean generated C/io_uring | 153 | 280,000 | 26,683 | 141/316 | 92% | 836 | Oct 28 |
| Mojo/io_uring/B-tree reads | 224 | 280,000 | 26,489 | 366/556 | 85% | 1,597 | Oct 31 |
| Crystal/io_uring | 193 | 270,000 | 25,693 | 348/879 | 92% | 1,160 | Oct 29 |
| C/io_uring, SQL reads | 230 | 270,000 | 25,873 | 87/251 | 82% | 1,006 | Oct 31 |
| C/io_uring, B-tree/plugins | 233 | 270,000 | 25,889 | 14/43 | 72% | 790 | Oct 31 |
| Rust/io_uring | 82 | 264,000 | 25,147 | 259/499 | 84% | 630 | Oct 21 |
| F#/custom transport | 201 | 247,000 | 23,884 | 14/72 | 71% | 750 | Oct 30 |
| Cider v3/B-tree reads | 234 | 228,000 | 21,945 | 370/853 | 86% | 668 | Oct 31 |

Source: pinned LEADERBOARD.md; full catalog in submission-catalog.json. These VUs include think time; they are not requests per second. Low tail latency/CPU at the held load does not imply more users will pass the next hold. A newer or lower-level implementation may score worse.

The original video/first batch's 64k frontier is historical. Current board uses a Synteq VPS; original DigitalOcean results were rerun by Oct 27. README still describes the original machine/search in places: use the scored run's actual protocol. Some runs use extra generator/source IP capacity; compare notes, not scores alone.

## Selected implementation studies

Read case-studies.md only for relevant architectures: Lean, highest-scoring Rust #82, assembly #206/#152/#86, C #230/#233, Mojo, F# and Cider. It contains source anchors, official vs local outcomes, reasoning, costs, rejected experiments and transfer rules. Read technique-catalog.md for reusable patterns and the project evidence journal. Keep numeric score/protocol/freshness records here and in submission-catalog.json; avoid duplicating long case writeups.

## Newest open submissions, not official winners

| PR/head | Latest observed status | Techniques/claim | Evidence boundary |
|---|---|---|---|
| #241 `c5fe044` | Open; newest by creation | C, direct descriptors, provided buffers, B-tree, group commit, 64 MiB cache | Claims 42 checks and local WSL tests to 100k; no official score |
| #240 `d630d40` | Open | Builds on #230; order-index B-tree plans, paced passes, task-work draining | Author reports ~10% less CPU/request in paired Ryzen local comparison; not capacity |
| #239 `1ab4c84` | Open | Lean-proved plans plus C io_uring/PCACHE hook | Claims clean build/42 checks; no official score |
| #238 `897da1d` | Open | Rust native B-tree read plans | ~299k is an extrapolation; reported 100k 5m local hold is a different environment |
| #237 `7ce1623` | Open rollback request | Ada restores #216 after #229 | Old 270k does not automatically rescore the new head; board currently 232k at #229 |
| #236 `9ed9f2e` | Open | DexLang group commit, three rings, buffer reuse | Claimed local +15% throughput/lower idle RSS, unscored |
| #235 `1569472` | Open updated follow-up | HolyPHP io_uring and ring/retry/send fixes | Prior revision `7a3f61e` scored 135k; latest head not scored in this snapshot |

Source: creation-sorted GitHub PR API, exact heads, relevant PR READMEs/source. Never inherit a score from a parent or turn the #238 projection into a measured record. #241 README includes claims such as “100% ACID” and “zero SQL overhead”; treat these as author language, not established facts. Prepared SQL already avoids repeated parsing, and WAL/NORMAL is not power-loss durable for every commit.

## Current rule rulings with practical impact

Organizer statements on Oct 31, recorded in LEADERBOARD and #233 discussion:

- Allowed: SQLite's own B-tree/cursor read paths through its pager/WAL; documented plugin APIs such as VFS and PCACHE2; route/fast-path ordering by measured traffic if all requests still work.
- Not allowed: replacing SQLite with a private file-format engine (#210 off board despite a prior 280k), or patching SQLite source (#154/#158 removed pending unpatched rerun).
- Still required: actual per-request data reads, no JWT-result/response/query cache, unchanged schema, committed writes before responses, build from source, no host/kernel tuning. Page cache/mmap and statement-plan reuse are allowed.
- Contest allows WAL/NORMAL. SQLite documents possible loss of recent committed transactions after power failure/hard reboot; do not weaken production durability on the strength of contest terminology.

## Failure lessons that should change an optimization plan

- FD cap: many entries sit at ~71k with ~0.93% timeouts because 65,535 sockets plus queued requests use almost the whole error allowance. Some frameworks exit on EMFILE; #98 appears to spin on repeated accept failure.
- Memory: Go Gin #103 and Crystal Kemal #146 OOM at modest CPU; report kernel/cgroup memory as well as RSS.
- Rare-route failures: #209's <1% total errors hide about 12% like and 11% create failures; an aggregate passing score is not a production acceptance criterion.
- Build: #178 installed Cargo in root's home while deploy built without Cargo; compiler bootstrap OOM/timeouts affected V/Goose. Large CI runners do not establish 2GB reproducibility.
- Auth: a long list of entries passed 42 checks yet accepted missing exp. Keep auth tests outside just the official suite.
- Freshness: #229's short 270k probe passed while full holds failed; current Ada 232k and rollback PR #237 illustrate regressions and score/revision discipline.
- No universal memory setting: Lean/Rust use mmap, while Mojo/C #233 measured advantages with mmap=0 and a small page cache. Measure the actual hot set.

## Apply to the target repo

Default order: profile existing stack; remove repeated DB/driver work; reduce query scans/copies; right-size workers/buffers; test bounded commit batching; isolate measured checkpoint stalls; only then evaluate platform-specific transport/DB internals. Keep product SLO/security/durability and realistic workloads. A benchmark architecture supplies hypotheses, not a migration mandate or guaranteed multiplier.

## Primary sources and refresh entry points

### Refresh procedure (instruction clarification, not a new snapshot)

For latest/contest work, refresh upstream rules, SPEC/schema/tests/load script,
leaderboard and PRs sorted by both creation and update. Record retrieval time,
main SHA, PR head, scored revision and status; inspect relevant source. Separate
official scores, local experiments, unscored revisions and projections. If a
refresh is unavailable, label this snapshot stale. Do not overwrite historical
dates, scores or SHAs. Use the primary source entry points below.

- Repository/rules: https://github.com/arjaythedev/twelve-dollar-server-challenge
- Pinned board and per-entry notes: https://github.com/arjaythedev/twelve-dollar-server-challenge/blob/4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0/LEADERBOARD.md
- Pinned API: https://github.com/arjaythedev/twelve-dollar-server-challenge/blob/4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0/SPEC.md
- Pinned load script: https://github.com/arjaythedev/twelve-dollar-server-challenge/blob/4d60dd808b54bcc326d6eb1fbfa9f713bf4983c0/bench/load.js
- Latest-created PRs: https://api.github.com/repos/arjaythedev/twelve-dollar-server-challenge/pulls?state=all&sort=created&direction=desc&per_page=100
- Latest-updated PRs: https://api.github.com/repos/arjaythedev/twelve-dollar-server-challenge/pulls?state=all&sort=updated&direction=desc&per_page=100
- SQLite ruling: https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/233
- Newest reviewed: https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/241
- Latest SQL-to-B-tree experiment: https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/240
- Rust projection vs measurement: https://github.com/arjaythedev/twelve-dollar-server-challenge/pull/238
- Community ARM/wrk evidence (different protocol): https://github.com/arjaythedev/twelve-dollar-server-challenge/issues/7
- SQLite durability: https://www.sqlite.org/pragma.html#pragma_synchronous
- SQLite checkpoint/concurrency: https://www.sqlite.org/wal.html

For immutable submission source, replace main with the snapshot SHA in a blob/tree URL; for open PRs use head_sha from the catalog and the head repository. Preserve MIT notices when copying upstream code. This skill summarizes techniques and facts; it does not bundle upstream server implementations.

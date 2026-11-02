# Mode 3 experiment brief

Written before implementing the architecture candidate. Educational local
fixture, not production or a challenge reproduction. Both earlier modes were
inconclusive, so the predecessor is the original baseline. The candidate keeps
both linear membership and duplicate encoding; no earlier gain is counted.

## Evidence and alternatives

`profile-optimize-v2.json` records 0.487 seconds for 100 requests, with 0.324
seconds in reads and 0.271 seconds in SQLite execute calls. The query plan scans
items and uses a temporary B-tree for `ORDER BY score DESC, id ASC LIMIT ?`.
The original baseline profile also spends 0.326 seconds in reads. This is a
measured remaining storage-layout limitation. Duplicate encoding
remains because Mode 1 was inconclusive; it must not be credited to Mode 3.

Investigate one persistent composite index on `(score DESC, id ASC)`. Under
this skill, changing persistent indexes is Mode 3. It can avoid scanning and
sorting all N rows for the top K, using an ordered B-tree seek/scan instead.
Measure SQLite's actual plan and complete request cost, not just asymptotics.
Index creation, storage, maintenance and rollback become explicit responsibilities.

Reject cross-request response caching because committed external writes must
become visible. A new multiprocess transport would preserve many responsibilities
but does not directly remove the measured sort; it is not the first experiment.
An in-memory replacement would change freshness/storage responsibilities and
lacks supporting evidence. No transport, language or framework rewrite is needed.

## Contracts and provisional acceptance

Keep byte-equivalent JSON, ordering/ties, duplicate selection semantics, Unicode,
limit/error handling, a coherent per-request read snapshot and fresh committed
external writes. Keep SQLite and its transaction/integrity guarantees. No
disabled thread checks, relaxed sync, dropped errors, live migration or machine
changes. This fixture has no write API, TLS, proxy, tenant or auth component to
replace. It must still start, serve concurrent reads and shut down cleanly.

Use the already frozen [protocol](protocol.json): CPU milliseconds per successful
request, median reduction >8% and greater than baseline relative range, zero
correctness/errors, no >25% p95/p99 regression and no >16 MiB RSS regression.
These are provisional fixture budgets, not product SLOs. Report build time,
index bytes and write-maintenance costs separately from warm serving gains.

## Validation and benchmark protocol

- Independent golden/differential checks across empty, tiny, typical and larger
  datasets, ties/skew, duplicates, Unicode, limits and JSON error bodies.
- Whole-feature HTTP checks: concurrent reads, external commit/read-after-write,
  external rollback, missing-table errors and later recovery.
- Storage/lifecycle faults: writer-lock failure during index creation, SQLite
  page-budget exhaustion, no partial index, integrity after failure/restart,
  idempotent setup and a working drop-index rollback with original outputs.
- Five alternating pairs per light (one worker, 5 req/s ceiling), target (two
  workers, 40 req/s ceiling) and unpaced near-saturation (four workers) regime.
  Use 12,000 rows, plus tiny and 100,000-row tied-score skew screens. Closed-loop
  request ceilings are not open-loop arrival or capacity guarantees.
- Five-minute target hold per version; a single fifteen-minute finalist soak
  followed by recovery/integrity/rollback checks. Extend for lifecycle cycles
  if observations reveal them. Read-only requests create no WAL/checkpoint
  stream; no long TTL/compaction policy was introduced.
- Preserve every attempt, timeout, unfinished request and generator warning;
  compare CPU/request, RSS, tails and errors. Do not average percentiles.

Partial-send, half-close, custom parser, TLS, cancellation and ring-exhaustion
fault suites are not changed-layer requirements for an index-only change.
The transport stays stdlib; ordinary integration, abrupt disconnect/recovery
and server lifecycle checks still apply. No power-loss claim is made. Disk-full
behavior is exercised with SQLite's real page limit, not a destructive host fill.

## Rollback

Stop the disposable server, drop only `feed_order`, and restart the preceding
implementation; or regenerate its disposable database. Confirm the temporary
sort plan and byte-equivalent results return. Keep the baseline and each candidate
in separate modules. Do not apply this fixture migration to a live database.
Reject the candidate if the screen fails. If any required finalist validation
cannot run, performance remains UNVERIFIED.

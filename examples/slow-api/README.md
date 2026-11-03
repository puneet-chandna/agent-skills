# Slow API educational fixture

This stdlib Python HTTP/SQLite fixture binds to loopback. It is not production
server code or a reproduction of the $12 Server Challenge environment. It uses
no artificial sleeps. See [results](RESULTS.md) and [provenance](evidence.json).

## Contract and experiments

GET /feed returns at most 1000 items, ordered by score descending, then id
ascending. Each item has id, score, title and selected. The limit parameter
accepts one ASCII decimal value from 0 to 10000. Duplicate selection rows must
not duplicate output. Preserve Unicode, compact UTF-8 JSON and byte content
length. Invalid queries return JSON 400; unknown paths return JSON 404; POST
returns JSON 405 and closes the connection; database errors return JSON 503.

Each request owns its SQLite connection. It closes the connection after reading
both tables in one transaction snapshot. The next request sees committed external
writes. There is no write API, authentication, TLS or proxy responsibility.

- baseline.py keeps linear membership and duplicate serialization.
- tune.py removes one serialization. It changes no algorithm or infrastructure.
- optimize.py builds a request-local membership set. Construction cost is included.
  It uses baseline.py because Tune has no accepted winner.
- rebuild.py adds a persistent ordering index to the original baseline. Under
  this skill's budgets, an index change is Mode 3. It changes no rendering code.

The Mode 3 hypothesis comes from the measured scan and temporary ordering
B-tree. An index can remove repeated sorting. A response cache would violate
external-write freshness. A transport rewrite would not remove the measured
sort. Preserve SQLite transactions and external-write maintenance. Setup is
atomic and idempotent; rollback drops feed_order. Tests cover failed setup,
SQLITE_FULL, concurrent reads, fresh writes, integrity, recovery and rollback.
The full original experiment brief is preserved in the local evidence archive.

## Reproduce

From the repository root, use fresh output paths outside the repository:

```bash
python3 -m unittest discover -s tests -v
python3 examples/slow-api/profile_app.py --out /tmp/slow-profile.json
python3 examples/slow-api/bench.py --candidate tune --out /tmp/slow-mode1.json
python3 examples/slow-api/bench.py --candidate optimize --out /tmp/slow-mode2.json
python3 examples/slow-api/bench.py --candidate rebuild --rounds 5 --out /tmp/slow-mode3.json
python3 examples/slow-api/bench.py --candidate rebuild --rounds 5 \
  --concurrency 4 --rate 0 --out /tmp/slow-pressure.json
```

The runner refuses existing output paths. Every trial creates a deterministic
temporary database, starts a server, warms it, measures and drains work, then
stops the server and removes the database. The [protocol](protocol.json) freezes
metrics and provisional budgets. Screen first. If every screen gate passes,
apply the selected mode's full validation ladder. For serving changes in Mode 2
or Mode 3, run a 300-second hold per version. For a Mode 3 finalist, also run a
single 900-second candidate soak with --single. Extend for relevant lifecycle
cycles. No finalist was selected in the recorded screens. Ordinary CI runs no
holds, soaks or speed assertions.

## Measurement boundaries

The client is closed-loop with one outstanding request per worker. Optional
pacing sets a ceiling; missed opportunities are not replayed. Equal concurrency
and pacing do not guarantee equal open-loop arrivals. Throughput uses the full
admission window plus drain. Successful-response percentiles use nearest rank
ceil(p*N)-1, including full body reading and hashing. Raw failures, timeouts,
unfinished work and warmups are preserved separately. Never average percentiles.

Memory observations come from the server's Linux smaps_rollup Rss. Snapshots run
after startup, after warmup, every ten seconds during measurement and after
drain. Their maximum is a sampled lower bound. Startup and warmup transients,
and peaks between samples, can be missed. Sampling cost is recorded per trial;
periodic sampling CPU remains included. Other platforms or unreadable procfs
return unavailable values. No platform reports a certified true peak here, so
the peak-memory gate stays UNVERIFIED even when sampled values are small.
The recorded sampling-read cost was 1.28 to 2.58 ms per trial. Its full observer
effect was not isolated with an uninstrumented control. To verify the memory
gate, collect separate validated evidence for true peak memory.

[Linux documentation](https://man7.org/linux/man-pages/man5/proc_pid_statm.5.html)
recommends smaps or smaps_rollup for accurate resident-memory observations.
[VmHWM](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html) is approximate
and is retained only as a diagnostic. Historical ru_maxrss results can inherit
parent high water. Their RSS conclusions are unreliable. This does not by itself
invalidate independent CPU or latency measurements.

Raw trials, profiles, logs and source snapshots are in a local unpublished
archive. The manifest names the archive and its checksum. Its internal
MANIFEST.json lists per-file checksums. There is no public download URL.
Untracking evidence does not erase previous Git commits. [Agent evaluation
preparation](../../evals/README.md) is separate; no agent trials have run.

# Slow API educational fixture

Local stdlib Python HTTP/SQLite fixture, not production server code or a
reproduction of the $12 Server Challenge environment. Binds to `127.0.0.1`.
There are no third-party dependencies, artificial sleeps or weakened responses.

## API and candidates

`GET /feed?limit=1000` returns `{"items":[...]}` in descending score and ascending
id order, with `id`, `score`, `title`, and boolean `selected` fields. Limit is
0..10000 (default 1000); invalid/duplicate/unknown parameters return JSON 400.
Unknown paths return JSON 404; POST returns JSON 405 and closes the connection.
SQLite errors return JSON 503. Content length counts UTF-8 bytes. Each request
owns/closes a SQLite connection and reads both tables in a transaction snapshot.
Committed external edits become visible on the next request. There is no write
API, auth, TLS or proxy. Existing infrastructure is deliberately simple.

- `baseline.py`: original repeated list membership and two JSON encodes.
- `tune.py`: Mode 1 candidate, one encode; no algorithm change. Inconclusive in
  local trials, so it is not the predecessor for Mode 2.
- `optimize.py`: Mode 2 candidate, request-local set including build cost;
  otherwise the original baseline, including its two encodes.
- `rebuild.py`: Mode 3 candidate, one persistent ordering index with atomic
  setup and drop-index rollback; original rendering unchanged.

No N+1 hypothesis is used. The application executes BEGIN and two SELECTs,
followed by COMMIT. Python sqlite3's statement cache is unchanged. The measured
query-plan sort is a separate Mode 3 experiment; see the
[brief](mode3-brief.md) and [journal](journal.md) for decisions and validation.

## Reproduce

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 examples/slow-api/profile_app.py --out /tmp/profile.json
python3 examples/slow-api/bench.py --out /tmp/mode1.json
python3 examples/slow-api/bench.py --baseline baseline --candidate optimize --out /tmp/mode2.json
python3 examples/slow-api/bench.py --baseline baseline --candidate rebuild --rounds 5 --out /tmp/mode3.json
```

Use a new output path each time; existing evidence is never overwritten. Each
trial seeds a temporary database, warms a fresh server, runs and drains the
workload, then stops the process and removes the database. No services remain.
For manual inspection, from `examples/slow-api`:

```bash
python3 -c 'import data; data.seed("/tmp/slow-feed.db")'
python3 app.py /tmp/slow-feed.db --implementation baseline --port 8000
```

The paired runner alternates AB/BA order, with three pairs by default. The
[frozen protocol](protocol.json) defines the primary CPU/request metric and
provisional budgets, screening and finalist requirements. Examples of sustained
commands, when a candidate merits them:

```bash
python3 examples/slow-api/bench.py --baseline baseline --candidate optimize \
  --rounds 1 --duration 300 --warmup 2 --out /tmp/mode2-hold.json
```

For a future Mode 3 finalist, run the five-minute holds with the appropriate
predecessor/candidate and then a single fifteen-minute candidate soak:

```bash
python3 examples/slow-api/bench.py --baseline baseline --candidate rebuild \
  --rounds 1 --duration 300 --warmup 2 --out /tmp/mode3-hold.json
python3 examples/slow-api/bench.py --candidate rebuild --single \
  --rounds 1 --duration 900 --warmup 2 --out /tmp/mode3-soak.json
```

These sustained commands were not run here because screening selected no finalist.

Do not put holds, soaks or speed assertions into unit tests or CI. A passing
runner command creates evidence; it does not automatically accept a candidate.

## Measurement limits

One outstanding request per worker, optionally paced to an aggregate ceiling.
There are no catch-up arrivals. Same concurrency and pacing policy do not imply
identical open-loop offered arrivals. Throughput uses the full admission window
plus drain. Percentiles use nearest rank `ceil(p*N)-1` over **successful** full
responses, including body reading/hashing; failures remain separate. Never
average run percentiles. Raw samples include start offsets, durations and
outcomes; warmup samples are separate. No automatic retries hide errors.

Raw JSON in [results/](results/) includes commands, timestamps, source hashes,
seed/checksum, Python/SQLite/OS/CPU data, limits or explicit unknown values,
warmup/duration/concurrency/reuse/timeout/reset policy and CPU/RSS summaries.
Generator CPU and missed pacing opportunities are reported. The server and
generator share this host; CPU quota isolation and kernel/cgroup accounting may
be unavailable. Process lifetime peak RSS is not a leak test. Loopback results
cannot establish production capacity, open-loop latency or gains on other data.

The fixture's hand-written results are application experiments. Instruction
regression tests are packaging checks. [Agent evaluations](../../evals/README.md)
are prepared but unrun; behavioral improvement remains unmeasured.

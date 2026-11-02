"""Record application profiles and SQLite plans separately from HTTP benchmarks."""
import argparse
import cProfile
from contextlib import closing
import hashlib
import importlib
import json
from pathlib import Path
import pstats
import sqlite3
import tempfile
import time

import app
import bench
import data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--implementation', default='baseline')
    parser.add_argument('--rows', type=int, default=12000)
    parser.add_argument('--repeats', type=int, default=100)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.rows < 0 or args.repeats < 1:
        parser.error('new output path, nonnegative rows and positive repeats required')
    implementation = importlib.import_module(args.implementation)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'db'
        checksum = data.seed(path, args.rows)
        started = time.perf_counter()
        if hasattr(implementation, 'prepare'):
            implementation.prepare(path)
        startup = time.perf_counter() - started
        with closing(sqlite3.connect(path)) as db:
            plan = db.execute('EXPLAIN QUERY PLAN ' + app.QUERY, (1000,)).fetchall()
        profile = cProfile.Profile()
        profile.enable()
        for _ in range(args.repeats):
            implementation.render(*app.read(path, 1000))
        profile.disable()
        entries = pstats.Stats(profile).stats
        artifact = dict(implementation=args.implementation, rows=args.rows, repeats=args.repeats,
                        seed=17, dataset_sha256=checksum, plan=plan,
                        prepare_seconds=startup, environment=bench.environment(),
                        provenance=bench.provenance(), explicit_statements_per_request=3,
                        statement_note='BEGIN and two SELECTs plus implicit COMMIT; statement caching unchanged.',
                        total_profile_seconds=sum(v[2] for v in entries.values()),
                        functions=[dict(file=k[0], line=k[1], function=k[2], calls=v[1],
                                        self_seconds=v[2], cumulative_seconds=v[3])
                                   for k, v in sorted(entries.items(), key=lambda e: -e[1][3])])
        args.out.write_text(json.dumps(artifact, indent=2) + '\n')
        print(json.dumps({k: artifact[k] for k in ('implementation', 'rows', 'plan', 'total_profile_seconds')}))

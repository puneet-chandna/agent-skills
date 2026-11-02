"""Changed-storage-layer checks for the Mode 3 index experiment."""
from contextlib import closing
import sqlite3
import tempfile
from pathlib import Path
from unittest import mock
import unittest

from test_slow_api import oracle
import app
import baseline
import data
import rebuild


class IndexTests(unittest.TestCase):
    def test_setup_rollback_integrity_and_freshness(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'db'
            data.seed(path, 12000)
            before = baseline.render(*app.read(path, 1000))
            for _ in range(2):
                rebuild.prepare(path)
                with closing(sqlite3.connect(path)) as db, db:
                    plan = str(db.execute('EXPLAIN QUERY PLAN ' + app.QUERY, (1000,)).fetchall())
                    self.assertIn('feed_order', plan)
                    self.assertNotIn('TEMP B-TREE', plan)
                self.assertEqual(baseline.render(*app.read(path, 1000)), before)
            with closing(sqlite3.connect(path)) as db, db:
                db.execute('INSERT INTO items VALUES(?,?,?)', (99999, 999, 'fresh'))
            self.assertEqual(oracle(path, 1)['items'][0]['id'], 99999)
            self.assertEqual(app.read(path, 1)[0][0][0], 99999)
            expected = baseline.render(*app.read(path, 1000))
            rebuild.rollback(path)
            rebuild.rollback(path)
            self.assertEqual(baseline.render(*app.read(path, 1000)), expected)
            with closing(sqlite3.connect(path)) as db:
                self.assertIn('TEMP B-TREE', str(db.execute('EXPLAIN QUERY PLAN ' + app.QUERY, (1000,)).fetchall()))
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_failed_setup_lock_and_page_exhaustion_leave_no_partial_index(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'db'
            data.seed(path, 12000)
            with closing(sqlite3.connect(path)) as writer:
                writer.execute('BEGIN IMMEDIATE')
                with self.assertRaises(sqlite3.OperationalError):
                    app.make_server(path, 'rebuild')
                writer.rollback()
            connect = sqlite3.connect
            def limited_connect(*args, **kwargs):
                db = connect(*args, **kwargs)
                pages = db.execute('PRAGMA page_count').fetchone()[0]
                db.execute(f'PRAGMA max_page_count={pages}')
                return db
            with mock.patch.object(rebuild.sqlite3, 'connect', side_effect=limited_connect):
                with self.assertRaises(sqlite3.DatabaseError) as caught:
                    rebuild.prepare(path)
                self.assertEqual(caught.exception.sqlite_errorcode, sqlite3.SQLITE_FULL)
            with closing(connect(path)) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM sqlite_master WHERE name='feed_order'").fetchone()[0], 0)
                self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            rebuild.prepare(path)
            rebuild.rollback(path)
            self.assertEqual(len(app.read(path, 1000)[0]), 1000)


if __name__ == '__main__':
    unittest.main()

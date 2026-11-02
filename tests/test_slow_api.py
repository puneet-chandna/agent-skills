"""Independent contract oracle and HTTP integration checks for the example."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import http.client
import importlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples' / 'slow-api'
sys.path.insert(0, str(EXAMPLE))
import app
import data

VARIANTS = ('baseline', 'tune', 'optimize', 'rebuild')


def oracle(path, limit):
    # Derive semantics from rows, not an optimized implementation or its helpers.
    with closing(sqlite3.connect(path)) as db:
        rows = list(db.execute('SELECT id, score, title FROM items'))
        chosen = list(db.execute('SELECT item_id FROM selected'))
    rows.sort(key=lambda row: (-row[1], row[0]))
    return {'items': [dict(id=i, score=s, title=t,
                           selected=any(i == entry[0] for entry in chosen))
                      for i, s, t in rows[:limit]]}


class FixtureTests(unittest.TestCase):
    def test_golden_and_differential(self):
        with tempfile.TemporaryDirectory() as folder:
            for size in (0, 3, 16, 12000):
                path = Path(folder) / str(size)
                data.seed(path, size)
                if size == 3:
                    with closing(sqlite3.connect(path)) as db, db:
                        db.execute('DELETE FROM items')
                        db.execute('DELETE FROM selected')
                        db.executemany('INSERT INTO items VALUES(?,?,?)',
                                       [(3, 1, 'duplicate'), (1, 2, '雪'), (2, 2, 'duplicate')])
                        db.executemany('INSERT INTO selected VALUES(?,?)', [(1, 2), (2, 2)])
                    golden = (b'{"items":[{"id":1,"score":2,"title":"\xe9\x9b\xaa","selected":false},'
                              b'{"id":2,"score":2,"title":"duplicate","selected":true},'
                              b'{"id":3,"score":1,"title":"duplicate","selected":false}]}')
                for limit in (0, 2, 1000, 10000):
                    rows, selected = app.read(path, limit)
                    expected = oracle(path, limit)
                    for variant in VARIANTS:
                        body, length = importlib.import_module(variant).render(rows, selected)
                        self.assertEqual(length, len(body))
                        self.assertEqual(json.loads(body), expected)
                        if size == 3 and limit >= 3:
                            self.assertEqual(body, golden)

    def test_http_contract_freshness_errors_and_concurrent_reads(self):
        with tempfile.TemporaryDirectory() as folder:
            for variant in VARIANTS:
                path = Path(folder) / variant
                data.seed(path, 16)
                with app.make_server(path, variant) as server:
                    thread = threading.Thread(target=server.serve_forever,
                                              kwargs={'poll_interval': .01})
                    thread.start()
                    def request(route='/feed', method='GET'):
                        conn = http.client.HTTPConnection(*server.server_address, timeout=3)
                        try:
                            conn.request(method, route)
                            response = conn.getresponse()
                            body = response.read()
                            self.assertEqual(int(response.getheader('Content-Length')), len(body))
                            self.assertEqual(response.getheader('Content-Type'),
                                             'application/json; charset=utf-8')
                            return response.status, json.loads(body)
                        finally:
                            conn.close()
                    try:
                        self.assertEqual(request(), (200, oracle(path, 1000)))
                        for route in ('/feed?limit=-1', '/feed?limit=10001', '/feed?limit=',
                                      '/feed?limit=2&limit=3', '/feed?other=2', '/feed?limit=²'):
                            # URL ASCII encoding is the client responsibility.
                            route = route.replace('²', '%C2%B2')
                            self.assertEqual(request(route), (400, {'error': 'invalid limit'}))
                        self.assertEqual(request('/missing'), (404, {'error': 'not found'}))
                        self.assertEqual(request(method='POST'), (405, {'error': 'method not allowed'}))
                        with closing(sqlite3.connect(path)) as db, db:
                            db.execute('INSERT INTO items VALUES(?,?,?)', (999, 999, 'fresh 雪'))
                        with ThreadPoolExecutor(max_workers=4) as pool:
                            replies = list(pool.map(lambda _: request('/feed?limit=1'), range(8)))
                        self.assertTrue(all(r == (200, oracle(path, 1)) for r in replies))
                        with closing(sqlite3.connect(path)) as db:
                            db.execute('BEGIN')
                            db.execute('DELETE FROM items')
                            db.rollback()
                        self.assertEqual(request(), (200, oracle(path, 1000)))
                        with closing(sqlite3.connect(path)) as db, db:
                            db.execute('DROP TABLE selected')
                        self.assertEqual(request(), (503, {'error': 'database unavailable'}))
                    finally:
                        server.shutdown()
                        thread.join()


if __name__ == '__main__':
    unittest.main()

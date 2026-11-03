"""Deterministic educational data; no generated database belongs in git."""
import hashlib
import json
import random
import sqlite3
from contextlib import closing


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def seed(path, rows=12000, seed_value=17, skew=False):
    rng = random.Random(seed_value)
    items = [(i, 0 if skew else rng.randrange(100),
              ('café 雪 "quote" \\ line\n ' * 3) + str(i))
             for i in range(1, rows + 1)]
    selected = [(i, rng.randrange(1, max(2, rows + 1))) for i in range(256)]
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript('CREATE TABLE items(id INTEGER PRIMARY KEY, score INTEGER, title TEXT);'
                         'CREATE TABLE selected(seq INTEGER PRIMARY KEY, item_id INTEGER);')
        db.executemany('INSERT INTO items VALUES(?,?,?)', items)
        db.executemany('INSERT INTO selected VALUES(?,?)', selected)
    return hashlib.sha256(encode([items, selected])).hexdigest()


def payload(rows, selected):
    return {'items': [{'id': i, 'score': score, 'title': title, 'selected': i in selected}
                      for i, score, title in rows]}

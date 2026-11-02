"""Mode 3: persistent ordering index, with explicit local setup and rollback."""
from contextlib import closing
import sqlite3

from baseline import render


def prepare(path):
    with closing(sqlite3.connect(path, timeout=.1)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('CREATE INDEX IF NOT EXISTS feed_order ON items(score DESC, id ASC)')


def rollback(path):
    with closing(sqlite3.connect(path, timeout=.1)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('DROP INDEX IF EXISTS feed_order')

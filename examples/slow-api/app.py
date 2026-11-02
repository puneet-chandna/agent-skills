"""Educational loopback HTTP/SQLite fixture, not production server code."""
import argparse
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib
import socket
import sqlite3
import time
from urllib.parse import parse_qs, urlsplit

from data import encode

QUERY = 'SELECT id, score, title FROM items ORDER BY score DESC, id ASC LIMIT ?'


def read(db_path, limit):
    # Each request owns and closes its connection; both reads share a snapshot.
    with closing(sqlite3.connect(db_path, timeout=1)) as db, db:
        db.execute('BEGIN')
        rows = db.execute(QUERY, (limit,)).fetchall()
        selected = [r[0] for r in db.execute('SELECT item_id FROM selected ORDER BY seq')]
    return rows, selected


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    timeout = 2

    def setup(self):
        super().setup()
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def log_message(self, *args):
        pass

    def reply(self, status, body, length=None):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body) if length is None else length))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True

    def do_POST(self):
        self.close_connection = True
        self.reply(405, encode({'error': 'method not allowed'}))

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path != '/feed':
            self.reply(404, encode({'error': 'not found'}))
            return
        params = parse_qs(url.query, keep_blank_values=True)
        value = params.get('limit', ['1000'])
        if (set(params) - {'limit'} or len(value) != 1 or not value[0].isascii()
                or not value[0].isdecimal() or len(value[0]) > 5
                or not 0 <= int(value[0]) <= 10000):
            self.reply(400, encode({'error': 'invalid limit'}))
            return
        try:
            rows, selected = read(self.server.db_path, int(value[0]))
            body, length = self.server.render(rows, selected)
        except sqlite3.Error:
            self.reply(503, encode({'error': 'database unavailable'}))
            return
        self.reply(200, body, length)


def make_server(db_path, implementation='baseline', port=0):
    implementation = importlib.import_module(implementation)
    started = time.perf_counter()
    if hasattr(implementation, 'prepare'):
        implementation.prepare(db_path)
    prepare_seconds = time.perf_counter() - started
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.db_path = str(db_path)
    server.render = implementation.render
    server.prepare_seconds = prepare_seconds
    return server


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database')
    parser.add_argument('--implementation', default='baseline')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    with make_server(args.database, args.implementation, args.port) as server:
        try:
            server.serve_forever(poll_interval=.05)
        except KeyboardInterrupt:
            pass

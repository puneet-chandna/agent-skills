"""Fast accounting/artifact tests. No speed gates or sustained performance runs."""
import http.server
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from types import SimpleNamespace

from test_slow_api import EXAMPLE
import bench


class BenchmarkTests(unittest.TestCase):
    def test_recorded_measurement_source_resolves_to_committed_bytes(self):
        evidence = json.loads((EXAMPLE / 'evidence.json').read_text())
        revision = evidence['source_revision']
        for name, digest in evidence['source_sha256'].items():
            content = subprocess.check_output(['git', 'show',
                revision + ':examples/slow-api/' + name], cwd=EXAMPLE)
            self.assertEqual(hashlib.sha256(content).hexdigest(), digest)
        protocol = subprocess.check_output(['git', 'show',
            revision + ':examples/slow-api/protocol.json'], cwd=EXAMPLE)
        self.assertEqual(hashlib.sha256(protocol).hexdigest(), evidence['protocol_sha256'])
        self.assertEqual(evidence['source_status'], '')
        self.assertEqual(evidence['availability'], 'local_unpublished')

    def test_accounting_and_percentiles(self):
        samples = [[0, 1000, 200], [1, 3000, 200], [2, 2000, 503],
                   [3, 5000, 'timeout'], [4, 4000, 'transport'], [5, 6000, 'semantic']]
        result = bench.summarize(samples, .002, .01)
        self.assertEqual((result['attempted'], result['completed'], result['successful']), (6, 4, 2))
        self.assertEqual((result['timeouts'], result['transport_failures'],
                          result['semantic_failures']), (1, 1, 1))
        self.assertAlmostEqual(result['error_rate'], 4 / 6)
        self.assertEqual((result['p50_ms'], result['p99_ms']), (1, 3))
        self.assertEqual(result['unfinished_at_deadline'], 5)
        self.assertIsNone(bench.percentile([], .99))

    def test_artifact_smoke_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'raw.json'
            command = [sys.executable, str(EXAMPLE / 'bench.py'), '--out', str(output),
                       '--candidate', 'optimize', '--rows', '16', '--rounds', '2',
                       '--duration', '.08', '--warmup', '.03', '--rate', '0',
                       '--concurrency', '1']
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            artifact = json.loads(output.read_text())
            self.assertEqual([t['variant'] for t in artifact['trials']],
                             ['baseline', 'optimize', 'optimize', 'baseline'])
            self.assertTrue(artifact['provenance']['sources'])
            for trial in artifact['trials']:
                summary = trial['summary']
                self.assertGreater(summary['successful'], 0)
                self.assertEqual(summary['attempted'], len(trial['samples']))
                self.assertEqual(summary['error_rate'], 0)
                self.assertIsNone(summary['server_peak_rss_bytes'])
                self.assertEqual(summary['memory_gate'], 'UNVERIFIED')
                recomputed = bench.summarize(trial['samples'], .08, summary['elapsed_seconds'])
                for key in recomputed:
                    self.assertEqual(summary[key], recomputed[key])
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('refusing to overwrite', result.stderr)

    def test_http_failures_are_saved_in_valid_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'failures.json'
            result = subprocess.run([sys.executable, str(EXAMPLE / 'bench.py'),
                '--out', str(output), '--candidate', 'baseline', '--single',
                '--rounds', '1', '--rows', '0', '--duration', '.04', '--warmup', '.02',
                '--path', '/missing', '--rate', '0', '--concurrency', '1'],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            trial = json.loads(output.read_text())['trials'][0]
            self.assertGreater(trial['summary']['attempted'], 0)
            self.assertEqual(trial['summary']['successful'], 0)
            self.assertEqual(trial['summary']['error_rate'], 1)
            self.assertTrue(all(s[2] == 404 for s in trial['samples']))

    def test_real_timeout_and_http_failure_accounting(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path == '/timeout':
                    # Deliberately unfinished response, no artificial fixture delay.
                    self.send_response(200)
                    self.send_header('Content-Length', '100')
                    self.end_headers()
                    self.wfile.flush()
                    try:
                        self.connection.recv(1)
                    except OSError:
                        pass
                else:
                    self.send_response(503)
                    self.send_header('Content-Length', '0')
                    self.end_headers()
        with http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': .01})
            thread.start()
            try:
                args = SimpleNamespace(concurrency=1, rate=0, timeout=.02, path='/timeout')
                result = bench.load(server.server_port, args, .06, 'unused')
                self.assertGreater(result['summary']['timeouts'], 0)
                self.assertEqual(result['summary']['completed'], 0)
                args.path = '/failure'
                result = bench.load(server.server_port, args, .04, 'unused')
                self.assertEqual(result['summary']['attempted'], result['summary']['completed'])
                self.assertEqual(result['summary']['successful'], 0)
                self.assertEqual(result['summary']['error_rate'], 1)
            finally:
                server.shutdown()
                thread.join()


if __name__ == '__main__':
    unittest.main()

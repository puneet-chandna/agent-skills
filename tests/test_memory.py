"""Server RSS must not report the parent's resident-memory high water."""
import multiprocessing
from pathlib import Path
import sys
import unittest
from unittest import mock

from test_slow_api import EXAMPLE
import bench


def report_memory(pipe):
    pipe.send(bench.stats())
    pipe.close()


class MemoryTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == 'linux' and Path('/proc/self/smaps_rollup').exists(),
                         'Linux smaps_rollup required')
    def test_parent_allocation_does_not_contaminate_server_rss(self):
        def sample():
            context = multiprocessing.get_context('spawn')
            parent, child = context.Pipe()
            process = context.Process(target=report_memory, args=(child,))
            process.start()
            child.close()
            try:
                self.assertTrue(parent.poll(10))
                result = parent.recv()
            finally:
                process.join(10)
                if process.is_alive():
                    process.terminate()
                    process.join()
                parent.close()
            self.assertEqual(process.exitcode, 0)
            return result
        before = sample()
        allocation = bytearray(96 * 1024 * 1024)
        after = sample()
        self.assertEqual(len(allocation), 96 * 1024 * 1024)
        self.assertIsNone(after['peak_rss_bytes'])
        self.assertIsNotNone(after['current_rss_bytes'])
        self.assertLess(abs(after['current_rss_bytes'] - before['current_rss_bytes']),
                        16 * 1024 * 1024)

    def test_unavailable_memory_is_not_a_zero_or_certified_peak(self):
        with mock.patch.object(bench, 'text_file', return_value='unknown'):
            result = bench.stats()
        self.assertIsNone(result['current_rss_bytes'])
        self.assertIsNone(result['peak_rss_bytes'])


if __name__ == '__main__':
    unittest.main()

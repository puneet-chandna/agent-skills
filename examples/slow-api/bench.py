"""Small closed-loop paired runner. No capacity claim or speedup assertion."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import http.client
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone

import app
import baseline
import data

HERE = Path(__file__).resolve().parent


def text_file(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return 'unknown'


def environment():
    import sqlite3
    cpu = text_file('/proc/cpuinfo')
    return dict(python=sys.version, sqlite=sqlite3.sqlite_version,
                os=platform.platform(), cpu=next((line.split(':', 1)[1].strip()
                for line in cpu.splitlines() if line.startswith('model name')), 'unknown'),
                logical_cpus=os.cpu_count(), affinity_cpus=(len(os.sched_getaffinity(0))
                if hasattr(os, 'sched_getaffinity') else 'unknown'),
                cpu_quota=text_file('/sys/fs/cgroup/cpu.max'),
                memory_limit=text_file('/sys/fs/cgroup/memory.max'),
                swap_limit=text_file('/sys/fs/cgroup/memory.swap.max'),
                memory_total=next((line for line in text_file('/proc/meminfo').splitlines()
                                   if line.startswith('MemTotal:')), 'unknown'))


def stats():
    try:
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        rss *= 1 if sys.platform == 'darwin' else 1024
    except (ImportError, AttributeError):
        rss = None
    status = text_file('/proc/self/status')
    current = next((int(line.split()[1]) * 1024 for line in status.splitlines()
                    if line.startswith('VmRSS:')), None)
    return {'cpu_seconds': time.process_time(), 'peak_rss_bytes': rss,
            'current_rss_bytes': current, 'active_threads': threading.active_count()}


def serve(pipe, path, variant):
    try:
        started = time.perf_counter()
        with app.make_server(path, variant) as server:
            thread = threading.Thread(target=server.serve_forever,
                                      kwargs={'poll_interval': .01})
            thread.start()
            pipe.send({'port': server.server_port,
                       'startup_seconds': time.perf_counter() - started,
                       'prepare_seconds': server.prepare_seconds,
                       'database_bytes': Path(path).stat().st_size})
            try:
                while pipe.recv() == 'stats':
                    pipe.send(stats())
            finally:
                server.shutdown()
                thread.join()
    except Exception as error:
        pipe.send({'error': repr(error)})
    finally:
        pipe.close()


def percentile(values, fraction):
    """Nearest rank: sorted values[ceil(p*n)-1]. Empty samples give null."""
    return sorted(values)[max(0, math.ceil(fraction * len(values)) - 1)] if values else None


def summarize(samples, duration, elapsed):
    outcomes = [s[2] for s in samples]
    successful = outcomes.count(200)
    latencies = [s[1] / 1000 for s in samples if s[2] == 200]
    attempted = len(samples)
    return dict(attempted=attempted,
                completed=sum(isinstance(o, int) or o == 'semantic' for o in outcomes),
                successful=successful, timeouts=outcomes.count('timeout'),
                transport_failures=outcomes.count('transport'),
                semantic_failures=outcomes.count('semantic'),
                unfinished_at_deadline=sum(s[0] + s[1] > duration * 1e6 for s in samples),
                unfinished_after_drain=0,
                successful_rps=successful / elapsed,
                error_rate=(attempted - successful) / attempted if attempted else None,
                p50_ms=percentile(latencies, .50), p95_ms=percentile(latencies, .95),
                p99_ms=percentile(latencies, .99))


def load(port, args, duration, expected):
    barrier = threading.Barrier(args.concurrency + 1)
    def worker(index):
        samples, errors = [], {}
        connection = http.client.HTTPConnection('127.0.0.1', port, timeout=args.timeout)
        barrier.wait()
        period = args.concurrency / args.rate if args.rate else 0
        due = start + (index / args.rate if args.rate else 0)
        overruns = 0
        try:
            while due < start + duration:
                if due > time.perf_counter():
                    time.sleep(due - time.perf_counter())
                request_start = time.perf_counter()
                if request_start >= start + duration:
                    break
                try:
                    connection.request('GET', args.path)
                    response = connection.getresponse()
                    body = response.read()
                    outcome = response.status
                    if outcome == 200 and hashlib.sha256(body).hexdigest() != expected:
                        outcome = 'semantic'
                except (TimeoutError, socket.timeout) as error:
                    outcome = 'timeout'
                    errors[repr(error)] = errors.get(repr(error), 0) + 1
                    connection.close()
                except (OSError, http.client.HTTPException) as error:
                    outcome = 'transport'
                    errors[repr(error)] = errors.get(repr(error), 0) + 1
                    connection.close()
                ended = time.perf_counter()
                samples.append([round((request_start - start) * 1e6),
                                round((ended - request_start) * 1e6), outcome])
                overruns += bool(period and ended > due + period)
                due = max(due + period, ended)
        finally:
            connection.close()
        return samples, errors, overruns

    cpu = time.process_time()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(worker, i) for i in range(args.concurrency)]
        start = time.perf_counter()
        barrier.wait()
        workers = [future.result() for future in futures]
    remaining = start + duration - time.perf_counter()
    if remaining > 0:
        time.sleep(remaining)
    # Include idle time after the last paced request, plus any actual drain.
    elapsed = max(duration, time.perf_counter() - start)
    samples = sorted((sample for worker in workers for sample in worker[0]), key=lambda s: s[0])
    summary = summarize(samples, duration, elapsed)
    generator_cpu = time.process_time() - cpu
    summary.update(elapsed_seconds=elapsed, generator_cpu_seconds=generator_cpu,
                   generator_cpu_cores=generator_cpu / elapsed,
                   pacing_overruns=sum(w[2] for w in workers),
                   pacing_ceiling_opportunities=duration * args.rate if args.rate else None)
    warnings = []
    if generator_cpu / elapsed >= .8:
        warnings.append('Generator used >=0.8 CPU core; its Python work may limit load.')
    if summary['pacing_overruns']:
        warnings.append('Closed-loop responses missed pacing opportunities; no catch-up arrivals.')
    return dict(summary=summary, samples=samples, errors=[w[1] for w in workers], warnings=warnings)


def trial(args, variant):
    with tempfile.TemporaryDirectory(prefix='slow-api-') as folder:
        path = Path(folder) / 'seed.db'
        checksum = data.seed(path, args.rows, args.seed, args.skew)
        expected = hashlib.sha256(baseline.render(*app.read(path, args.limit))[0]).hexdigest()
        ctx = multiprocessing.get_context('spawn')
        parent, child = ctx.Pipe()
        process = ctx.Process(target=serve, args=(child, str(path), variant))
        process.start()
        child.close()
        try:
            if not parent.poll(30):
                raise RuntimeError('Server did not start within 30 seconds')
            startup = parent.recv()
            if 'error' in startup:
                raise RuntimeError(startup['error'])
            warmup = load(startup['port'], args, args.warmup, expected)
            parent.send('stats')
            before = parent.recv()
            resource_samples = []
            stop_monitor = threading.Event()
            measurement_start = time.perf_counter()
            def monitor():
                while not stop_monitor.wait(10):
                    parent.send('stats')
                    resource_samples.append({'offset_seconds': time.perf_counter() - measurement_start,
                                             **parent.recv()})
            monitor_thread = threading.Thread(target=monitor)
            monitor_thread.start()
            try:
                measured = load(startup['port'], args, args.duration, expected)
            finally:
                stop_monitor.set()
                monitor_thread.join()
            parent.send('stats')
            after = parent.recv()
            cpu = after['cpu_seconds'] - before['cpu_seconds']
            successful = measured['summary']['successful']
            measured['summary'].update(server_cpu_seconds=cpu,
                server_cpu_ms_per_success=1000 * cpu / successful if successful else None,
                server_peak_rss_bytes=after['peak_rss_bytes'])
            return dict(variant=variant, timestamp=datetime.now(timezone.utc).isoformat(),
                        dataset_sha256=checksum, startup=startup,
                        resource_samples=resource_samples,
                        warmup=warmup, before=before, after=after, **measured)
        finally:
            if process.is_alive():
                try:
                    parent.send('stop')
                except (OSError, BrokenPipeError):
                    pass
            process.join(5)
            if process.is_alive():
                process.terminate()
                process.join()
            parent.close()


def provenance():
    def git(*args):
        try:
            return subprocess.check_output(['git', *args], cwd=HERE, text=True,
                                           stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return 'unknown'
    return dict(revision=git('rev-parse', 'HEAD'), dirty=git('status', '--porcelain=v1'),
                sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in HERE.glob('*.py')},
                protocol_sha256=hashlib.sha256((HERE / 'protocol.json').read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='baseline')
    parser.add_argument('--candidate', default='tune')
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--duration', type=float, default=2)
    parser.add_argument('--warmup', type=float, default=.5)
    parser.add_argument('--concurrency', type=int, default=2)
    parser.add_argument('--rate', type=float, default=40)
    parser.add_argument('--timeout', type=float, default=2)
    parser.add_argument('--rows', type=int, default=12000)
    parser.add_argument('--limit', type=int, default=1000)
    parser.add_argument('--seed', type=int, default=17)
    parser.add_argument('--skew', action='store_true')
    parser.add_argument('--single', action='store_true', help='One candidate trial per round, for a soak')
    parser.add_argument('--path', default=None)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if (not all(math.isfinite(x) and x > 0 for x in (args.duration, args.warmup, args.timeout))
            or not math.isfinite(args.rate) or args.rate < 0 or args.rounds < 1
            or args.concurrency < 1 or args.rows < 0 or not 0 <= args.limit <= 10000):
        parser.error('positive finite durations/rounds/concurrency; nonnegative rate/rows; limit 0..10000')
    if args.out.exists():
        parser.error('refusing to overwrite an existing artifact')
    args.path = args.path or f'/feed?limit={args.limit}'
    artifact = dict(schema_version=1, command=[sys.executable, *sys.argv],
        timestamp=datetime.now(timezone.utc).isoformat(), environment=environment(),
        provenance=provenance(), config={k: str(v) if isinstance(v, Path) else v
                                        for k, v in vars(args).items()},
        protocol=json.loads((HERE / 'protocol.json').read_text()),
        load_model='Closed-loop, one outstanding request per worker; optional pacing ceiling, no catch-up. '
                   'Same concurrency/pacing policy, not equal open-loop arrivals or a capacity guarantee.',
        reset='New deterministic DB and new server per trial; warmup excluded; OS page cache not flushed.',
        connection_reuse='One HTTP/1.1 connection per worker per phase; reconnect after errors; no retries.',
        timing='samples=[start_offset_us, elapsed_us, outcome]; 200 means matching body checksum. '
               'Nearest-rank percentiles over successful requests only, errors retained separately. '
               'Throughput uses admission plus drain elapsed. Latencies include full body read/hash.',
        limitations=['Generator and server share host resources; CPU quota isolation unavailable.',
                     'RSS is process lifetime high water, not kernel/socket/page cache or a memory leak test.',
                     'Warmup and measured samples retained, but only measured samples enter summaries.',
                     'Expected body comes from baseline; independent contract tests must also pass.'],
        trials=[])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    def save():
        temporary = args.out.with_suffix(args.out.suffix + '.tmp')
        temporary.write_text(json.dumps(artifact, separators=(',', ':'), allow_nan=False) + '\n')
        temporary.replace(args.out)
    save()
    try:
        for number in range(args.rounds):
            order = [args.candidate] if args.single else [args.baseline, args.candidate]
            if number % 2:
                order.reverse()
            for variant in order:
                artifact['active_trial'] = {'pair': number + 1, 'variant': variant,
                                            'started': datetime.now(timezone.utc).isoformat()}
                save()
                result = trial(args, variant)
                result['pair'] = number + 1
                artifact['trials'].append(result)
                artifact.pop('active_trial')
                save()
                print(json.dumps({'pair': number + 1, 'variant': variant, **result['summary']}), flush=True)
    except BaseException as error:
        artifact['interrupted'] = repr(error)
        save()
        raise


if __name__ == '__main__':
    main()

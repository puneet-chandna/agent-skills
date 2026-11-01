#!/usr/bin/env python3
"""Check transport SLOs only; never infer correctness or capacity from a summary."""
import argparse
import json
import math
import sys
from pathlib import Path


def number(value, label, *, minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: missing or non-numeric value")
    if not math.isfinite(value) or value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{label}: value outside valid range")
    return value


def values(metrics, name):
    metric = metrics.get(name)
    if not isinstance(metric, dict):
        raise ValueError(f"{name}: missing metric")
    result = metric.get("values", metric)
    if not isinstance(result, dict):
        raise ValueError(f"{name}: invalid metric values")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("--p95-ms", type=float, default=500)
    parser.add_argument("--p99-ms", type=float, default=1000)
    parser.add_argument("--max-error-rate", type=float, default=0.01)
    args = parser.parse_args()
    report = {
        "status": "UNVERIFIED",
        "scope": "transport SLO only; not API correctness, duration, resources or official capacity",
        "summary": str(args.summary),
    }
    try:
        p95_limit = number(args.p95_ms, "p95 limit", minimum=0.000001)
        p99_limit = number(args.p99_ms, "p99 limit", minimum=0.000001)
        error_limit = number(args.max_error_rate, "error limit", minimum=0.000000001, maximum=1)
        if p99_limit < p95_limit:
            raise ValueError("p99 limit must be at least p95 limit")
        data = json.loads(args.summary.read_text())
        if not isinstance(data, dict) or not isinstance(data.get("metrics"), dict):
            raise ValueError("missing metrics object")
        metrics = data["metrics"]
        duration = values(metrics, "http_req_duration")
        p95 = number(duration.get("p(95)"), "p95")
        p99 = number(duration.get("p(99)"), "p99")
        if p99 < p95:
            raise ValueError("p99 is less than p95")
        errors = number(values(metrics, "http_req_failed").get("rate"), "error rate", maximum=1)
        count = number(values(metrics, "http_reqs").get("count"), "request count", minimum=1)
        if int(count) != count:
            raise ValueError("request count must be an integer")
        gates = {"p95": p95 < p95_limit, "p99": p99 < p99_limit, "error_rate": errors < error_limit}
        report.update(
            status="PASS" if all(gates.values()) else "FAIL",
            metrics={"p95_ms": p95, "p99_ms": p99, "error_rate": errors, "request_count": count},
            limits={"p95_ms_exclusive": p95_limit, "p99_ms_exclusive": p99_limit,
                    "error_rate_exclusive": error_limit},
            gates=gates,
        )
        # Tagged submetrics are optional and may cover only some endpoints.
        tagged = {}
        for name in sorted(metrics):
            if name.startswith("http_req_duration{") or name.startswith("http_req_failed{"):
                val = values(metrics, name)
                fields = ("p(95)", "p(99)") if name.startswith("http_req_duration{") else ("rate",)
                tagged[name] = {key: number(val[key], name + ":" + key,
                                           maximum=1 if key == "rate" else None)
                                for key in fields if key in val}
        report["tagged_metrics"] = tagged
        if "checks" in metrics:
            check_values = values(metrics, "checks")
            if "rate" in check_values:
                report["check_success_rate"] = number(check_values["rate"], "checks rate", maximum=1)
        report["limitations"] = [
            "Default gates assess aggregate HTTP latency and failures only.",
            "Tagged metrics are reported, not gated; add per-route thresholds in the load harness.",
            "A transport PASS can coexist with failed checks or failed writes; inspect both.",
            "Verify hold duration, workload, committed data, resources and generator capacity separately.",
        ]
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError, OverflowError) as error:
        report["status"] = "UNVERIFIED"
        report["reason"] = str(error)
        print(json.dumps(report, indent=2, allow_nan=False))
        return 2
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

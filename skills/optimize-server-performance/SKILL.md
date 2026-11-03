---
name: optimize-server-performance
description: Profile and improve backend, HTTP server, database, networking and application algorithm performance through controlled experiments and correctness checks. Use for slow APIs, high p95/p99, low throughput, excessive CPU/memory, SQLite/WAL contention, many connections or $12 Server Challenge submissions. Supports Tune, Optimize and Rebuild change budgets. Default to Mode 1.
---

# Optimize Server Performance

For unspecified requests, default to Mode 1. This includes “make it faster.” State the selected mode. State whether the context is production or a challenge. Never silently escalate, including subtasks. A mode is a ceiling, not a rewrite requirement. Narrower user constraints prevail.

| Mode | Permitted changes | Required boundaries |
|---|---|---|
| **1 Tune** | Remove redundant work and copies. Reuse resources. Tune existing queries and pools. | Preserve algorithms, data representation, architecture and stack. |
| **2 Optimize** | Use Tune techniques. Change application algorithms, data structures, layout, batching and concurrency. | Preserve language, framework, database engine, schema, indexes, library feature architecture, transport, runtime, kernel and native dependencies. |
| **3 Rebuild** | Change any justified architectural layer, including storage, transport, libraries and language. | Preserve required behavior, security, durability, compatibility and operational responsibilities. |

Mode 3 permits reversible local experiments. It does not inherit lower-mode architectural restrictions. It does not independently authorize destructive migrations, live deployment or machine-wide changes. When replacing a component, preserve its responsibilities. No mode permits weaker contracts.

## 1. Inspect

Read applicable AGENTS.md. Inspect git status, manifests, hot paths, tests and previous performance records. Confirm the actual target. Do not treat a reference repository as the target. Identify the workload, data sizes, skew and resource limits. Identify required semantics, including isolation, validation, ordering, freshness, acknowledged writes and proxy or TLS responsibilities.

## 2. Read the required guidance

Before planning edits, read [modes.md](references/modes.md): “Selecting a mode,” the selected mode's section, its explicitly inherited requirements, and “Validation ladder.” Read relevant sections of [measurement.md](references/measurement.md). Read relevant [technique entries](references/technique-catalog.md) and the project journal template. These readings are mandatory.

When useful, consult matching [playbook sections](references/optimization-playbook.md) and [case studies](references/case-studies.md). For contest work or requests for current information, read [challenge research](references/challenge-research.md) and its refresh instructions. Query only relevant [catalog entries](references/submission-catalog.json). Keep historical, official, local and projected evidence separate.

## 3. Establish evidence

Before edits, run correctness checks. Measure the baseline on disposable authorized data. Profile the limiting resource. Where relevant, inspect query plans and counts. Record source, environment and dataset provenance. Check generator health.

Before candidate measurements, freeze the primary metric, minimum effect, regression budgets and resource budgets. Use actual product SLOs when available. Otherwise, label budgets provisional.

## 4. Experiment

Rank hypotheses by evidence. Change one mechanism at a time within the selected mode. Preserve the baseline and rollback. Include construction, updates, invalidation, memory and crossover costs. Report deeper opportunities without escalating.

Before Mode 3 implementation, write the architecture experiment brief required by modes.md. Use quick screening first. Retain supported winners. Record rejected and inconclusive attempts.

## 5. Validate

Follow the changed layer's correctness, sustained and fault requirements. In Modes 1 and 2, run at least three interleaved baseline and candidate pairs. In Mode 3, run at least five pairs. Follow the mandatory holds, soak and representative workloads in the validation ladder. Short pairs do not replace sustained validation.

Report every trial, paired effects, variation, resources and results for each route. Never average percentiles. Never cherry-pick trials. Never hide rare-route failures. Label incomplete performance evidence UNVERIFIED. Never claim universal success. Never transfer another implementation's score to the target.

## Deliver

State the mode, context, bottleneck, changes, checks, unrun checks, results, uncertainty, tradeoffs, remaining limit and rollback. Record lessons in the project journal with the catalog template. During project runs, never modify the installed skill.

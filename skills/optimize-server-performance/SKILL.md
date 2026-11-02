---
name: optimize-server-performance
description: Profile and improve backend, HTTP server, database, networking and application algorithm performance through controlled experiments and correctness checks. Use for slow APIs, high p95/p99, low throughput, excessive CPU/memory, SQLite/WAL contention, many connections or $12 Server Challenge submissions. Supports Tune, Optimize and Rebuild change budgets. Default to Mode 1.
---

# Optimize Server Performance

Default to Mode 1 for unspecified requests, including “make it faster.” State mode and production/challenge context. Never silently escalate, including subtasks. A mode is a ceiling, not a rewrite requirement. Narrower user constraints prevail.

| Mode | Allowed changes | Preserve |
|---|---|---|
| **1 Tune** | Remove redundant work/copies; reuse resources; tune existing queries/pools | Algorithms, data representation, architecture and stack |
| **2 Optimize** | Tune plus application algorithms, structures, layout, batching/concurrency | Language, framework, DB engine/schema/indexes, library feature architecture, transport/runtime/kernel and native dependencies |
| **3 Rebuild** | Any justified architectural layer, including storage, transport, libraries or language | Required behavior, security, durability, compatibility and operational responsibilities |

Mode 3 permits reversible local experiments. It does not independently authorize destructive migrations, live deployment or machine-wide changes. Replace a removed component's responsibilities. No mode requires a rewrite or permits weaker contracts.

## 1. Inspect

Read applicable AGENTS.md, git status, manifests, hot paths, tests and previous performance records. Confirm the actual target; a reference repository is not the application. Identify workload, sizes/skew, resource limits and required semantics, including isolation, validation, ordering, freshness, acknowledged writes and proxy/TLS duties.

## 2. Load the required guidance

Before planning edits, read [modes.md](references/modes.md): “Selecting a mode,” the selected mode's section, all explicitly inherited requirements, and “Validation ladder.” Read relevant [measurement](references/measurement.md) sections and [technique](references/technique-catalog.md) entries, including its project journal template. These readings are mandatory.

Load matching [playbook](references/optimization-playbook.md) sections and [case studies](references/case-studies.md) when useful. For contest/latest work, read [challenge research](references/challenge-research.md), including refresh instructions; query only relevant [catalog](references/submission-catalog.json) entries. Keep historical, official, local and projected evidence separate.

## 3. Establish evidence

Run correctness checks and baseline load on disposable authorized data before edits. Profile the limiting resource; inspect query plans/counts where relevant. Record source/environment/dataset provenance and generator health. Freeze primary metric, minimum effect and provisional regression/resource budgets before candidate measurements; use actual product SLOs when available.

## 4. Experiment

Rank evidence-backed hypotheses. Change one mechanism at a time within budget; preserve baseline and rollback. Include construction, updates, invalidation, memory and crossover costs. Report deeper opportunities without escalating. For Mode 3, write the architecture experiment brief required by modes.md before implementation. Screen quickly; retain supported winners and record rejected/inconclusive attempts.

## 5. Validate

Follow the changed layer's correctness, sustained and fault requirements. Require at least three interleaved baseline/candidate pairs in Modes 1/2, five in Mode 3, plus the mandatory holds/soak and representative regimes in the validation ladder. Short pairs do not replace sustained validation.

Report every trial, paired effects/variation, resources and per-route outcomes. Never average percentiles, cherry-pick or hide rare-route failures. Incomplete performance evidence is UNVERIFIED. Never claim universal success or transfer another implementation's score to the target.

## Deliver

State mode/context, bottleneck, changes, checks/unrun checks, results/noise, tradeoffs, remaining limit and rollback. Record lessons in the project journal using the catalog template; never modify the installed skill during project runs.

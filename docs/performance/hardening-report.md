# Skill hardening evidence

## Baseline before edits

Revision `9c854e1b0f43403aa09035140d6554cb4408b0f3`, branch `main`, clean
working tree. No applicable AGENTS.md was found at the repository or ancestor
paths, or within the repository. Work continues on local `skill-hardening`.
The baseline [counts and hashes](hardening-baseline.json) use `len(text.split())`,
equivalent to whitespace-delimited word counts. Body excludes YAML frontmatter
with `split('---', 2)[2]`; description counts characters after `description: `.
SKILL.md: 974 total words, 905 body words, 509 description characters.
All 9 existing tests passed; [actual output](baseline-tests.txt).

## Regression contract

These are document invariants, not evidence of agent compliance. Baseline
locations refer to the pinned revision and its section headings:

- Default Mode 1: SKILL.md / Select the change budget; modes.md / Selecting a mode.
- No silent escalation, including subtasks: SKILL.md / Select the change budget.
- Ceiling, not rewrite requirement: SKILL.md / Select the change budget.
- Narrower constraints prevail: SKILL.md / Select the change budget; modes.md / Selecting a mode.
- Mode 3 preserves behavior/security/durability/compatibility/operations:
  SKILL.md opening and Inspect the actual project; modes.md / Mode 3.
- Mode 3 is not destructive migration/deployment/machine-wide authorization:
  SKILL.md / Select the change budget; modes.md / Mode 3.
- Baseline and acceptance before candidate measurements: SKILL.md / Establish
  the baseline; modes.md / Validation ladder.
- Three interleaved pairs in 1/2, five in 3: SKILL.md / Prove the result;
  modes.md / Validation ladder; measurement.md / Reproducible comparison.
- Validation follows the changed layer, sustained/fault checks: same locations.
- No averaged percentiles, cherry-picking or hidden rare-route failures:
  SKILL.md / Prove the result; measurement.md / Reproducible comparison.
- Incomplete performance is UNVERIFIED: SKILL.md / Deliver; modes.md / Validation ladder.
- No universal success or transferred score: SKILL.md opening and Prove the result;
  technique-catalog.md / Read evidence before applying a technique.
- Project journal, no installed-skill mutation: SKILL.md / Prove the result;
  technique-catalog.md / Project-owned technique journal.

## Implementation plan and scope

1. Prepare task prompts, isolated A/B/C staging, rubric and blank results before
   revising the skill. No agent evaluations will run.
2. Shorten SKILL.md to a 500-word body budget, route mandatory safeguards through
   explicit mode and validation reading, append clarifications without changing
   historical evidence. Add document regression tests.
3. Add one stdlib HTTP/SQLite fixture, independent correctness tests and a small
   paired runner. Freeze metrics/budgets before measurements; profile baseline.
4. Run one-mechanism Tune and Optimize experiments, screening before holds.
   Investigate Mode 3 from the remaining profile and write its brief before any
   architecture implementation. Retain rejected and inconclusive results.
5. Record all raw trials and journal entries, minimally link from README, run
   unit tests, inspect scope and protected hashes, make focused local commits.

Reach: SKILL.md, selected existing references, new evals/, examples/slow-api/,
tests/, this evidence record and README. No new dependency, installation, push,
publication or globally installed skill change. Public API behavior and existing
k6 checker remain intact. Databases stay in temporary directories.

## Final invariant locations

All paths below are within `skills/optimize-server-performance/`.
Mandatory reading is enforced in SKILL.md / 2. Load the required guidance:
mode selection, selected mode, explicit inheritance and Validation ladder;
relevant measurement/technique sections and the journal template. This is
document reachability, not a behavioral compliance result.

- Default Mode 1: SKILL.md opening; references/modes.md / Selecting a mode.
- No silent escalation, including subtasks: SKILL.md opening.
- Mode is a ceiling: SKILL.md opening and paragraph after mode table.
- Narrower constraints prevail: SKILL.md opening; modes.md / Selecting a mode.
- Mode 3 behavior/security/durability/compatibility/operations: SKILL.md mode
  table and following paragraph; modes.md / Mode 3.
- No destructive migration/deployment/machine-wide authorization: same paragraph;
  modes.md / Mode 3 retains isolated reversible-experiment scope.
- Baseline before edits and acceptance before candidate measurement: SKILL.md / 3.
  Establish evidence; modes.md / Validation ladder.
- Three pairs in Modes 1/2, five in Mode 3: SKILL.md / 5. Validate; mandatory
  modes.md / Validation ladder; measurement.md / Reproducible comparison.
- Changed-layer sustained/fault validation: same sections; measurement.md /
  Required acceptance by changed behavior. Mode 3 inherits correctness/evidence
  duties from Modes 1/2, not their architecture ceilings; Mode 2 explicitly
  inherits Mode 1 semantics/ownership/freshness/security requirements.
- No averaged percentiles/cherry-picking/hidden rare-route failures: SKILL.md / 5.
  Validate; measurement.md / Reproducible comparison.
- Incomplete evidence UNVERIFIED: SKILL.md / 5. Validate; modes.md / Validation ladder.
- No universal success or transferred score: SKILL.md / 5. Validate;
  technique-catalog.md / Read evidence before applying a technique.
- Project journal, no installed-skill mutation: SKILL.md / Deliver; mandatory
  technique-catalog.md / Project-owned technique journal and its template.

Contest refresh detail now lives in challenge-research.md / Refresh procedure.
SQLite WAL/NORMAL power-loss limitations already remain in measurement.md /
Challenge protocol snapshot, challenge-research.md / Current rule rulings,
and optimization-playbook.md / SQL and SQLite. The old main-body warning is
covered by the retained durability contract and relevant mandatory readings.
Extended fault/validation detail stays in the mandatory ladder and measurement
sections. Historical snapshots and protected files were not rewritten.

## Counts and packaging

Counting method remains whitespace-delimited `len(text.split())`; frontmatter
body split is defined above. SKILL.md total: 974 -> 529 words. Body: 905 -> 476.
Description: 509 -> 374 characters. The explicit upper body budget is 500 words,
with no minimum and no exception. Length and document tests are not quality or
behavioral evidence. Reference counts before -> after:

- case-studies.md: 2075 -> 2075.
- challenge-research.md: 1287 -> 1360.
- measurement.md: 634 -> 669.
- modes.md: 1367 -> 1408.
- optimization-playbook.md: 1030 -> 1030.
- submission-catalog.json: 5842 -> 5842.
- technique-catalog.md: 1851 -> 1851.
- upstream-license.txt: 172 -> 172.

The protected license/catalog and unchanged historical case studies, playbook
and technique catalog match baseline SHA-256 values. Existing dates, scores and
SHAs remain in the three references receiving additive instructions as well.
Only one skill folder exists; installation and Claude Code support remain.

## Application outcomes and attribution

Complete [journal](../../examples/slow-api/journal.md), including every trial,
paired effects/variation, checks, tradeoffs and rejection rationale. The
[derived JSON summary](../../examples/slow-api/results/summary.json) and raw
artifacts retain all measurements and provenance.

- Mode 1: longer paired CPU reductions +4.57%, +6.84%, +9.90%; median +6.84%,
  baseline relative range 11.21%. Inconclusive under the frozen >8% and
  above-variation gate. No accepted gain. Gain UNVERIFIED.
- Incremental Mode 2: predecessor is original, since Tune was not accepted.
  Longer reductions -2.88%, +11.38%, +1.39%; median +1.39%, baseline relative
  range 5.64%. Inconclusive, no accepted gain. Gain UNVERIFIED.
- Mode 3: predecessor is original, since neither earlier candidate was accepted.
  Persistent index only. Five-pair median CPU reductions: light +30.68%, target
  +30.94%, 100000-row skew +63.28%, tiny -1.58%, four-worker pressure -12.00%.
  The pressure screen has worse throughput in every pair and breaches the tail
  budget. Rejected after screening. Promising gains remain UNVERIFIED because
  the full finalist validation was not run.
- Original -> final: final retained source is original baseline.py. No accepted
  performance change or compounded gain exists. Mode 3 observations are not
  attributed to Mode 1/2 or advertised as final application speedups.

All application performance trials completed without observed HTTP, timeout or
semantic failures. Tests separately exercise recorded HTTP failures and actual
client timeouts. The first two artifacts have a superseded paced-throughput
denominator and remain visible. Later artifact summaries use the full window
plus drain. No per-run percentiles were averaged.

Environment: CPython 3.14.4, SQLite 3.46.1, Linux 7.0.0-42 x86_64, i5-1235U,
12 visible/affinity logical CPUs, 16088348 kB reported RAM. CPU quota and cgroup
memory/swap limits are unknown. Server and generator share the host. Loopback
read-only results are neither challenge scores nor open-loop capacity proof.
The index adds 151552 bytes at 12000 rows and 1249280 at 100000 rows; SQLite
maintains it on external writes. Write-maintenance performance was not measured.
Golden/differential, external write/rollback, concurrent reads, setup failures,
SQLITE_FULL, integrity, error recovery and rollback checks passed. Remaining
baseline cost is read/sort work, encoding and membership; pressure contention
needs profiling. No sync or required behavior was weakened.

Five-minute holds and fifteen-minute finalist soak were **not run**: no candidate
survived all screening gates, so the ladder did not select a finalist. Those
jobs remain reproducible through the runner; ordinary CI runs no sustained
benchmarks or speed assertions. Recovery checks were functional, not a measured
recovery-time SLO. Power-loss/custom-transport suites were not run, as no such
responsibility changed. No accepted gain is asserted from incomplete evidence.

## Agent evaluation preparation and limits

[evaluation instructions](../../evals/README.md) define five scenarios, including
Mode 3 initiative/restraint strata; identical fresh A/B/C trials; trace/artifact
rubrics; repeat-agent-trial requirements; and an empty results template.
A gets no skill, B gets baseline 9c854e1, C gets an explicitly pinned revised
commit. The preparer copies only baseline application inputs into task/ and
keeps guide bundles, trusted fixtures, hidden correctness oracle and manifests
in evaluator control/. No target candidates, results, journal or git history
are copied into task/.

Staging A/B/C and the external hidden baseline oracle were actually exercised;
the two hidden tests passed. Contamination tests check a clean isolated-tree
fixture and fail on an injected copy. The actual fresh VM/container mount audit
and CLI startup context inspection remain prerequisites for future evaluations;
no fully isolated CLI session was launched here. **Do not run condition A in
this host checkout or assume that HOME redirection isolates it.** The protocol
requires that installed/repository/plugin copies cannot be discovered or read,
with a fail-closed preflight and external mount/context inspection.

Local installed versions and help were inspected: Codex 0.163.0, Claude Code
2.1.251. The complete command prefixes parse with --help; an initial misplaced
Codex global approval flag was rejected and corrected before exec. No model,
authentication, full evaluation invocation or repeated agent trial ran. Actual
results remain blank and behavioral improvement remains **unmeasured**.

## Changed files and reasons

- SKILL.md: 476-word entrypoint with mode table, five steps, evidence boundaries,
  delivery format and mandatory conditional reference loading.
- references/modes.md: explicit inheritance; measurement.md: changed-layer
  routing; challenge-research.md: separately labeled refresh procedure. Other
  references, protected files and UI metadata are preserved.
- tests/test_hardening.py: install arguments, 500-word budget, description,
  mandatory reading, invariant text, protected history and blank agent results.
  These are document/package regression checks, not agent behavior evidence.
- evals/README.md, prompts.json, results-template.json, prepare.py and audit.py:
  repeatable isolated study preparation. tests/test_evals.py checks package
  contents and contamination rejection without calling a model.
- examples/slow-api/app.py and data.py: loopback server, owned transactional
  SQLite reads and deterministic data. Four separate candidate modules preserve
  the original and each experiment. protocol.json freezes budgets; mode3-brief.md
  records architectural reasoning before implementation.
- examples/slow-api/bench.py and profile_app.py: compact stdlib paired measurement
  and diagnostic commands. README.md, journal.md, raw JSON and summary.json keep
  reproduction, failures/inconclusive decisions and all observed values.
- tests/test_slow_api.py, test_benchmark.py and test_index.py: independent oracle,
  golden/API semantics, failure accounting, artifact smoke, storage faults and
  rollback. No performance acceptance assertion enters CI.
- .github/workflows/validate.yml: fetch repository history so pinned-baseline
  extraction works in CI's otherwise shallow checkout. Hosted CI was not run.
- Root README.md: small example/evaluation links and requested stack scope;
  installation blocks and visual style retained.
- docs/performance/: baseline/final counts, hashes, actual test logs and this
  invariant/change/result report.

## Commands and verification

Baseline: `git status --short`, `git rev-parse HEAD`, branch/remotes/log inspection,
ancestor/repository AGENTS.md search, `python3 -m unittest discover -s tests -v`.
Baseline output is preserved verbatim. New document checks were run before the
revision and failed on the old body budget/wording, then passed on the revision;
these failures were document checks, not model behavioral failures.

Application commands are stored literally in each raw JSON `command` field.
They include baseline-only controls; three 2-second and three 10-second pairs
for Modes 1/2; five Mode 3 pairs per regime/size; one-pair concurrency probes;
and profiling commands. Profiles record actual plans and call times.
Reproduce through the example README and use new output paths.

CLI verification: `codex --version`, `codex --help`, `codex exec --help`,
`claude --version`, `claude --help`, and documented full prefixes ending in
`--help`. These calls never launch model evaluations. Staging was exercised
through prepare.py for A/B/C and the resulting external hidden oracle.

The first local socket test was blocked by the filesystem/network sandbox;
rerunning with loopback permission passed. A later combined packaging smoke
command hit an automatic approval-review deadline. Staging succeeded separately
without escalation; the one retry of the two-test loopback oracle passed. This
was a review timeout, not a finding that the action was unsafe.

Final required command and its actual output are in [final-tests.txt](final-tests.txt).
`git diff --check` passes. The final diff was inspected for scope, historical
preservation, readability and unwanted databases/dependencies. No global install,
model evaluation, push, publication or deployment occurred.

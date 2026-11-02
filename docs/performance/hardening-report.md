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

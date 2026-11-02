# Instruction and review notes

This revision uses direct commands, shorter sentences and consistent terms.
The mode table separates permissions from required boundaries. Conditional
reading distinguishes mandatory guidance from optional examples.

Counts use `len(text.split())`. Body counts exclude YAML frontmatter with
`split('---', 2)[2]`. The previous entrypoint had 529 total words, 476 body words
and a 374-character description. The revision has 613 total words and 560 body
words. The description remains unchanged. The 500-word body target is editorial.
The reviewed upper budget is now 575 words, with no minimum. The 60-word overrun
expands ambiguous shorthand and states architectural inheritance explicitly.
Length and document checks do not establish instruction quality or agent behavior.

## Invariant check

Locations refer to [SKILL.md](../skills/optimize-server-performance/SKILL.md).
No safeguard moved to optional reading.

- Opening: default Mode 1; no silent escalation, including subtasks; mode ceilings;
  narrower user constraints; no required rewrite.
- Table and following paragraph: Mode 3 architectural freedom; no lower-mode
  architectural restrictions; required behavior, security, durability,
  compatibility and operational responsibilities; no independent authority for
  destructive migration, deployment or machine-wide changes.
- Step 3: baseline measurements and correctness before experiments; frozen
  primary metric, minimum effect and regression and resource budgets; real SLOs or
  explicitly provisional budgets.
- Step 5: three interleaved pairs in Modes 1 and 2, five in Mode 3; changed-layer
  correctness, sustained and fault checks; no averaged percentiles, cherry-picked
  trials or hidden rare-route failures; incomplete evidence UNVERIFIED; no
  universal success or transferred score.
- Deliver: project-owned lessons and no installed-skill modification.

Step 2 requires modes.md / Selecting a mode, the selected section, explicitly
inherited requirements and Validation ladder. It also requires relevant
measurement sections, technique entries and the journal template. The mandatory
ladder retains Mode 3 interleaving, representative regimes, five-minute holds
and the fifteen-minute finalist soak. The selected mode supplies its inheritance
rules. Other references are conditional on the actual task.

## Review corrections

The runner reports server-owned RSS observations. It does not certify a true
peak-memory gate. Historical ru_maxrss conclusions are unreliable. Missing draft
source cannot be recovered from a hash; unrelated CPU and latency data are not
automatically invalidated. See the example's [results](../examples/slow-api/RESULTS.md)
and [evidence manifest](../examples/slow-api/evidence.json).

Evaluation preparation now creates one sanitized Git commit. Grading requires
an explicit selected module and executes setup plus HTTP checks. This was tested
without a model. Model-based evaluations have not run. Agent behavioral
improvement remains unmeasured.

Verbose evidence is preserved locally outside the repository. It is unpublished,
so the public source tree does not provide independent access to the raw trials.
Untracking those files does not remove them from previous commits. Historical
reference files and protected upstream content were not rewritten.

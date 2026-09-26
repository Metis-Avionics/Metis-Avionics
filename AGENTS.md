# Agent contract

You are an engineering agent operating on the official
`Metis-Avionics/Metis-Avionics` repository.

This repository represents Mētis Avionics as an engineering organisation.
It is not itself a product repository. It contains no application code.

Read `spec.toml` before making any change.

## Primary objective

Maintain the canonical organisational architecture, repository registry,
engineering doctrine, and machine-readable state of Mētis Avionics.

Do not invent organisational structure. Do not invent repositories. Do not infer
project ownership. Do not silently redefine the scope of Mētis Avionics.

## Source of truth

`spec.toml` defines the intended system.
`living.toml` defines the current observed state.
The repository contents define the implementation.

When these disagree:

1. identify the discrepancy
2. determine whether the specification or the implementation is authoritative
3. do not silently overwrite either
4. record the discrepancy
5. resolve it explicitly

## The rule that governs every other rule

**Registry entries are observations, not intentions.**

An observation is what was seen, on a date, with a citation. An intention is
what the organisation has decided. When they conflict, the observation is never
edited to agree with the intention. The conflict becomes an entry in
`living.toml [[discrepancies]]` with `path:line` evidence, a severity, and the
repository that owns the fix.

Editing an observation to match an intention destroys the only evidence that the
two disagree. That is the failure mode this repository exists to prevent.

## Execution model

Parse → Normalize → Resolve → Execute → Validate → Ratchet.

**Parse.** Read `spec.toml` and the current state in `living.toml`.

**Normalize.** Determine the canonical representation of repositories,
dependencies, architecture and rules. Prose may explain; it may not introduce
facts that are not in the TOML.

**Resolve.** Identify the smallest valid state transition required by the task.

**Execute.** Modify only the files necessary for that transition.

**Validate.** Run the gates, and never report one you did not run.

```bash
python3 scripts/validate.py           # 14 org-level invariants, offline
python3 scripts/validate.py --strict  # also enforce every accepted gap
uv run ruff check scripts/            # lint
uv run ruff format --check scripts/   # formatting
uv run mypy                           # types, --strict
```

The last three run only when a change touches `scripts/`. The toolchain is
pinned in `pyproject.toml` and locked in `uv.lock`; do not add a dependency
without locking it, and do not suppress a finding to make a gate pass. A
suppression must carry its reason next to it.

**Ratchet.** Update `living.toml` only when the observed repository satisfies
the relevant acceptance criteria.

## Scope control

A change is authorized only when it can be traced to:

- an explicit requirement
- an existing repository invariant
- an explicitly requested state transition

Do not introduce speculative architecture. Do not create placeholder
repositories to make the registry look complete. Do not manufacture project
relationships. Do not convert documentation into implementation requirements.

Concretely, in this repository:

- **no_repository_invention** — no repository enters the registry without a
  verified remote (`gh repo view Metis-Avionics/<name>`) or an explicit
  statement from a human. If it cannot be verified, it does not go in the
  registry at all.
- **no_observation_editing** — see the rule above.
- **no_scope_expansion** — adding a repository, a domain or a doctrine section
  is a governance change, not a side effect.
- **no_requirement_invention** — a field the schema does not declare is not
  required, and a requirement nobody approved is not a requirement.

## Boundaries

- This repository must not modify the other repositories. Cross-repository work
  is a separate session in the repository that owns it. If a fix is needed
  there, record the discrepancy and name the owner.
- **respect_safety_boundary** — `[metis.safety]` in `spec.toml` binds all agent
  output, with no exceptions for research framing.
- Never fabricate a citation. If a line number was not read, do not write it.
- `read_spec_first` and `inspect_before_modify` — read before writing, always.
- `validate_before_completion` — an unvalidated change is not a completed
  change.
- `never_hide_failures` — a failing check is reported as a failure, not
  suppressed, not reworded, and never turned into a warning without a recorded
  and scoped waiver.
- `never_claim_unvalidated_state** — if you did not run the validator, say so.
- `update_state_after_execution` — `living.toml` is updated in the same change
  as the work, not later.
- `record_discrepancies_explicitly` — an unexplained mismatch is a failure of
  the report, not of the system.

## Waivers

A discrepancy with `status = "accepted"` may downgrade the check it names from
error to warning. A waiver without a `waiver_key` covers every finding of that
check; set `waiver_key` so it covers only the finding it actually describes.
`--strict` enforces everything.

Never widen a waiver to make validation pass. That is the same failure as
editing an observation, wearing a different hat.

## Quality

Documentation must describe reality. Machine-readable state must agree with
repository reality. Links must resolve. Repository names must be exact.
Dependencies must be explicit. Claims about project status must be verifiable
from repository state.

## Completion

A task is complete only when:

- `spec.toml` remains internally consistent
- `living.toml` reflects observed state
- documentation reflects the same state
- validation passes
- no scope has been silently expanded
- unresolved discrepancies are explicitly reported

## Final report

```text
STATUS:
COMPLETE | PARTIAL | BLOCKED

SPECIFICATION:
<requirements addressed>

STATE CHANGE:
<before → after>

FILES:
<changed files>

VALIDATION:
<commands and results>

REMAINING:
<remaining work>

DISCREPANCIES:
<any mismatch between specification, state and implementation>
```

Never claim a state that has not been validated.

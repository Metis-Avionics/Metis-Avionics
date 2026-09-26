# Governance

## What governs what

| Artefact | Authority | Changes when |
|---|---|---|
| `spec.toml` | highest | Doctrine changes, or a re-observation changes what is recorded |
| `living.toml` | observed state | Every session, every observation, every discrepancy |
| `docs/*.md` | projection | Only to match `spec.toml` |
| `AGENTS.md` | executable prompt | When the agent contract changes |
| The six member repositories | reality | In sessions held there, never from here |

`spec_version` in `spec.toml` is the constitution's own version. It increments
on any change to identity, safety, scope, doctrine, governance or agent rules.
A registry-only correction does not increment it; it updates
`[repositories.observed].observed_at` and the entry.

## Change classes

**Doctrine.** A change to `spec.toml` outside the registry — identity, safety,
scope, non-goals, engineering, governance, agent rules. Requires a `CHANGELOG.md`
entry with a rationale, a `spec_version` increment, and a note in
`living.toml [handover].changed`.

**Registry.** A change to `repositories.registry`, `repositories.related`,
`repositories.publications` or `repositories.excluded`. Requires re-observation
evidence, never invention. Hand-editing an observation to make it true is
prohibited; the mechanism for recording a change in reality is a discrepancy,
not an edit.

**Discrepancy.** An entry in `living.toml [[discrepancies]]`. The only
permitted way to record a mismatch between specification, state and
implementation. Carries evidence, severity, an owning repository, and what a
resolution would look like. Never deleted to make a report cleaner — closed by
changing `status` to `resolved` with a pointer to the fixing commit.

## The discrepancy protocol

When a discrepancy is found:

1. **Record it** in `living.toml` with `path:line` or command evidence. An
   observation without evidence is an opinion and `check C11` rejects it.
2. **Classify the severity.** `high` when it affects supply chain, licensing,
   reproducibility or whether a build can succeed at all. `medium` when it
   contradicts doctrine or leaves a control unenforced. `low` when it is drift
   with no operational consequence.
3. **Name the owner.** The repository whose session must fix it. Almost never
   this one.
4. **Decide whether it is a waiver.** If the gap is real and consciously
   tolerated, set `status = "accepted"` and name the `check` it downgrades, with
   a `waiver_key` narrowing the waiver to the finding it actually covers. If the
   gap should fail the build, leave it `open` and let validation fail.
5. **Do not fix it here.** A fix belongs to the owning repository. This
   repository records, names, and hands off.

Nineteen discrepancies are registered. Five are high, six medium, eight low.
Eleven are open. Five carry an active waiver — D5, D7, D8, D9, D17 — and every
one is scoped to a message so that no waiver conceals an unrelated finding.
D8 and D9 both waive check C13 and are kept apart by their `waiver_key`: one
covers "no continuous integration", the other "no living state". A single
unscoped waiver there would have hidden all five automation findings behind the
one that was consciously tolerated.

## Requirements on member repositories

`governance.repository_requirements` declares what every organisation repository
must have: a licence, CI, a specification file, living state, an agent contract,
and TETANUS rules where the code is safety-critical.

**None of these are met by all six member repositories.** That is the honest state, and
it is why `check C13` exists and why the gaps below are named explicitly. Four
of them are waived, with the requirement left stated as the target so that
`--strict` enforces it on demand:

- `seven`, `theLiGI` — no CI (D8)
- `theMQL`, `theDAF`, `theLiGI` — no living state (D9)
- `theSix`, `theDAF` — no specification file (D7)
- `theDAF` — no `AGENTS.md` (D14)
- `economic-prv`, `seven` — no `LICENSE` file (D5)

An unmet requirement is a discrepancy, not a reason to lower the requirement.
If a requirement is genuinely wrong, amend it in `spec.toml` with a rationale
and let the affected entries be re-evaluated — do not leave both claiming
authority, which is exactly the state D6 records for the `status` field.

## Dependency policy

`governance.dependencies` is binding on new work:

- `cross_repository_dependencies_must_be_explicit` — every edge is recorded in
  the registry with a source citation.
- `prefer_crates_io_over_fork` — consume the organisation's published packages.
  Reference implementation: `seven/specs/decisions/0003-themql-sourcing.md`.
- `forks_must_be_declared` — a fork is a legitimate choice, recorded as a
  `related` entry with a `relationship` kind, never left implicit in a
  `Cargo.toml`.
- `revisions_must_be_pinned` and `unpinned_git_dependencies_prohibited` — a git
  dependency without a revision is not reproducible.
- Pin primitives exactly. `seven` does (`=0.2.3`); `economic-prv` does not (D11).

TheLiGI's fork pin at `37d54d7` satisfies the letter of this policy — it is
pinned and declared — while violating its intent, because theDAF publishes all
nine of the same crates at 0.1.0 (D4). The policy exists to catch exactly this,
so it is recorded as high severity rather than waved away.

## Safety

`[metis.safety]` in `spec.toml` binds every agent, document and publication in
the organisation. It is adopted verbatim from `seven/README.md:8-11` and applies
to all six member repositories and all agent output. An agent that produces output
violating it has failed regardless of what the validation says.

## Adding a repository to the registry

1. Confirm the remote exists and belongs to the organisation. `gh repo view
   Metis-Avionics/<name>`. No entry without a verified remote or an explicit
   statement from a human.
2. Observe it: language, default branch, visibility, licence, specification
   file, living state, CI, published packages.
3. Record only what was observed. If a field could not be observed, record it as
   unknown rather than inferred.
4. Record cross-repository edges with the file and line that asserts them.
5. If the repository belongs to another organisation, it goes in
   `repositories.related` with a `relationship` kind — never in the registry.

## Changing this repository

1. Read `spec.toml` before changing anything.
2. Run `python3 scripts/validate.py` before and after.
3. Update `living.toml` in the same change: what you observed, what you changed,
   what you validated, what remains.
4. Add a `CHANGELOG.md` entry for any doctrine or registry change.
5. Never claim a state you have not validated. `PARTIAL` and `BLOCKED` are
   legitimate results; a false `COMPLETE` is not.

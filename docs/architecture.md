# Architecture

This repository is the control plane. It contains no application code, no
subsystem, and no vendored copy of anything. It exists so that one question has
one authoritative answer:

> What is Mētis Avionics, what exists, how do the pieces relate, what are the
> rules, and what is the current state?

## Layers

```text
                     ┌─────────────────────────────────────────┐
   intent  ─────────▶│  spec.toml                             │
                     │  identity · safety · scope · doctrine  │
                     │  governance · agent rules · registry   │
                     └────────────────────┬────────────────────┘
                                          │  authority: highest
                     ┌────────────────────▼────────────────────┐
   state    ─────────▶│  living.toml                           │
                     │  observed status · discrepancies       │
                     │  remaining work · evidence              │
                     └────────────────────┬────────────────────┘
                                          │  projection
                     ┌────────────────────▼────────────────────┐
   humans   ─────────▶│  docs/*.md · README.md · AGENTS.md     │
                     └────────────────────┬────────────────────┘
                                          │  validated by
                     ┌────────────────────▼────────────────────┐
   check    ─────────▶│  scripts/validate.py + CI              │
                     │  schemas/repository.schema.toml         │
                     └─────────────────────────────────────────┘

                     ┌─────────────────────────────────────────┐
   reality  ────────▶│  the six member repositories           │
                     │  (observed, never owned by this repo)   │
                     └─────────────────────────────────────────┘
```

The two-way arrow at the bottom is the whole point. Reality flows up as
observations; intent never flows down as edits to other repositories.

## Authority order

1. **`spec.toml`** — the constitution. Intended structure, doctrine, and the
   registry of what was observed. If it conflicts with anything below, it wins,
   and the conflict becomes a discrepancy.
2. **`living.toml`** — what is true now, with `path:line` evidence, plus the
   complete list of known disagreements.
3. **`docs/*.md`, `README.md`, `AGENTS.md`** — projections for humans and agents.
   Prose may explain; it may not introduce facts.
4. **The other repositories** — reality. Never edited from here.

## The registry is an observation, not an intention

This is the distinction the whole design turns on.

An **intention** is what the organisation has decided: "theLiGI depends on
theDAF." An **observation** is what was seen on a date: "theLiGI's
`Cargo.toml:79-84` pins six `daf-*` crates to a fork at revision `37d54d7`,
while theDAF publishes all nine of its crates at 0.1.0."

The registry stores observations, each stamped with `observed_at` and the means
of verification. When an observation contradicts an intention, the correct move
is to record a discrepancy (`D4` in this case), not to edit the observation until
it agrees with the intention. Editing an observation destroys the only evidence
that the two disagree.

Consequences that follow from this rule:

- Every registry entry carries a `source` — a file path, a line number, or a
  command whose output was checked.
- Three of the six member repositories are not cloned on the observation host.
  Their
  entries say `not cloned` rather than guessing at local state.
- `observed_at` plus `stale_after_days` (30) means the registry expires. Check
  C10 fails validation once the data is older than the window, because a stale
  registry that looks authoritative is worse than no registry.

## State flow

`spec.toml` says what should be. `living.toml` says what is. A change lands in
this order:

1. An observation is made and written to `living.toml` with evidence.
2. If it contradicts the spec, a discrepancy is registered. Both readings stand.
3. A human decides which is authoritative — usually by fixing the repository
   that owns the defect, in a session in that repository.
4. The spec is updated only if the *intent* genuinely changed. If only reality
   was wrong, the spec does not move and the discrepancy closes on the strength
   of the repository's own commit.

`ratchet.remaining_work_only_decreases` and `ratchet.observations_never_edited_to_match_intent`
encode steps 3 and 2 as machine-checkable policy.

## Why TOML is the memory

Markdown is comfortable to write and terrible to diff, so it drifts. A
specification that lives in prose cannot be validated, and a specification that
cannot be validated is an opinion. Hence the pattern the organisation already
uses in `economic-prv` and `seven`: **the TOML is the memory, the Markdown is a
generated projection.** `prv-cli living update` renders `living.toml` into
`docs/living.md`; this repository achieves the same guarantee more cheaply, by
validating that the projection still matches (`check C7`) instead of generating
it.

## Validation

`scripts/validate.py` enforces 14 invariants offline, with no network access
and no access to any other repository. It exists because documentation drifts
silently, and a control plane whose own documentation has drifted has no
authority to complain about anyone else's.

| Check | Enforces |
|---|---|
| C1 | `spec.toml` matches the shape the schema declares |
| C2 | every registry entry carries its required keys, types, enums, patterns |
| C3 | `full_name` agrees with the organisation and the entry name |
| C4 | no duplicate entries across registry and related list |
| C5 | specification filename conforms to the org convention |
| C6 | every declared dependency resolves to a publication or a known repository |
| C7 | `docs/repositories.md` matches the registry, in order |
| C8 | relative links in README and docs resolve on disk |
| C9 | `AGENTS.md` documents every `[agent.rules]` key |
| C10 | observations are inside the staleness window |
| C11 | every discrepancy is well formed, evidenced, and uniquely identified |
| C12 | a declared licence is backed by an actual `LICENSE` file |
| C13 | repositories meet the automation `governance` requires of them |
| C14 | `[state]` points only at files that exist |

Waivers are narrow on purpose. A discrepancy may downgrade the check it names
from error to warning, but only findings whose message contains its
`waiver_key`. Without that narrowing, one accepted gap would silently mask every
other finding of the same check — which is how a validator becomes decorative.
`--strict` removes the waivers entirely.

## What this repository deliberately does not do

- It does not build, test, or release any of the six member repositories. It
  runs its own gates, and it holds itself to them.
- It does not enforce their quality gates. It records that a gate exists, and
  records its absence where `ci = "none"`.
- It does not fix discrepancies. It registers them, names the owning
  repository, and describes what a fix would look like.
- It does not infer relationships between projects. Every edge in the registry
  is one somebody asserted in a file, cited to the line.

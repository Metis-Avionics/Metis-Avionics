# HANDOVER

Entry point for whoever or whatever works on this repository next. Read
[`AGENTS.md`](AGENTS.md) first, then [`spec.toml`](spec.toml), then this.

## State

- **Phase:** constitution published and gated (`living.toml` → `handover.phase`)
- **Status:** published
- **Last updated:** 2026-09-26
- **Validation:** 0 errors, 11 warnings; every warning is a waived finding.
  `ruff check`, `ruff format --check` and `mypy --strict` are clean.
- **Registry:** 7 repositories, 2 related public forks, observed 2026-09-26, expires after 30 days
- **Open discrepancies:** 11 of 20; 5 carry scoped waivers
- **Open work:** R1, R2, R3, R4, R6. R5 is closed.

## What exists

A complete control plane: constitution, schema, living state, five
documentation pages, an agent contract, three state files, an offline validator,
a live registry observer, and three CI jobs over a pinned toolchain. No
application code, by design. It is the seventh repository in the registry and
registers itself like any other.

## What to do next, in order

1. **Get a decision on the copyright holder** (`R1`, blocking). The `LICENSE` is
   published and says `Copyright (c) 2026 Mētis Avionics`. If a natural person
   or legal entity must be named instead, that is a licence change, not a
   documentation fix.
2. **Re-observe the registry** (`R2`). Run on 2026-09-26 with
   `python3 scripts/observe_registry.py`: 7 repositories observed, no
   publication drift across all 32 packages, and no registry drift beyond the
   known D5 licence finding. Run it again before relying on the registry after
   2026-10-26, when the 30-day window expires.
3. **File the high-severity discrepancies** (`R3`) as issues in the repositories
   that own them:

   | Issue | Repository | Severity |
   |---|---|---|
   | D1, D2 — theMQL declared but unused; unpublished version specified | economic-prv | high |
   | D3 — `../theMQL` path dependencies cannot resolve | theLiGI | high |
   | D4 — fork pin bypasses nine published crates | theLiGI + theDAF | high |
   | D5 — MIT declared, no `LICENSE` file | economic-prv, seven | high |

5. **Decide about the founding statement** (`R6`). `docs/mission.md` is an
   adaptation of a statement that exists only at `~/Desktop/metis.md`, outside
   version control. Either commit the original here or record why it stays
   outside the organisation's repositories.

## What not to do

- Do not fix anything in the other repositories from here. Record and hand off.
- Do not edit a registry observation to make it agree with an intention. Add a
  discrepancy. This is the rule the whole repository turns on.
- Do not add a repository to the registry without a verified remote.
- Do not widen a waiver to make validation pass. Every waiver carries a
  `waiver_key` for exactly this reason.
- Do not rename the spec files in other repositories from here. D7 records the
  divergence; the migration, if any, is a decision for a session in each
  repository.

## Traps

- **`validate.py` is offline.** It never contacts GitHub or crates.io, so it
  cannot tell you that reality moved. Only `observe_registry.py` does that, and
  only when you run it. A green validation means internal consistency, not
  accuracy.
- **Waived ≠ fixed.** `--strict` re-raises every waived finding. Run it when you
  want to see the real debt rather than the accepted debt.
- **Twelve discrepancies are open and produce no validator finding at all.**
  Validation checks consistency, not the world. Read `living.toml`, not the
  exit code, to know the state of the organisation.
- **`docs/repositories.md` is checked against `spec.toml`, including row
  order** (C7). Reorder one and not the other and validation fails.

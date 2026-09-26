# CHANGELOG

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version tracks `spec_version` in [`spec.toml`](spec.toml) for doctrine changes.
Registry-only corrections update `[repositories.observed].observed_at` and the
affected entry without incrementing `spec_version`.

## [Unreleased]

### Added

- `pyproject.toml` and `uv.lock`: the toolchain, pinned. `ruff==0.16.9` and
  `mypy==2.3.1`, exact, with `ruff` and `mypy` configured for what these two
  programs are — a line length, a rule selection with every exclusion argued in
  the file itself, and `strict = true` types against the 3.11 floor that
  `tomllib` sets.
- A `gates` CI job running `ruff check`, `ruff format --check` and `mypy`, plus a
  hygiene check that fails if `uv.lock` is ever untracked. A lockfile that is not
  committed is a toolchain that silently drifts.
- `spec.toml [engineering.quality_gates.observed_gates]` now records this
  repository's own gates alongside the members'. An organisation that does not
  hold itself to its doctrine has no doctrine.

### Changed

- `scripts/validate.py` and `scripts/observe_registry.py` are fully typed and
  pass `mypy --strict`. Navigation of parsed TOML goes through `as_table` and
  `as_keys` rather than falling back to `Any`.
- C1 now reports a scalar where the schema declares a table, instead of passing
  it to `require_keys`.
- `.github/workflows/validate.yml`: `actions/checkout` and `actions/setup-python`
  moved from the `v4`/`v5` majors to `v7`, which target Node 24. The first CI
  run annotated both as Node 20 deprecations forced onto Node 24.
- `spec.toml [repositories.registry]`: added `Metis-Avionics/Metis-Avionics` as
  the seventh entry, after the remote was created. The observer reported its own
  absence from the registry on its first run after publication, and the entry was
  added in the same change that created the remote rather than later. Prose that
  meant the six members now says "six member repositories".
- `spec.toml [metis.identity].mission_provenance` no longer claims the mission is
  reproduced verbatim. It is an adaptation, and the original statement is not
  under version control (R6).

### Removed

- `observe_registry.py`'s `gh()` helper. It was never called: the fetcher does
  the work. Deleting it removed the `subprocess` import and the two bandit
  findings that came with it, rather than annotating them away.

### Removed

- Two entries from `spec.toml [repositories.related]`, and their rows and prose
  in `docs/repositories.md` and `docs/engineering.md`. Both named private
  repositories. See D20: the first two published revisions of this repository
  disclosed work that was never ours to publish, and the fix is not a redaction
  but a rule — a private repository is never recorded here, by name or by
  description, however relevant it is technically.

### Fixed

- `spec.toml [repositories.excluded]` states why a private repository is never
  entered, so the mistake is a rule now rather than only a correction.
- `CHANGELOG.md`: two counts in the 0.1.0 entry were wrong and are corrected —
  6 remaining-work items, not 5, and 5 check waivers, not 7.
- The `gates` job failed on its first run: `astral-sh/setup-uv@v10` does not
  resolve, because that action publishes patch tags but no floating major tag.
  It is now pinned to `v10.2.0`, verified against the GitHub API rather than
  assumed. The job that exists to catch drift caught a drifted assumption in the
  same commit that introduced it.
- `observe_registry.py` now refuses to open a non-https URL, and the one bandit
  suppression that remains is scoped to the two call sites with the reason
  written next to it.

## [0.1.0] — 2026-09-26

Initial constitution. Bootstrap — no prior state existed.

### Added

- `spec.toml`: organisation identity, mission reference, safety boundary, scope
  and non-goals, engineering doctrine, governance rules and change classes, the
  agent execution model, state map, and ratchet policy.
- `spec.toml [repositories]`: a registry of all six Metis-Avionics
  repositories, four related external repositories with typed relationships, the
  crates.io publication ledger (32 packages), and an explicit exclusion list.
  Every field carries its evidence.
- `schemas/repository.schema.toml`: the registry contract, enforced rather than
  decorative.
- `living.toml`: observed state, 19 discrepancies with `path:line` evidence, and
  6 remaining-work items (R1-R6).
- `docs/`: `mission.md`, `architecture.md`, `engineering.md`, `repositories.md`,
  `governance.md` — projections, with `repositories.md` machine-checked against
  the registry including row order.
- `AGENTS.md`: the agent contract, with `no_repository_invention`,
  `no_observation_editing`, cross-repository boundaries and scoped waivers added
  to the base prompt.
- `scripts/validate.py`: 14 offline invariants, `--strict`, `--quiet`, `--list`.
- `scripts/observe_registry.py`: re-observation against the live GitHub and
  crates.io APIs. Prints a diff; never writes, never commits.
- `.github/workflows/validate.yml`: CI running the validator.
- `.github/ISSUE_TEMPLATE/`: forms for registry, doctrine and new-repository
  changes.
- `SESSION.md`, `HANDOVER.md`, this file.

### Decisions

- `spec.toml`, lowercase, at the repository root, is the org convention — it
  matches the two most recently active repositories. `theMQL` and `theLiGI` use
  uppercase; `theSix` and `theDAF` have no specification. Recorded as D7, not
  enforced away.
- The registry covers the six organisation repositories; external repositories
  with real edges go in a typed `related` list rather than being mixed in.
- Waivers are scoped by `waiver_key`. A waiver without one covers every finding
  of its check, which would let a single accepted gap conceal unrelated debt.
- MIT, matching `theLiGI`, `theMQL`, `theSix` and `theDAF`.

### Recorded, not fixed

19 discrepancies, 5 high / 6 medium / 8 low; 11 open, 8 accepted, of which 5
downgrade a named check to a warning under a scoped `waiver_key`.
The five high-severity findings: a declared dependency absent from a build
graph, a specified crate version that was never published, unresolvable path
dependencies, a fork pin bypassing nine published crates, and two repositories
declaring MIT without a `LICENSE` file. None is fixed here; each names the
repository whose session must fix it.

### Published after this entry was written

`Metis-Avionics/Metis-Avionics` did not exist when the 0.1.0 entry was drafted,
and the draft said so. The commit, the public remote and the push all happened
afterwards, in the same session, once approved. R5 is closed; R1, R3, R4 and R6
remain open.

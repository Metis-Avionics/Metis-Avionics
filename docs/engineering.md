# Engineering

This page records doctrine that the organisation's repositories actually
practise. Where practice and doctrine diverge, the divergence is a registered
discrepancy, not a footnote.

## The memory is TOML

`spec.toml` in this repository; `spec.toml` plus `specs/*.toml` in
`economic-prv` and `seven`; `SPEC.toml` plus `specs/*.toml` in `theMQL`;
`@specs/SPEC.toml` plus `@specs/SUBSYSTEM.toml` in `theLiGI`. Markdown is a
projection.

`economic-prv/AGENTS.md:61` states it as doctrine: "The TOML spec is the memory;
Markdown is a generated projection." `prv-cli living update` renders
`living.toml` to `docs/living.md` and `docs/changelog.md`, and
`prv-cli session handover` renders the handover — the projections carry a
generated-file banner saying so.

The org convention is lowercase `spec.toml` at the repository root. Two
repositories diverge (`theMQL`, `theLiGI`) and two have no specification at all
(`theSix`, `theDAF`). Recorded as D7; no migration is scheduled from here.

## Spec-and-go

Work is specified before it is written, and the specification is executable
enough to be checked. `seven` goes furthest: `specs/VERIFICATION.md` maps every
spec §22 invariant to a named test, and `AGENTS.md:61-63` forbids merging
anything that breaks that mapping or weakens an invariant to silence a lint.

`theLiGI` defines an authority order in `@specs/SPEC.toml:52-57` — spec highest,
then subsystem specs, then tests, then public interfaces, then implementation.
That is a good pattern and it is not yet org doctrine.

## The Power of Ten

`economic-prv`, `theLiGI`, `theMQL` and `theDAF` all carry a TETANUS
implementation. `theLiGI/TETANUS.md` adapts Holzmann's NASA/JPL Power of Ten
for Rust, and the same rules appear machine-readable in
`economic-prv/tetanus.toml` with an enforced checker at
`economic-prv/scripts/tetanus-check.py`, plus `pyproject`/`Cargo` enforcement
for the other three.

This is the clearest example of the doctrine working: a rule that is only prose
gets followed until it is inconvenient. `tetanus.toml` gives the same rules
numeric thresholds, so a machine can refuse a commit.

## Quality gates that exist

| Repository | Gate | Kind |
|---|---|---|
| economic-prv | `scripts/tetanus-check.py` | power-of-ten static analysis |
| economic-prv | `scripts/check_no_coarse_locks.sh` | concurrency primitive policy |
| economic-prv | `scripts/check_schema.sh` | HelixDB schema conformance |
| economic-prv | `cargo deny` | supply chain: advisories, licences, bans |
| economic-prv | `cargo machete` | unused dependencies |
| economic-prv | `cargo fmt`, `cargo clippy`, `cargo test` | standard gates |
| seven | `cargo nextest --workspace --no-fail-fast` | test |
| seven | `cargo clippy --workspace --all-targets -- -D warnings` | lint |
| seven | `specs/VERIFICATION.md` invariant→test mapping | traceability |
| theMQL | `scripts/ci_guard.py` | static analysis |
| theLiGI | *documented only* — `AGENTS.md:37-44` | not enforced |
| seven | *nothing* | — |

`economic-prv` is the reference implementation of the whole doctrine:
spec-first, TOML memory, enforced power-of-ten, supply-chain gating, and a
staged crates.io publisher that refuses to skip a crate in dependency order.

`seven` and `theLiGI` document gates that nothing runs. A documented gate is a
claim; an enforced gate is a control. Recorded as D8.

## Reproducibility

- **Pinned primitives.** `seven/Cargo.toml:44` exact-pins `thesix = "=0.2.3"` with
  the comment that it matches the sibling projects. `economic-prv/Cargo.toml:39`
  allows the floating range `"0.2"` — recorded as D11, because a primitive that
  can drift under a consumer is not a primitive.
- **Published over forked.** `seven/specs/decisions/0003-themql-sourcing.md`
  is the reference decision: theMQL was believed unpublished, so a fork checkout
  was vendored; a corrected check against the crates.io API showed all four
  needed crates published at 0.1.0, so the decision became "depend on crates.io
  directly; no vendor directory", with Cargo.lock checksums carrying
  reproducibility. Recorded as decision 0003, status decided 2026-09-23.
- **Single-flight and stampede resistance** are design-level reproducibility
  concerns in `theSix`: a cache miss must never trigger a stampede, which
  otherwise makes population order — and therefore observable state —
  nondeterministic.

## Determinism

- `seven` is built around a canonical codec (`specs/decisions/0001`) with a
  benchmark as decision evidence: `cargo bench -p seven-core --bench
  canonical_codec`.
- `economic-prv` pins `tokio` exactly where a newer patch release fails
  internally on the pinned compiler; `seven/living.toml:33` records the same
  constraint for the same reason.
- `economic-prv/clippy.toml` sets a cognitive-complexity threshold, enforced
  through the workspace lint table.

## Rust

Edition 2024 is the target; `economic-prv` conforms. `theLiGI` and `theDAF` are
on 2021, and `seven` declares no edition at all because it is a virtual
manifest. Recorded as D16. Rust 1.98 is the declared minimum.

## What this organisation does not do

- It does not claim certification, and no system in it may issue ATC
  clearances, command aircraft, provide separation assurance, or present
  experimental state as authoritative. See `spec.toml [metis.safety]`.
- It does not build a graph database as a substitute for thinking. HelixDB
  appears in `economic-prv`, `seven` and `theMQL` as a persistence
  substrate, with `economic-prv/SCHEMA.md` and `scripts/check_schema.sh` keeping
  the graph schema and the code in agreement.

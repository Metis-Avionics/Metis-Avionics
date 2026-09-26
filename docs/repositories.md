# Repositories

The registry in [`spec.toml`](../spec.toml) is authoritative. This page is a
projection of it, and `scripts/validate.py` fails if the two disagree — including
the order of rows.

**Observed:** 2026-09-26 · **Source:** GitHub API, local clones, crates.io API
· **Entry count:** 7 · **Stale after:** 30 days

Re-observe with `python3 scripts/observe_registry.py` before trusting anything
here. Never edit a row to match an intention; record a discrepancy in
[`living.toml`](../living.toml) instead.

## Organisation repositories

<!-- registry:begin -->

| Repository | Role | Language | Default | Licence | CI | Crates | Local clone | Spec |
|---|---|---|---|---|---|---|---|---|
| `Metis-Avionics/economic-prv` | economic_simulation_research | rust | `master` | declared MIT, **no LICENSE file** | `ci.yml` | 9 | `/home/leo/prv` | `spec.toml` |
| `Metis-Avionics/seven` | aviation_resilience_research | rust | `main` | declared MIT, **no LICENSE file** | **none** | 9 | `/home/leo/seven` | `spec.toml` |
| `Metis-Avionics/theMQL` | message_query_runtime | rust | `main` | MIT | `ci.yml` | 19 | not cloned | `SPEC.toml` ⚠ |
| `Metis-Avionics/theSix` | cache_orchestration_primitive | rust | `main` | MIT | `ci.yml` | 1 | not cloned | none |
| `Metis-Avionics/theDAF` | data_access_primitive | python+rust | `main` | MIT | `ci.yml`, `publish.yml` | 9 + python | not cloned | none |
| `Metis-Avionics/theLiGI` | graph_intelligence_system | rust | `main` | MIT | **none** | 37 | `/home/leo/theLiGI` | `@specs/SPEC.toml` ⚠ |
| `Metis-Avionics/Metis-Avionics` | organisational_control_plane | python | `main` | MIT | `validate.yml` | 0 | this repository | `spec.toml` |

<!-- registry:end -->

⚠ diverges from the org convention `spec.toml` (lowercase, at repository root).

Three of the six member repositories are not cloned on the observation host, so
their entries are remote-only. Nothing in this table was inferred from a
directory listing that does not exist.

### What each one is

**economic-prv** — Research-grade economic simulation with EKF state estimation,
Monte Carlo shock simulation and a policy engine, under a Spec-and-Go
methodology. Rust 2024, nine crates, all published at 0.2.1. The only
organisation repository with a full local quality gate suite: TETANUS
power-of-ten checker, coarse-lock audit, schema check, `cargo deny`,
`cargo machete`.

**seven** — Experimental distributed aviation-resilience research system.
Independently operating nodes maintain a deterministic, provenance-aware
probabilistic representation of physical state while communications degrade
(loss, partition, delay, duplication, reordering). Carries the organisation's
safety boundary verbatim. Nine crates, all published at 0.1.0 except `seven-bin`.

**theMQL** — Native Rust message-query runtime for desktop, distributed,
telemetry, analysis, AI, GNC and embedded systems. External protocols and
applications are projections of the model rather than independent semantic
systems. Nineteen crates, four published at 0.1.0. The org's message and
semantics primitive.

**theSix** — Policy-driven six-tier cache orchestration. Application code never
selects tiers; a policy engine routes every operation and a control plane
coordinates concurrent state, including single-flight population so a cache
miss never triggers a stampede. One crate, published as `thesix` 0.2.3, consumed
by five other repositories across three GitHub organisations.

**theDAF** — Data-access abstraction layer separating transport, data access and
authorisation. A Python reference implementation (FastAPI) plus an LLVM-backed
Rust backend with a C-compatible ABI. All nine `daf-*` crates published at 0.1.0.
Its README documents a separate `theDAF-LLVM` repository that does not exist —
see discrepancy D15.

**theLiGI** — Native Rust adaptive commercial and social graph intelligence
system. Acquires external information and telemetry, normalises it into typed
messages and graph entities, performs deterministic and learned inference,
generates structured content, deploys through platform adapters, and feeds
telemetry back into the knowledge system. Thirty-seven crates, none published.
The most intricate consumer of the org's primitives, and the source of the
fork-pinning problem in D4.

**Metis-Avionics** — This repository. The constitution, the observed registry
and the machine-readable state of the organisation. No application code, no
crates, nothing to build. Two programs: `scripts/validate.py`, which checks
that the spec, the state, the schema, the documentation and `AGENTS.md` all
agree, and `scripts/observe_registry.py`, which re-reads the GitHub and
crates.io APIs and prints what has moved without ever writing. Created
2026-09-26, after the other six were registered; `observe_registry.py` reported
its own absence from the registry on its first run after publication, and the
entry was added in the same change that created the remote.

## Related repositories outside the organisation

These are not Mētis Avionics repositories. They are recorded because an
explicit edge exists, and an undeclared edge is a supply-chain risk.

| Repository | Relationship | Direction | Asserted by |
|---|---|---|---|
| `RAliane-REBORN/theDAF` | `fork_source` | consumed by org | theLiGI `Cargo.toml:79-84` |
| `RAliane-REBORN/theMQL` | `fork_source` | consumed by org | seven `specs/decisions/0003-themql-sourcing.md:5-8` |

Private repositories are not listed here, by name or by description. Their
existence, their ownership and their shape are not the organisation's to publish.

## Published artefacts

32 packages are published under this organisation, all verified against the
crates.io index on 2026-09-26. The primitives other repositories depend on:

| Package | Version | Owner | Consumed by |
|---|---|---|---|
| `thesix` | 0.2.3 | theSix | economic-prv, seven, theLiGI (via spec) |
| `themql-core` | 0.1.0 | theMQL | economic-prv (declared only), seven, theLiGI (path) |
| `themql-runtime` | 0.1.0 | theMQL | economic-prv (declared only) |
| `themql-estimation` | 0.1.0 | theMQL | seven |
| `themql-gnc` | 0.1.0 | theMQL | — |
| `prv-monte-carlo` | 0.2.1 | economic-prv | seven |

`theligi-*` is unpublished: theLiGI can only be consumed as a git dependency.
`seven-bin` is unpublished because it is a workspace binary.

## Known problems

20 discrepancies are registered in [`living.toml`](../living.toml): 6 high, 6
medium, 8 low. The five high-severity ones are, in short:

- **D1** economic-prv declares theMQL required, but no member crate consumes it
  and its lockfile has no theMQL package.
- **D2** economic-prv specifies `themql-runtime 0.2.0`, a version that has never
  been published; crates.io max is 0.1.0.
- **D3** theLiGI's `path = "../theMQL/..."` dependencies cannot resolve; the
  sibling checkout does not exist.
- **D4** theLiGI pins theDAF from a personal fork at a revision, bypassing nine
  crates theDAF publishes at 0.1.0.
- **D5** economic-prv and seven declare MIT in their specs but ship no LICENSE
  file, so neither is in fact MIT-licensed.

This repository records these. It does not fix them: the fixes belong in the
repositories that own them.

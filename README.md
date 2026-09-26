# Metis-Avionics

The control plane for **Mētis Avionics** — an independent avionics lab.

This repository is not a product. It contains no application code. It is the
canonical machine-readable constitution of the organisation: what Mētis is,
which repositories exist, how they relate, what the engineering rules are, and
what the current verified state is.

```text
spec.toml      the constitution: identity, safety, doctrine, governance, registry
living.toml    observed state, 20 registered discrepancies, remaining work
AGENTS.md      the contract an agent operates under
docs/          human projections of the two files above
scripts/       validate.py (offline consistency checks), observe_registry.py
pyproject.toml  pinned ruff and mypy, and the rules they enforce
schemas/       the registry contract, enforced rather than decorative
```

Start here:

| Question | Answer |
|---|---|
| What is this organisation? | [docs/mission.md](docs/mission.md) |
| What is the structure? | [docs/architecture.md](docs/architecture.md) |
| What are the rules? | [docs/governance.md](docs/governance.md) |
| How do we build? | [docs/engineering.md](docs/engineering.md) |
| What exists? | [docs/repositories.md](docs/repositories.md) |
| What is broken? | `living.toml` → `[[discrepancies]]` |

## The organisation at a glance

Six repositories, all public, all MIT-intended:

| Repository | What it is |
|---|---|
| [economic-prv](https://github.com/Metis-Avionics/economic-prv) | Economic simulation: EKF, Monte Carlo, policy engine |
| [seven](https://github.com/Metis-Avionics/seven) | Distributed aviation-resilience research under degraded comms |
| [theMQL](https://github.com/Metis-Avionics/theMQL) | Message-query runtime: 19 crates, the semantics primitive |
| [theSix](https://github.com/Metis-Avionics/theSix) | Policy-driven six-tier cache orchestration (`thesix`) |
| [theDAF](https://github.com/Metis-Avionics/theDAF) | Data-access abstraction: Python + LLVM-backed Rust with a C ABI |
| [theLiGI](https://github.com/Metis-Avionics/theLiGI) | Graph intelligence: 37 crates, acquisition to content |

32 published packages. Four related repositories outside the organisation are
recorded with typed relationships, because an undeclared dependency is a
supply-chain risk.

## Safety boundary

Mētis Avionics systems are research and engineering platforms. They must never
issue ATC clearances, command aircraft, provide separation assurance,
autonomously direct aircraft, claim certification, or present experimental state
as authoritative aviation state. Adopted from `seven` and binding org-wide.

## Working in this repository

```bash
python3 scripts/validate.py            # 14 offline invariants
python3 scripts/validate.py --strict   # accepted gaps enforced too
python3 scripts/validate.py --list     # what each check enforces
python3 scripts/observe_registry.py    # re-observe; prints a diff, never commits

uv run ruff check scripts/              # lint
uv run ruff format --check scripts/    # formatting
uv run mypy                            # types, --strict
```

`validate.py` makes no network calls and inspects no other repository. It
enforces org-level internal consistency. Per-repository quality gates are
enforced in those repositories. The two programs in `scripts/` are held to
this repository's own gates — pinned `ruff` and `mypy` in `pyproject.toml`,
locked in `uv.lock`, and run on every push.

Read [AGENTS.md](AGENTS.md) before making a change. It is the contract, and the
validator enforces that it stays in sync with `spec.toml [agent.rules]`.

## Current state

20 discrepancies are registered — 6 high, 6 medium, 8 low. Five concern member
repositories: a declared dependency that is not in a build graph, a specified
crate version that was never published, unresolvable path dependencies, a fork
pin bypassing nine published crates, and two repositories that declare MIT while
shipping no `LICENSE` file. The sixth is D20, which this repository committed
against itself: an early public revision named and described two private
repositories. They were removed, the history was rebuilt, and the rule that
should have prevented it is now written into the spec.

This repository records all of them and fixes none. The fixes belong in the
repositories that own them.

## Licence

MIT — see [LICENSE](LICENSE). Note that two member repositories declare MIT in
their specs without shipping a `LICENSE` file, which is discrepancy D5 and is
not a precedent to copy.

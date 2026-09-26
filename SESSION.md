# SESSION

Live record of the current working session. Machine-readable counterparts live
in [`living.toml`](living.toml); this page is a projection and adds no facts.

## Current session

- **Started:** 2026-09-26
- **Agent:** opencode
- **Mode:** bootstrap, then publication
- **Branch:** `main`, tracking `origin/main`, published
- **Phase:** constitution published and gated

## What this session did

1. Verified the organisation's actual repository set from the GitHub API: six
   public member repositories, no forks, none archived, no `theDAF-LLVM`.
2. Verified local state for the three cloned repositories
   (`economic-prv`, `seven`, `theLiGI`): remotes, HEADs, branch positions,
   cleanliness, governance files, and the exact declaration-vs-implementation
   mismatches.
3. Verified the crates.io publication state of 34 package names, which corrected
   two beliefs held at the start of the session: `theDAF` *does* publish all nine
   of its `daf-*` crates at 0.1.0, and `prv-monte-carlo` is published at 0.2.1.
4. Wrote the constitution: `spec.toml`, `schemas/repository.schema.toml`,
   `living.toml`, the documentation projections, `AGENTS.md`, the validator, and
   the CI workflow.
5. Registered 20 discrepancies with evidence, and scoped every waiver to a single
   finding so that no accepted gap conceals an unrelated one.
6. Committed and published the repository as
   `github.com/Metis-Avionics/Metis-Avionics`, public, on `main`. The observer
   then reported the new repository's own absence from the registry, so the
   seventh registry entry was added in the same change rather than left for later.
7. Held the two programs to the organisation's own doctrine: pinned `ruff` and
   `mypy`, `uv.lock` committed, three gates running on every push, and the first
   CI run's Node 20 deprecation annotation acted on rather than ignored.
8. Disclosed two private repositories in the first two published revisions of
   this registry, and purged them: entries removed, local history rebuilt from
   the clean tree rather than filtered, GitHub repository deleted and recreated.
   Recorded as D20 without naming them. The names appear in no object in this
   repository and in no ref of the remote.

## Findings that changed the design

| Belief at session start | Observed reality |
|---|---|
| theDAF, theMQL, theSix are sibling repos with clones | All three exist remotely; none is cloned here. theDAF is a Python/Rust hybrid, not a Rust repo |
| theLiGI depends on theDAF, which is unpublished | theDAF publishes nine crates at 0.1.0; theLiGI pins a fork at a revision instead |
| economic-prv and seven are MIT | Both *declare* MIT and neither ships a `LICENSE` file |
| `SPEC.toml` is the org convention | Two repositories use `SPEC.toml`; the two most active use `spec.toml`; two have no spec at all |
| theDAF's LLVM backend is a separate repo | That repo does not exist; the backend is in-tree, including `daf-ffi` |

## Validation

```text
python3 scripts/validate.py           →  0 errors, 11 warnings
python3 scripts/validate.py --strict  →  11 errors (every waived gap enforced)
python3 scripts/observe_registry.py   →  7 repositories, no registry drift
                                         beyond D5, no publication drift
uv run ruff check scripts/            →  All checks passed
uv run ruff format --check scripts/   →  2 files already formatted
uv run mypy                           →  Success: no issues in 2 source files
```

All 11 warnings are waived findings: 4 spec-filename findings waived by D7,
2 licence findings by D5, 5 automation findings by D8 (no CI) and D9 (no living
state). No waiver is broader than the finding it names, and `--strict` re-raises
every one of them.

The observer independently confirmed all 32 recorded packages against the
crates.io index and found no drift in any of them.

## Not done

- The copyright holder of record is still unconfirmed (`R1`). The published
  `LICENSE` names the organisation, not a person.
- No discrepancy was fixed in another repository. Nineteen are registered; the
  five high-severity ones need sessions in `economic-prv`, `theLiGI` and
  `theDAF` (`R3`).

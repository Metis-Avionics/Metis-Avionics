#!/usr/bin/env python3
"""Validate the Mētis Avionics control plane.

Checks that spec.toml, living.toml, the registry schema, the documentation
projections and AGENTS.md agree with each other and with the shape declared in
schemas/repository.schema.toml.

This validator is offline. It makes no network calls and inspects no other
repository. It enforces org-level internal consistency only; per-repository
quality gates are enforced in those repositories.

Usage:
    python3 scripts/validate.py            # errors fail, accepted gaps warn
    python3 scripts/validate.py --strict   # accepted gaps fail too
    python3 scripts/validate.py --quiet    # warnings suppressed
    python3 scripts/validate.py --list     # list check ids and exit

Exit codes: 0 clean, 1 findings, 2 bad invocation or unreadable input.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
"""Parsed TOML. spec.toml, living.toml and the schema are all this shape."""

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec.toml"
LIVING = ROOT / "living.toml"
SCHEMA = ROOT / "schemas" / "repository.schema.toml"
AGENTS = ROOT / "AGENTS.md"
REGISTRY_DOC = ROOT / "docs" / "repositories.md"
DOC_DIR = ROOT / "docs"

CHECKS = {
    "C1": "spec.toml document shape matches the schema",
    "C2": "registry entries carry every required key with the declared type/enum/pattern",
    "C3": "full_name is consistent with the organisation and the entry name",
    "C4": "no duplicate entries across the registry and the related list",
    "C5": "specification filename conforms to the org convention",
    "C6": "every declared dependency resolves to a publication or a known repository",
    "C7": "docs/repositories.md matches the registry exactly and in order",
    "C8": "relative documentation links resolve on disk",
    "C9": "AGENTS.md documents every [agent.rules] key",
    "C10": "registry observations are within the staleness window",
    "C11": "living.toml [[discrepancies]] entries are well formed",
    "C12": "declared licences are backed by an actual LICENSE file",
    "C13": "repositories claiming org requirements have the required automation",
    "C14": "living state points only at files that exist",
}

# What GitHub reports when a repository has no LICENSE file. The registry uses
# the same spelling so the two can be compared directly.
NO_GITHUB_LICENCE = ("UNSET", "NOASSERTION")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REGION_RE = re.compile(r"<!--\s*registry:begin\s*-->(.*?)<!--\s*registry:end\s*-->", re.DOTALL)
FIRST_COL_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|", re.MULTILINE)


class Findings:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str, str]] = []

    def add(self, check: str, level: str, where: str, message: str) -> None:
        self.items.append((check, level, where, message))

    def error(self, check: str, where: str, message: str) -> None:
        self.add(check, "error", where, message)

    def warn(self, check: str, where: str, message: str) -> None:
        self.add(check, "warning", where, message)


def load(path: Path) -> JSON:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError:
        sys.exit(f"error: {path.relative_to(ROOT)} is missing")
    except tomllib.TOMLDecodeError as exc:
        sys.exit(f"error: {path.relative_to(ROOT)} is not valid TOML: {exc}")


def dig(mapping: JSON, dotted: str) -> object:
    """Walk a dotted path. Returns None when any step is absent."""
    node: object = mapping
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def as_table(node: object) -> JSON:
    """Interpret a node as a table. Anything else is an empty table."""
    return node if isinstance(node, dict) else {}


def as_keys(node: object) -> list[Any]:
    """Interpret a node as a list of required keys. Anything else is empty."""
    if isinstance(node, list) and all(isinstance(item, str) for item in node):
        return node
    return []


def require_keys(f: Findings, check: str, where: str, obj: JSON, keys: list[str]) -> None:
    for key in keys:
        if key not in obj:
            f.error(check, where, f"missing required key `{key}`")


def check_types(f: Findings, where: str, obj: JSON, types: JSON) -> None:
    actual = {
        str: "str",
        bool: "bool",
        int: "int",
        list: "list",
        dict: "dict",
    }
    for key, expected in types.items():
        if key not in obj:
            continue
        if not isinstance(obj[key], (str, bool, int, list, dict)):
            f.error("C2", where, f"`{key}` has unsupported type {type(obj[key]).__name__}")
        elif actual[type(obj[key])] != expected:
            found = actual[type(obj[key])]
            f.error("C2", where, f"`{key}` is {found}, expected {expected}")


def check_enums(f: Findings, check: str, where: str, obj: JSON, enums: JSON) -> None:
    for key, allowed in enums.items():
        if key not in obj:
            continue
        if obj[key] not in allowed:
            f.error(check, where, f"`{key}` = {obj[key]!r} is not one of {allowed}")


def check_patterns(f: Findings, check: str, where: str, obj: JSON, patterns: JSON) -> None:
    for key, pattern in patterns.items():
        if key not in obj or not isinstance(obj[key], str):
            continue
        if not re.fullmatch(pattern, obj[key]):
            f.error(check, where, f"`{key}` = {obj[key]!r} does not match {pattern}")


# ── individual checks ────────────────────────────────────────────────────────


def c1_document(f: Findings, spec: JSON, schema: JSON) -> None:
    document = schema["document"]
    require_keys(f, "C1", "spec.toml", spec, document["required_top_level_keys"])
    for table in document["required_top_level"]:
        if table not in spec:
            f.error("C1", "spec.toml", f"missing required table `[{table}]`")
            continue
        for sub, rules in as_table(dig(document, f"tables.{table}")).items():
            if not isinstance(rules, dict) or "required" not in rules:
                continue
            where = f"spec.toml [{table}.{sub}]"
            node = dig(spec, f"{table}.{sub}")
            if node is None:
                f.error("C1", where, "table is missing")
                continue
            if not isinstance(node, dict):
                f.error("C1", where, "the schema declares a table here and the file has a value")
                continue
            require_keys(f, "C1", where, node, rules["required"])
        if isinstance(spec.get(table), dict) and "required" in spec[table]:
            require_keys(f, "C1", f"spec.toml [{table}]", spec[table], spec[table]["required"])


def c2_c3_c4_entries(f: Findings, spec: JSON, schema: JSON) -> None:
    repos = spec.get("repositories", {})
    registry = repos.get("registry", [])
    related = repos.get("related", [])
    org = spec.get("metis", {}).get("repository", "Metis-Avionics/Metis-Avionics")
    org_prefix = org.rsplit("/", 1)[0]

    seen_full: dict[str, str] = {}
    seen_short: dict[str, str] = {}

    entry_rules = schema["entry"]
    for entry in registry:
        where = f"registry[{entry.get('full_name', '<unnamed>')}]"
        require_keys(f, "C2", where, entry, entry_rules["required"])
        check_types(f, where, entry, entry_rules.get("types", {}))
        check_enums(f, "C2", where, entry, entry_rules.get("enums", {}))
        check_patterns(f, "C2", where, entry, entry_rules.get("patterns", {}))

        full = entry.get("full_name", "")
        if not full.startswith(f"{org_prefix}/"):
            f.error("C3", where, f"full_name {full!r} is not under {org_prefix}/")
        elif full.rsplit("/", 1)[1] != entry.get("name"):
            f.error("C3", where, f"name {entry.get('name')!r} disagrees with {full!r}")

        seen_full[full] = where
        seen_short.setdefault(f"{org_prefix}/{entry.get('name')}", where)

        for consumes in entry.get("consumes", []):
            require_keys(
                f, "C2", f"{where}.consumes", consumes, schema["entry_consumes"]["required"]
            )
            check_enums(
                f, "C2", f"{where}.consumes", consumes, schema["entry_consumes"].get("enums", {})
            )

        for git_dep in entry.get("consumes_git", []):
            where_git = f"{where}.consumes_git"
            require_keys(f, "C2", where_git, git_dep, schema["entry_consumes_git"]["required"])
            check_patterns(
                f, "C2", where_git, git_dep, schema["entry_consumes_git"].get("patterns", {})
            )

    related_rules = schema["related_entry"]
    for entry in related:
        where = f"related[{entry.get('full_name', '<unnamed>')}]"
        require_keys(f, "C2", where, entry, related_rules["required"])
        check_enums(f, "C2", where, entry, related_rules.get("enums", {}))
        if entry.get("in_org") is not False:
            f.error("C3", where, "related entries must declare in_org = false")
        if entry.get("full_name") in seen_full:
            f.error("C4", where, f"duplicate of registry entry {entry['full_name']}")
        seen_full[entry.get("full_name", "")] = where
        if entry.get("name") in seen_short:
            f.error(
                "C4",
                where,
                f"name {entry.get('name')!r} collides with org repository "
                f"{seen_short[entry['name']]}",
            )

    duplicates = {
        name: where for name, where in seen_full.items() if list(seen_full).count(name) > 1
    }
    for name, where in duplicates.items():
        f.error("C4", where, f"duplicate entry for {name}")

    observed = repos.get("observed", {})
    declared = observed.get("entry_count")
    if isinstance(declared, int) and declared != len(registry):
        f.error(
            "C1",
            "spec.toml [repositories.observed]",
            f"entry_count {declared} does not match {len(registry)} registry entries",
        )


def c5_spec_filename(f: Findings, spec: JSON) -> None:
    convention = dig(spec, "repositories.conventions.spec_file")
    for entry in spec.get("repositories", {}).get("registry", []):
        actual = entry.get("spec_file", "")
        name = entry.get("full_name", "<unnamed>")
        if not actual:
            f.error("C5", f"registry[{name}]", "no specification file present")
            continue
        basename = actual.rsplit("/", 1)[-1]
        if basename != convention:
            f.error(
                "C5",
                f"registry[{name}]",
                f"specification file is {actual!r}, org convention is {convention!r}",
            )
        if entry.get("spec_file_conforms") is not (basename == convention):
            f.error(
                "C5",
                f"registry[{name}]",
                f"spec_file_conforms = {entry.get('spec_file_conforms')!r} contradicts {actual!r}",
            )


def c6_dependencies(f: Findings, spec: JSON, schema: JSON) -> None:
    repos = spec.get("repositories", {})
    publications = repos.get("publications", {})
    known = {e.get("full_name") for e in repos.get("registry", [])}
    known |= {e.get("full_name") for e in repos.get("related", [])}

    if schema.get("publication", {}).get("must_cover_crates_io_dependencies"):
        metadata_keys = set(schema["publication"].get("metadata_keys", []))
        for key, value in publications.items():
            if key in metadata_keys or not isinstance(value, dict):
                continue
            require_keys(f, "C2", f"publications[{key}]", value, schema["publication"]["required"])
            check_patterns(
                f, "C2", f"publications[{key}]", value, schema["publication"].get("patterns", {})
            )

    for entry in repos.get("registry", []):
        name = entry.get("full_name", "<unnamed>")
        for consumes in entry.get("consumes", []):
            package = consumes.get("package")
            source = consumes.get("source")
            if source == "crates_io" and package not in publications:
                f.error(
                    "C6",
                    f"registry[{name}].consumes",
                    f"crates.io package {package!r} is not recorded in [repositories.publications]",
                )
            if source == "path" and consumes.get("resolved_in_lock") is not True:
                f.warn(
                    "C6",
                    f"registry[{name}].consumes",
                    f"path dependency {package!r} is not recorded as resolved in any lockfile",
                )
        for git_dep in entry.get("consumes_git", []):
            target = git_dep.get("repository")
            if target not in known:
                f.error(
                    "C6",
                    f"registry[{name}].consumes_git",
                    f"git dependency target {target!r} is neither a registry "
                    "nor a related repository",
                )
        for integration in entry.get("integrations", []):
            target = integration.get("repository")
            if target not in known:
                f.error(
                    "C6",
                    f"registry[{name}].integrations",
                    f"integration target {target!r} is neither a registry nor a related repository",
                )
        for package in entry.get("publishes", []):
            if package not in publications:
                f.error(
                    "C6",
                    f"registry[{name}].publishes",
                    f"{package!r} is declared as published but is absent from "
                    "[repositories.publications]",
                )
        for package in entry.get("publishes", []):
            recorded = publications.get(package, {}).get("owner_repo")
            if recorded and recorded != name:
                f.error(
                    "C6",
                    f"registry[{name}].publishes",
                    f"{package!r} is attributed to {recorded} in the publication ledger",
                )


def c7_docs_table(f: Findings, spec: JSON) -> None:
    if not REGISTRY_DOC.exists():
        f.error("C7", "docs/repositories.md", "file is missing")
        return
    text = REGISTRY_DOC.read_text(encoding="utf-8")
    match = REGION_RE.search(text)
    if not match:
        f.error(
            "C7",
            "docs/repositories.md",
            "missing <!-- registry:begin --> / <!-- registry:end --> markers",
        )
        return
    documented = FIRST_COL_RE.findall(match.group(1))
    registry = [e.get("full_name") for e in spec.get("repositories", {}).get("registry", [])]
    if documented != registry:
        f.error(
            "C7",
            "docs/repositories.md",
            f"documented order {documented} does not match registry order {registry}",
        )


def c8_links(f: Findings) -> None:
    targets = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        *sorted(ROOT.glob("*.md")),
        *sorted(DOC_DIR.glob("*.md")),
    ]
    seen: set[Path] = set()
    for doc in targets:
        if doc in seen:
            continue
        seen.add(doc)
        if not doc.exists():
            f.warn("C8", str(doc.relative_to(ROOT)), "file is missing")
            continue
        text = doc.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = raw.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "/")):
                continue
            resolved = (doc.parent / target).resolve()
            if not resolved.exists():
                f.error("C8", str(doc.relative_to(ROOT)), f"broken link: {target}")


def c9_agent_prompt(f: Findings, spec: JSON, schema: JSON) -> None:
    rules = as_table(dig(spec, "agent.rules"))
    required = as_keys(dig(schema, "document.tables.agent.rules.required")) or list(rules)
    if not AGENTS.exists():
        f.error("C9", "AGENTS.md", "file is missing")
        return
    text = AGENTS.read_text(encoding="utf-8")
    for key in required:
        if key not in rules:
            f.error(
                "C9", "spec.toml [agent.rules]", f"{key!r} is required by the schema but absent"
            )
        elif key not in text:
            f.error("C9", "AGENTS.md", f"does not document the rule `{key}`")


def c10_freshness(f: Findings, spec: JSON) -> None:
    node = dig(spec, "repositories.observed")
    if not isinstance(node, dict):
        f.error(
            "C1",
            "spec.toml [repositories.observed]",
            "table is missing or is not a table",
        )
        return
    observed = node
    window = observed.get("stale_after_days", 30)
    try:
        seen = datetime.fromisoformat(str(observed["observed_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        f.error(
            "C1", "spec.toml [repositories.observed]", "observed_at is not an ISO-8601 timestamp"
        )
        return
    age = (datetime.now(UTC) - seen).days
    if age > window:
        f.error(
            "C10",
            "spec.toml [repositories.observed]",
            f"observations are {age} days old, staleness window is {window}; re-observe",
        )


def c11_living(f: Findings, living: JSON, schema: JSON) -> None:
    rules = schema["living"]
    require_keys(f, "C11", "living.toml", living, rules["required_top_level"])
    require_keys(
        f,
        "C11",
        "living.toml [handover]",
        living.get("handover", {}),
        rules["handover"]["required"],
    )

    seen: set[str] = set()
    for entry in living.get("discrepancies", []):
        where = f"discrepancies[{entry.get('id', '<unnamed>')}]"
        require_keys(f, "C11", where, entry, rules["discrepancies"]["required"])
        check_enums(f, "C11", where, entry, rules["discrepancies"].get("enums", {}))
        if not entry.get("evidence"):
            f.error("C11", where, "an observation without evidence is an opinion")
        if not isinstance(entry.get("evidence"), list):
            f.error("C11", where, "evidence must be a list of path:line or command strings")
        identifier = entry.get("id")
        if identifier in seen:
            f.error("C11", where, f"duplicate discrepancy id {identifier!r}")
        seen.add(identifier)
        referenced = entry.get("check")
        if referenced and referenced not in CHECKS:
            f.error("C11", where, f"check {referenced!r} is not a check this validator implements")


def c12_licences(f: Findings, spec: JSON) -> None:
    for entry in spec.get("repositories", {}).get("registry", []):
        name = entry.get("full_name", "<unnamed>")
        github = entry.get("github_license")
        declared = entry.get("declared_license")
        if github == "UNSET" and declared and declared != "NONE":
            f.error(
                "C12",
                f"registry[{name}]",
                f"spec declares {declared} but the repository has no LICENSE file; "
                "the code is not in fact licensed as declared",
            )
        if declared and github and github not in NO_GITHUB_LICENCE and declared != github:
            f.warn("C12", f"registry[{name}]", f"declared {declared} but GitHub reports {github}")


def c13_automation(f: Findings, spec: JSON) -> None:
    requirements = as_table(dig(spec, "governance.repository_requirements"))
    for entry in spec.get("repositories", {}).get("registry", []):
        name = entry.get("full_name", "<unnamed>")
        if requirements.get("ci_required") and entry.get("ci") == "none":
            f.error(
                "C13",
                f"registry[{name}]",
                "no continuous integration, but governance.repository_requirements requires it",
            )
        if requirements.get("living_state_required") and not entry.get("living_file"):
            f.error(
                "C13",
                f"registry[{name}]",
                "no living state, but governance.repository_requirements requires it",
            )


def c14_state_files(f: Findings, spec: JSON) -> None:
    state = as_table(dig(spec, "state"))
    for key, value in state.items():
        if not isinstance(value, str) or "/" in value:
            continue
        if not (ROOT / value).exists():
            f.error("C14", f"spec.toml [state].{key}", f"{value!r} does not exist")


# ── driver ───────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--strict", action="store_true", help="treat accepted discrepancies as errors"
    )
    parser.add_argument("--quiet", action="store_true", help="suppress warnings")
    parser.add_argument("--list", action="store_true", help="list check ids and exit")
    args = parser.parse_args()

    if args.list:
        for check, description in CHECKS.items():
            print(f"{check}  {description}")
        return 0

    spec = load(SPEC)
    living = load(LIVING)
    schema = load(SCHEMA)

    findings = Findings()
    c1_document(findings, spec, schema)
    c2_c3_c4_entries(findings, spec, schema)
    c5_spec_filename(findings, spec)
    c6_dependencies(findings, spec, schema)
    c7_docs_table(findings, spec)
    c8_links(findings)
    c9_agent_prompt(findings, spec, schema)
    c10_freshness(findings, spec)
    c11_living(findings, living, schema)
    c12_licences(findings, spec)
    c13_automation(findings, spec)
    c14_state_files(findings, spec)

    waivers: dict[str, list[str | None]] = {}
    for entry in living.get("discrepancies", []):
        if entry.get("status") == "accepted" and entry.get("check"):
            waivers.setdefault(entry["check"], []).append(entry.get("waiver_key"))

    def waived(check: str, message: str) -> bool:
        """Report whether an accepted discrepancy covers this finding."""
        return any(key is None or key in message for key in waivers.get(check, []))

    errors = warnings = 0
    for check, level, where, message in findings.items:
        effective = (
            "warning" if level == "error" and waived(check, message) and not args.strict else level
        )
        if effective == "error":
            errors += 1
            print(f"ERROR   {check}  {where}: {message}")
        elif not args.quiet:
            warnings += 1
            print(f"warning {check}  {where}: {message}")

    open_gaps = sum(1 for e in living.get("discrepancies", []) if e.get("status") == "open")
    accepted_gaps = sum(
        1
        for e in living.get("discrepancies", [])
        if e.get("status") == "accepted" and e.get("check")
    )
    scoped = sum(1 for e in living.get("discrepancies", []) if e.get("waiver_key"))
    print()
    print(f"checked {len(CHECKS)} invariants against spec_version {spec.get('spec_version', '?')}")
    print(
        f"registry: {len(spec.get('repositories', {}).get('registry', []))} repositories, "
        f"{len(spec.get('repositories', {}).get('related', []))} related"
    )
    print(
        f"discrepancies: {len(living.get('discrepancies', []))} registered, "
        f"{open_gaps} open, {accepted_gaps} with an active check waiver "
        f"({scoped} scoped to a message)"
    )
    print(f"result: {errors} error(s), {warnings} warning(s)")
    if accepted_gaps and not args.strict:
        print(
            "note: accepted discrepancies downgrade their check to a warning; "
            "use --strict to enforce them"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

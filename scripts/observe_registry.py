#!/usr/bin/env python3
"""Re-observe the Mētis Avionics registry and print what changed.

This is the only tool here that touches the network. It reads the current state
of every organisation repository from the GitHub API and every published package
from the crates.io API, then prints a diff against the observations recorded in
spec.toml.

It NEVER writes and NEVER commits. An observation is corrected by a human who
has read the diff, understood it, and decided what it means. That restriction is
the point: a script that silently rewrites the registry would make the registry
an intention rather than an observation.

Usage:
    python3 scripts/observe_registry.py            # diff only
    python3 scripts/observe_registry.py --json     # machine-readable
    python3 scripts/observe_registry.py --stale   # only report staleness

Exit codes: 0 registry matches reality, 1 drift detected, 2 bad invocation or
unreachable API.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

JSON = dict[str, Any]
"""Parsed TOML, or a parsed JSON object. Registry entries and every API
response body that is an object have this shape."""

JSON_LIST = list[JSON]
"""A parsed JSON array of objects, as the GitHub repository listing returns."""

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec.toml"
ORG = "Metis-Avionics"
GITHUB_API = "https://api.github.com"
CRATES_IO = "https://crates.io/api/v1/crates"
TIMEOUT = 20
# The registry compares a field the organisation requires against the field it
# actually observed. Only these are compared; anything else is out of scope for
# a drift check and would produce noise nobody acts on.
COMPARED_FIELDS = ("default_branch", "visibility", "archived", "pushed_at", "github_license")
# Values GitHub or a repository may use to mean "no licence", spelled every way
# the ecosystem spells it.
NO_LICENCE = ("UNSET", "NONE", "NOASSERTION")


def fetch_json(url: str, accept: str = "application/vnd.github+json") -> JSON | JSON_LIST:
    if not url.startswith("https://"):
        # The scheme is constant in every call site below. This is here so that a
        # future edit which interpolates registry data into a URL cannot quietly
        # turn an observation tool into a local file reader.
        sys.exit(f"error: refusing to open a non-https URL: {url}")
    # S310: the scheme is asserted to be https immediately above, and the URL is
    # assembled from module constants and a page number. Audited, not silenced.
    request = urllib.request.Request(  # noqa: S310
        url,
        headers={
            "Accept": accept,
            "User-Agent": "metis-avionics-registry-observer",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
            payload: JSON | JSON_LIST = json.load(response)
            return payload
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            # crates.io answers 404 for a crate that was never published, and
            # GitHub answers 404 when the listing runs off the end. Both mean
            # "nothing here", not "something is wrong".
            return {}
        raise
    except urllib.error.URLError as exc:
        sys.exit(f"error: cannot reach {url}: {exc.reason}")


def observe_org() -> dict[str, JSON]:
    """Every repository in the organisation, public and private alike."""
    found: dict[str, JSON] = {}
    page = 1
    while True:
        url = f"{GITHUB_API}/orgs/{ORG}/repos?per_page=100&type=all&page={page}"
        batch = fetch_json(url)
        if not batch:
            break
        if not isinstance(batch, list):
            sys.exit(f"error: expected a JSON array of repositories from {url}")
        for repo in batch:
            found[repo["name"]] = {
                "full_name": repo["full_name"],
                "language": repo.get("language"),
                "default_branch": repo.get("default_branch"),
                "visibility": repo.get("visibility"),
                "archived": repo.get("archived", False),
                "pushed_at": repo.get("pushed_at"),
                "github_license": (repo.get("license") or {}).get("spdx_id") or "UNSET",
            }
        page += 1
    return found


def observe_publication(name: str) -> JSON:
    data = fetch_json(f"{CRATES_IO}/{name}")
    if not isinstance(data, dict) or "crate" not in data:
        return {"published": False}
    return {
        "published": True,
        "max_version": data["crate"].get("max_version"),
        "version_count": len(data.get("versions", [])),
    }


def load_registry() -> tuple[list[JSON], JSON, JSON]:
    with SPEC.open("rb") as handle:
        spec: JSON = tomllib.load(handle)
    repos: JSON = spec.get("repositories", {})
    return repos.get("registry", []), repos.get("publications", {}), spec


def report_staleness(spec: JSON) -> bool:
    observed = spec.get("repositories", {}).get("observed", {})
    window = observed.get("stale_after_days", 30)
    seen = observed.get("observed_at")
    try:
        seen_at = datetime.fromisoformat(str(seen).replace("Z", "+00:00"))
    except ValueError:
        print(f"observed_at {seen!r} is not a timestamp")
        return True
    age = (datetime.now(UTC) - seen_at).days
    state = "EXPIRED" if age > window else "fresh"
    print(f"observed_at {seen} — {age} day(s) old, window {window} — {state}")
    if age > window:
        print("  the registry has expired: re-observe before relying on it")
    return bool(age > window)


def compare_repositories(recorded: dict[str, JSON], actual: dict[str, JSON]) -> list[str]:
    """Every way in which the recorded registry differs from the GitHub API."""
    drift: list[str] = []
    for name in sorted(set(recorded) | set(actual)):
        want = recorded.get(name)
        have = actual.get(name)
        if have is None:
            drift.append(f"{name}: in spec.toml but not in the {ORG} organisation")
            continue
        if want is None:
            drift.append(
                f"{name}: in the {ORG} organisation but absent from spec.toml — "
                "add it deliberately, do not let a tool add it"
            )
            continue
        for field in COMPARED_FIELDS:
            if field in want and want[field] != have[field]:
                drift.append(
                    f"{name}.{field}: spec says {want[field]!r}, GitHub says {have[field]!r}"
                )
        declared = want.get("declared_license")
        if have["github_license"] in NO_LICENCE and declared not in (None, *NO_LICENCE):
            drift.append(
                f"{name}: still has no LICENSE file while the spec declares {declared} "
                "(discrepancy D5)"
            )
    return drift


def compare_publications(publications: JSON) -> list[str]:
    """Every recorded package whose published version has moved, or vanished."""
    drift: list[str] = []
    published = (k for k, v in publications.items() if isinstance(v, dict) and "max_version" in v)
    for package in sorted(published):
        found = observe_publication(package)
        recorded_version = publications[package].get("max_version")
        if not found.get("published"):
            drift.append(
                f"{package}: recorded as published at {recorded_version} "
                "but absent from the crates.io index"
            )
        elif found["max_version"] != recorded_version:
            drift.append(
                f"{package}: spec says {recorded_version}, crates.io says {found['max_version']}"
            )
    return drift


def print_report(drift: list[str], package_drift: list[str], report: JSON) -> None:
    print(f"organisation {ORG}: {len(report['repositories'])} repositories observed")
    if drift:
        print(f"\nregistry drift ({len(drift)}):")
        for line in drift:
            print(f"  - {line}")
    else:
        print("\nno registry drift: every entry matches the GitHub API")
    if package_drift:
        print(f"\npublication drift ({len(package_drift)}):")
        for line in package_drift:
            print(f"  - {line}")
    else:
        print("no publication drift: every recorded package matches the crates.io index")
    print("\nnothing was written. Correct the observations by hand, or record a discrepancy.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a diff")
    parser.add_argument("--stale", action="store_true", help="report staleness and exit")
    args = parser.parse_args()

    registry, publications, spec = load_registry()

    if args.stale:
        return 1 if report_staleness(spec) else 0

    actual = observe_org()
    recorded = {entry["name"]: entry for entry in registry}
    drift = compare_repositories(recorded, actual)
    package_drift = compare_publications(publications)
    report: JSON = {
        "organisation": ORG,
        "observed_at": datetime.now(UTC).isoformat(),
        "repositories": actual,
    }

    if args.json:
        print(json.dumps({"drift": drift, "packages": package_drift, "observed": report}, indent=2))
    else:
        print_report(drift, package_drift, report)

    return 1 if (drift or package_drift) else 0


if __name__ == "__main__":
    sys.exit(main())

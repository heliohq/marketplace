#!/usr/bin/env python3
"""Validate marketplace structure and merge-time Heliox publication order."""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

VERSION_PATHS = {
    "heliox/.claude-plugin/plugin.json": ("version",),
    "heliox/.codex-plugin/plugin.json": ("version",),
    ".claude-plugin/marketplace.json": ("plugins", "heliox", "version"),
    ".agents/plugins/marketplace.json": ("plugins", "heliox", "version"),
}
CATALOG_PATHS = {
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
}
PUBLISH_PREFIX = "heliox-publish-v"
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
CLAUDE_CATALOG = ".claude-plugin/marketplace.json"
CODEX_CATALOG = ".agents/plugins/marketplace.json"
CLAUDE_MANIFEST = "heliox/.claude-plugin/plugin.json"
CODEX_MANIFEST = "heliox/.codex-plugin/plugin.json"


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def parse_version(value: object, location: str) -> tuple[int, int, int]:
    if not isinstance(value, str) or not SEMVER_RE.fullmatch(value):
        fail(f"{location} must use stable X.Y.Z SemVer")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def json_at_ref(root: Path, ref: str, path: str) -> object:
    raw = run_git(root, "show", f"{ref}:{path}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        fail(f"{path} at {ref} is invalid JSON: {error}")


def json_file(root: Path, path: str) -> object:
    try:
        return json.loads((root / path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path} is unreadable or invalid JSON: {error}")


def nested_version(document: object, selector: tuple[str, ...], location: str) -> str:
    if not isinstance(document, dict):
        fail(f"{location} must contain a JSON object")
    if selector[0] == "version":
        value = document.get("version")
    else:
        plugins = document.get("plugins")
        if not isinstance(plugins, list):
            fail(f"{location} must contain a plugins array")
        matches = [
            plugin
            for plugin in plugins
            if isinstance(plugin, dict) and plugin.get("name") == selector[1]
        ]
        if len(matches) != 1:
            fail(f"{location} must contain exactly one heliox entry")
        value = matches[0].get("version")
    parse_version(value, location)
    return str(value)


def versions(root: Path, ref: str | None = None) -> tuple[str, tuple[int, int, int]]:
    found: dict[str, str] = {}
    for path, selector in VERSION_PATHS.items():
        document = json_at_ref(root, ref, path) if ref else json_file(root, path)
        found[path] = nested_version(
            document, selector, f"{path}{f' at {ref}' if ref else ''}"
        )
    unique = set(found.values())
    if len(unique) != 1:
        fail(
            "Heliox versions are not in lockstep: "
            + ", ".join(f"{p}={v}" for p, v in found.items())
        )
    version = unique.pop()
    return version, parse_version(version, "Heliox version")


def require_nonempty_string(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{location} must be a non-empty string")
    return value


def plugin_entries(catalog: object, location: str) -> list[dict[str, object]]:
    if not isinstance(catalog, dict) or not isinstance(catalog.get("plugins"), list):
        fail(f"{location} catalog must contain a plugins array")
    plugins = catalog["plugins"]
    if not plugins:
        fail(f"{location} catalog must contain at least one plugin")
    if not all(isinstance(plugin, dict) for plugin in plugins):
        fail(f"{location} catalog plugins must be objects")
    entries = plugins  # type: ignore[assignment]
    names = [
        require_nonempty_string(plugin.get("name"), location) for plugin in entries
    ]
    if len(names) != len(set(names)):
        fail(f"{location} catalog contains duplicate plugin names")
    return entries


def resolve_relative_dir(root: Path, relative: object, location: str) -> Path:
    value = require_nonempty_string(relative, location)
    if not value.startswith("./") or ".." in Path(value).parts:
        fail(f"{location} must be a safe ./ relative directory")
    resolved_root = root.resolve()
    resolved = (root / value).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        fail(f"{location} escapes the marketplace root")
    if not resolved.is_dir():
        fail(f"{location} does not resolve to a directory")
    return resolved


def validate_declared_skills(plugin_root: Path, value: object, location: str) -> None:
    paths = [value] if isinstance(value, str) else value
    if not isinstance(paths, list) or not paths:
        fail(f"{location} must be a path or non-empty path list")
    for index, path in enumerate(paths):
        target = resolve_relative_dir(plugin_root, path, f"{location}[{index}]")
        has_root_skill = (target / "SKILL.md").is_file()
        has_nested_skill = any(
            child.is_dir() and (child / "SKILL.md").is_file()
            for child in target.iterdir()
        )
        if not has_root_skill and not has_nested_skill:
            fail(f"{location}[{index}] contains no loadable SKILL.md")


def validate_catalogs(root: Path) -> None:
    claude = json_file(root, CLAUDE_CATALOG)
    codex = json_file(root, CODEX_CATALOG)
    if not isinstance(claude, dict):
        fail("Claude catalog must be an object")
    if (
        claude.get("$schema")
        != "https://json.schemastore.org/claude-code-marketplace.json"
    ):
        fail("Claude catalog must declare the canonical marketplace schema")
    if claude.get("name") != "heliohq":
        fail("Claude catalog name must be heliohq")
    require_nonempty_string(claude.get("description"), "Claude catalog description")
    owner = claude.get("owner")
    if not isinstance(owner, dict):
        fail("Claude catalog owner must be an object")
    require_nonempty_string(owner.get("name"), "Claude catalog owner name")
    require_nonempty_string(owner.get("email"), "Claude catalog owner email")
    claude_plugins = plugin_entries(claude, "Claude")
    for plugin in claude_plugins:
        name = require_nonempty_string(plugin.get("name"), "Claude plugin name")
        plugin_root = resolve_relative_dir(
            root, plugin.get("source"), f"Claude plugin {name} source"
        )
        if "skills" in plugin:
            validate_declared_skills(
                plugin_root, plugin["skills"], f"Claude plugin {name} skills"
            )

    if not isinstance(codex, dict):
        fail("Codex catalog must be an object")
    if codex.get("name") != "heliohq":
        fail("Codex catalog name must be heliohq")
    interface = codex.get("interface")
    if not isinstance(interface, dict):
        fail("Codex catalog interface must be an object")
    require_nonempty_string(interface.get("displayName"), "Codex displayName")
    codex_plugins = plugin_entries(codex, "Codex")

    claude_matches = [
        plugin for plugin in claude_plugins if plugin.get("name") == "heliox"
    ]
    codex_matches = [
        plugin for plugin in codex_plugins if plugin.get("name") == "heliox"
    ]
    if len(claude_matches) != 1 or len(codex_matches) != 1:
        fail("both catalogs must contain exactly one heliox entry")
    claude_heliox = claude_matches[0]
    codex_heliox = codex_matches[0]
    if claude_heliox.get("source") != "./heliox":
        fail("Claude heliox source must be ./heliox")
    if codex_heliox.get("source") != {"source": "local", "path": "./heliox"}:
        fail("Codex heliox source must be the local ./heliox directory")
    resolve_relative_dir(root, "./heliox", "Codex heliox source")
    policy = codex_heliox.get("policy")
    if policy != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
        fail("Codex heliox policy must retain the reviewed install/auth contract")
    require_nonempty_string(codex_heliox.get("category"), "Codex heliox category")


def validate_manifests(root: Path) -> None:
    claude = json_file(root, CLAUDE_MANIFEST)
    codex = json_file(root, CODEX_MANIFEST)
    if not isinstance(claude, dict) or not isinstance(codex, dict):
        fail("Heliox manifests must be JSON objects")
    shared_fields = (
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
    )
    for field in shared_fields:
        if claude.get(field) != codex.get(field):
            fail(f"Heliox manifests disagree on {field}")
    if claude.get("name") != "heliox":
        fail("Heliox manifest name must be heliox")
    for field in ("description", "homepage", "repository", "license"):
        require_nonempty_string(claude.get(field), f"Heliox manifest {field}")
    author = claude.get("author")
    if not isinstance(author, dict):
        fail("Heliox manifest author must be an object")
    require_nonempty_string(author.get("name"), "Heliox manifest author name")
    require_nonempty_string(author.get("email"), "Heliox manifest author email")
    keywords = claude.get("keywords")
    if (
        not isinstance(keywords, list)
        or not keywords
        or not all(isinstance(keyword, str) and keyword.strip() for keyword in keywords)
    ):
        fail("Heliox manifest keywords must contain non-empty strings")
    if codex.get("skills") != "./skills/":
        fail("Codex Heliox manifest skills must be ./skills/")
    validate_declared_skills(root / "heliox", codex["skills"], "Codex Heliox skills")


def validate_payload_git_modes(root: Path) -> None:
    raw = run_git(
        root,
        "ls-files",
        "-s",
        "-z",
        "--",
        "heliox",
        CLAUDE_CATALOG,
        CODEX_CATALOG,
    )
    entries = [entry for entry in raw.split("\0") if entry]
    if not entries:
        fail("Heliox payload contains no tracked files")
    tracked_paths: set[str] = set()
    for entry in entries:
        try:
            metadata, path = entry.split("\t", 1)
            mode = metadata.split(" ", 1)[0]
        except ValueError:
            fail("git returned malformed Heliox payload metadata")
        tracked_paths.add(path)
        if mode not in {"100644", "100755"}:
            fail(
                f"Heliox payload must contain regular files only: {path} has mode {mode}"
            )
    for catalog in CATALOG_PATHS:
        if catalog not in tracked_paths:
            fail(f"Heliox payload catalog is not tracked: {catalog}")


def validate_skills(root: Path) -> None:
    skills_root = root / "heliox" / "skills"
    try:
        skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    except OSError as error:
        fail(f"Heliox skills directory is unreadable: {error}")
    if not skill_dirs:
        fail("Heliox contains no skills")
    names: list[str] = []
    for skill_dir in skill_dirs:
        path = skill_dir / "SKILL.md"
        if not path.is_file():
            fail(f"{skill_dir.relative_to(root)} is missing SKILL.md")
        try:
            content = path.read_text(encoding="utf-8")
            if not content.startswith("---\n") or "\n---\n" not in content[4:]:
                fail(f"{path.relative_to(root)} must begin with YAML frontmatter")
            frontmatter = content[4:].split("\n---\n", 1)[0]
            document = yaml.safe_load(frontmatter)
        except (OSError, yaml.YAMLError) as error:
            fail(f"{path.relative_to(root)} is invalid YAML/Markdown: {error}")
        if not isinstance(document, dict):
            fail(f"{path.relative_to(root)} must begin with YAML frontmatter")
        name = document.get("name")
        description = document.get("description")
        if not isinstance(name, str) or not name:
            fail(f"{path.relative_to(root)} has no skill name")
        if name != path.parent.name:
            fail(f"{path.relative_to(root)} name must match its directory")
        if not isinstance(description, str) or not description.strip():
            fail(f"{path.relative_to(root)} has no description")
        if document.get("user-invocable") is not False:
            fail(f"{path.relative_to(root)} must set user-invocable: false")
        metadata = document.get("metadata")
        requires = metadata.get("requires") if isinstance(metadata, dict) else None
        bins = requires.get("bins") if isinstance(requires, dict) else None
        if (
            not isinstance(bins, list)
            or not bins
            or not all(isinstance(binary, str) and binary.strip() for binary in bins)
        ):
            fail(
                f"{path.relative_to(root)} metadata.requires.bins must contain non-empty strings"
            )
        names.append(name)
    if len(names) != len(set(names)):
        fail("Heliox contains duplicate skill names")
    for required in ("apps", "artifact"):
        if required not in names:
            fail(f"Heliox must preserve the {required} skill")


def changed_paths(root: Path, base_ref: str) -> list[str]:
    return [
        path
        for path in run_git(
            root, "diff", "--name-only", f"{base_ref}...HEAD"
        ).splitlines()
        if path
    ]


def is_payload_path(path: str) -> bool:
    return path.startswith("heliox/") or path in CATALOG_PATHS


def heliox_catalog_entry(document: object, location: str) -> dict[str, object]:
    entries = plugin_entries(document, location)
    matches = [entry for entry in entries if entry.get("name") == "heliox"]
    if len(matches) != 1:
        fail(f"{location} must contain exactly one heliox entry")
    return matches[0]


def heliox_changed(root: Path, base_ref: str, changes: list[str]) -> bool:
    if any(path.startswith("heliox/") for path in changes):
        return True
    for path in CATALOG_PATHS:
        if path not in changes:
            continue
        if heliox_catalog_entry(json_file(root, path), path) != heliox_catalog_entry(
            json_at_ref(root, base_ref, path), f"{path} at {base_ref}"
        ):
            return True
    return False


def catalog_without_heliox(document: object, location: str) -> object:
    if not isinstance(document, dict) or not isinstance(document.get("plugins"), list):
        fail(f"{location} must contain a plugins array")
    normalized = copy.deepcopy(document)
    normalized["plugins"] = [
        plugin
        for plugin in normalized["plugins"]
        if not isinstance(plugin, dict) or plugin.get("name") != "heliox"
    ]
    return normalized


def validate_automated_catalog_preservation(root: Path, base_ref: str) -> None:
    for path in sorted(CATALOG_PATHS):
        current = json_file(root, path)
        base = json_at_ref(root, base_ref, path)
        if catalog_without_heliox(current, path) != catalog_without_heliox(
            base, f"{path} at {base_ref}"
        ):
            fail(
                f"automated Heliox publication may only replace the {path} heliox entry"
            )


def validate_merge_order(
    root: Path,
    base_ref: str,
    head_ref: str,
    repository: str,
    head_repository: str,
    event_name: str,
) -> None:
    head_version, head_order = versions(root)
    _, base_order = versions(root, base_ref)
    changes = changed_paths(root, base_ref)
    changed = heliox_changed(root, base_ref, changes)

    if changed and head_order <= base_order:
        fail(
            "Heliox payload changes must strictly increase the version relative to current base"
        )
    if not changed and head_order != base_order:
        fail("Heliox version changed without a payload change")

    if changed and event_name == "pull_request_target":
        if head_repository != repository:
            fail("Heliox publication must use a same-repository branch")
        if head_ref != f"{PUBLISH_PREFIX}{head_version}":
            fail(f"publish branch must be named {PUBLISH_PREFIX}{head_version}")
    if changed:
        validate_automated_catalog_preservation(root, base_ref)
        unexpected = [path for path in changes if not is_payload_path(path)]
        if unexpected:
            fail(
                "Heliox publication changes files outside its payload: "
                + ", ".join(unexpected)
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--head-repository", required=True)
    parser.add_argument(
        "--event-name", choices=("pull_request_target", "push"), required=True
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    try:
        validate_payload_git_modes(root)
        versions(root)
        validate_catalogs(root)
        validate_manifests(root)
        validate_skills(root)
        validate_merge_order(
            root,
            args.base_ref,
            args.head_ref,
            args.repository,
            args.head_repository,
            args.event_name,
        )
    except ValidationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print("Marketplace and Heliox publication order are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

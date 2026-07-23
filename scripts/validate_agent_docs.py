#!/usr/bin/env python3
"""Validate documented commands and toolchain claims against repository contracts."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]

LOCAL_COMMANDS = ("build", "test", "clippy", "fmt")
CI_COMMANDS = ("build-ci", "test-ci", "clippy-ci", "fmt-check")
CAPABILITY_COMMANDS = (
    "check-boundaries",
    "check-cargo-contract",
    "verify-capabilities-ci",
)
REQUIRED_RECIPES = (
    *LOCAL_COMMANDS,
    "run-example",
    "list-examples",
    *CI_COMMANDS,
    *CAPABILITY_COMMANDS,
    "update-cargo-contract",
    "validate-agent-docs",
    "check-clippy-policy",
    "clippy-strict",
)

STATIC_REQUIRED_TEXT: Dict[str, Sequence[str]] = {
    "AGENTS.md": (
        "just run-example demo",
        "just run-example slider_styled_demo",
        "just list-examples",
        *(f"just {target}" for target in CI_COMMANDS),
        *(f"just {target}" for target in CAPABILITY_COMMANDS),
        "just update-cargo-contract",
        "GitHub Actions uses `gpui/runtime_shaders` on hosted macOS runners",
        "The `Justfile` is the canonical command source",
        "clippy-strict",
    ),
    "CLAUDE.md": (
        "just run-example demo",
        "just run-example slider_styled_demo",
        "just list-examples",
        *(f"just {target}" for target in CI_COMMANDS),
        *(f"just {target}" for target in CAPABILITY_COMMANDS),
        "just update-cargo-contract",
        "GitHub Actions uses `gpui/runtime_shaders` on hosted macOS runners",
        "The `Justfile` is the canonical command source",
        "clippy-strict",
    ),
    "CONTRIBUTING.md": ("just update-cargo-contract",),
    ".github/workflows/ci.yml": (
        *(f"target: {target}" for target in CI_COMMANDS),
        *(f"just {target}" for target in CAPABILITY_COMMANDS),
        "run: just $",
        "run: just validate-agent-docs",
        "run: just check-clippy-policy",
    ),
}

REQUIRED_LINES: Dict[str, Sequence[str]] = {
    "AGENTS.md": tuple(f"- `just {target}`" for target in LOCAL_COMMANDS),
}

FORBIDDEN_TEXT: Dict[str, Sequence[str]] = {
    "README.md": (
        "rust-nightly",
        "Rust nightly",
        "cargo +nightly",
    ),
}


def required_text(rust_version: str) -> Dict[str, Sequence[str]]:
    return {
        **STATIC_REQUIRED_TEXT,
        "README.md": (
            f"rust-{rust_version}%2B",
            f"Rust {rust_version} or newer",
            "just list-examples",
        ),
    }


def cargo_package(root: Path) -> dict:
    metadata = json.loads(
        subprocess.check_output(
            ["cargo", "metadata", "--no-deps", "--format-version", "1"],
            cwd=root,
            text=True,
        )
    )
    return next(
        package for package in metadata["packages"] if package["name"] == "adabraka-ui"
    )


def validate_text(
    label: str,
    text: str,
    required: Iterable[str] = (),
    required_lines: Iterable[str] = (),
    forbidden: Iterable[str] = (),
) -> List[str]:
    errors = []
    lines = set(text.splitlines())

    for fragment in required:
        if fragment not in text:
            errors.append(f"{label}: missing required text: {fragment}")
    for line in required_lines:
        if line not in lines:
            errors.append(f"{label}: missing required line: {line}")
    for fragment in forbidden:
        if fragment in text:
            errors.append(f"{label}: contains forbidden text: {fragment}")

    return errors


def documented_errors(root: Path, rust_version: str) -> List[str]:
    errors = []
    required = required_text(rust_version)
    paths = set(required) | set(REQUIRED_LINES) | set(FORBIDDEN_TEXT)
    for relative_path in sorted(paths):
        path = root / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: file does not exist")
            continue
        errors.extend(
            validate_text(
                relative_path,
                path.read_text(),
                required=required.get(relative_path, ()),
                required_lines=REQUIRED_LINES.get(relative_path, ()),
                forbidden=FORBIDDEN_TEXT.get(relative_path, ()),
            )
        )
    return errors


def recipe_errors(root: Path, recipes: Optional[Iterable[str]] = None) -> List[str]:
    if recipes is None:
        summary = subprocess.check_output(
            ["just", "--summary"], cwd=root, text=True
        )
        recipes = summary.split()

    available = set(recipes)
    return [
        f"Justfile: missing recipe: {recipe}"
        for recipe in REQUIRED_RECIPES
        if recipe not in available
    ]


def main() -> None:
    package = cargo_package(ROOT)
    rust_version = package.get("rust_version")
    errors = []
    if not rust_version:
        errors.append("Cargo.toml: package rust-version is required")
    else:
        errors.extend(documented_errors(ROOT, rust_version))
    errors.extend(recipe_errors(ROOT))
    if errors:
        print("Agent documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Agent documentation commands and toolchain claims are consistent")


if __name__ == "__main__":
    main()

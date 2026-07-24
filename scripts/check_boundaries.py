#!/usr/bin/env python3
"""Enforce dependency direction between canonical capability modules."""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = ROOT / "src" / "capabilities"
ALLOWED = {
    "foundation": set(),
    "layout": {"foundation", "primitives"},
    "motion": {"foundation"},
    "primitives": {"foundation", "motion"},
    "scroll": {"foundation", "layout", "motion", "primitives"},
    "overlays": {"foundation", "layout", "motion", "primitives", "scroll"},
    "controls": {
        "foundation",
        "layout",
        "motion",
        "primitives",
        "scroll",
        "overlays",
    },
    "navigation": {"foundation", "motion", "primitives", "scroll", "controls"},
    "data": {"foundation", "primitives", "scroll", "controls"},
    "content": {"foundation", "primitives"},
    "editor": {"foundation", "scroll"},
    "media": {"foundation", "primitives", "scroll"},
    "effects": {"foundation", "motion", "primitives"},
}
LEGACY = {
    "components",
    "display",
    "charts",
    "navigation",
    "overlays",
    "theme",
    "animate",
    "animated_state",
    "animation_coordinator",
    "animations",
    "content_transition",
    "gestures",
    "gpui_ext",
    "layout",
    "responsive",
    "scroll_physics",
    "spring",
    "styled_ext",
    "transitions",
    "virtual_list",
    "fonts",
    "icon_config",
    "http",
    "initialization",
    "text_util",
    "util",
}
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|::|[{},;*]")
TEST_MODULE = re.compile(
    r"#\s*\[\s*cfg\s*\(\s*(?:test|all\s*\(\s*test\b[^)]*\))\s*\)\s*\]"
    r"\s*mod\s+tests\s*\{"
)


class Token(NamedTuple):
    value: str
    line: int


class Segment(NamedTuple):
    value: str
    line: int


class Violation(NamedTuple):
    line: int
    message: str


def _mask_non_code(source: str) -> str:
    """Replace comments and literals with spaces while preserving line numbers."""
    chars = list(source)
    index = 0
    while index < len(chars):
        if source.startswith("//", index):
            end = source.find("\n", index)
            end = len(chars) if end == -1 else end
            for offset in range(index, end):
                chars[offset] = " "
            index = end
            continue

        if source.startswith("/*", index):
            depth = 1
            end = index + 2
            while end < len(chars) and depth:
                if source.startswith("/*", end):
                    depth += 1
                    end += 2
                elif source.startswith("*/", end):
                    depth -= 1
                    end += 2
                else:
                    end += 1
            for offset in range(index, end):
                if chars[offset] != "\n":
                    chars[offset] = " "
            index = end
            continue

        raw = re.match(r'(?:br|r)(?P<hashes>#{0,255})"', source[index:])
        if raw:
            terminator = '"' + raw.group("hashes")
            end = source.find(terminator, index + raw.end())
            end = len(chars) if end == -1 else end + len(terminator)
            for offset in range(index, end):
                if chars[offset] != "\n":
                    chars[offset] = " "
            index = end
            continue

        if chars[index] == '"':
            end = index + 1
            while end < len(chars):
                if chars[end] == "\\":
                    end += 2
                    continue
                end += 1
                if chars[end - 1] == '"':
                    break
            for offset in range(index, min(end, len(chars))):
                if chars[offset] != "\n":
                    chars[offset] = " "
            index = end
            continue

        index += 1
    return "".join(chars)


def _production_source(source: str) -> str:
    """Mask test-only ``mod tests`` blocks without hiding later production code."""
    masked = _mask_non_code(source)
    chars = list(source)
    for match in TEST_MODULE.finditer(masked):
        depth = 0
        for index in range(match.end() - 1, len(masked)):
            if masked[index] == "{":
                depth += 1
            elif masked[index] == "}":
                depth -= 1
                if depth == 0:
                    for offset in range(match.start(), index + 1):
                        if chars[offset] != "\n":
                            chars[offset] = " "
                    break
    return "".join(chars)


def _tokens(source: str) -> list[Token]:
    masked = _mask_non_code(source)
    return [Token(match.group(), masked.count("\n", 0, match.start()) + 1) for match in TOKEN.finditer(masked)]


def _parse_tree(
    tokens: list[Token], index: int, prefix: tuple[Segment, ...] = ()
) -> tuple[list[tuple[Segment, ...]], int]:
    if index >= len(tokens):
        return [], index

    if tokens[index].value == "{":
        paths = []
        index += 1
        while index < len(tokens) and tokens[index].value != "}":
            branch, index = _parse_tree(tokens, index, prefix)
            paths.extend(branch)
            if index < len(tokens) and tokens[index].value == ",":
                index += 1
        return paths, min(index + 1, len(tokens))

    segments = list(prefix)
    while index < len(tokens):
        token = tokens[index]
        if token.value in {"self", "super", "crate", "*"} or token.value.isidentifier():
            if token.value != "self":
                segments.append(Segment(token.value, token.line))
            index += 1
        else:
            break

        if index >= len(tokens) or tokens[index].value != "::":
            break
        index += 1
        if index < len(tokens) and tokens[index].value == "{":
            return _parse_tree(tokens, index, tuple(segments))

    if index < len(tokens) and tokens[index].value == "as":
        index += 2
    return ([tuple(segments)] if segments else []), index


def _crate_paths(source: str) -> list[tuple[Segment, ...]]:
    tokens = _tokens(source)
    paths = []
    for index, token in enumerate(tokens):
        if token.value != "crate" or index + 1 >= len(tokens) or tokens[index + 1].value != "::":
            continue
        parsed, _ = _parse_tree(tokens, index)
        paths.extend(parsed)
    return paths


def _super_path_errors(path: Path, owner: str, source: str) -> list[Violation]:
    """Reject parent-relative paths in production capability source.

    The boundary rule is deliberately syntactic: production code must use the
    canonical ``crate::capabilities::...`` route, not ``super::``. This catches
    imports, type paths, expressions, and macro arguments without trying to
    reconstruct Rust's nested module tree.
    """
    tokens = _tokens(source)
    errors = []
    for index, token in enumerate(tokens[:-1]):
        if token.value != "super" or tokens[index + 1].value != "::":
            continue
        previous = tokens[index - 1].value if index else ""
        grandparent = tokens[index - 2].value if index > 1 else ""
        if previous == "::" and grandparent != "self":
            continue
        errors.append(
            Violation(
                token.line,
                f"{path}:{token.line}: {owner} uses a forbidden relative super:: path",
            )
        )
    return errors


def _edge_violation(
    path: Path, owner: str, path_segments: tuple[Segment, ...]
) -> Violation | None:
    """Return the boundary violation message for a resolved absolute path.

    A path is resolved to ``crate::<root>[::<target>]``. Legacy facades are
    flagged when ``<root>`` itself is a legacy module; capability edges are
    flagged when ``<root>`` is ``capabilities`` and ``<target>`` is neither the
    owner nor an allowed dependency. Returns ``None`` for compliant paths.
    """
    if len(path_segments) < 2:
        return None
    root = path_segments[1]
    if root.value in LEGACY:
        return Violation(
            root.line,
            f"{path}:{root.line}: {owner} imports through a legacy facade",
        )
    if root.value != "capabilities" or len(path_segments) < 3:
        return None
    target = path_segments[2]
    if target.value != owner and target.value not in ALLOWED[owner]:
        return Violation(
            target.line,
            f"{path}:{target.line}: rejected edge {owner} -> {target.value}",
        )
    return None


def check_source(path: Path, owner: str, source: str) -> list[str]:
    production_source = _production_source(source)
    violations = _super_path_errors(path, owner, production_source)
    for path_segments in _crate_paths(production_source):
        violation = _edge_violation(path, owner, path_segments)
        if violation:
            violations.append(violation)
    violations.sort(key=lambda violation: (violation.line, violation.message))
    return list(dict.fromkeys(violation.message for violation in violations))


def main() -> None:
    errors = []
    owners = set(ALLOWED)
    actual_directories = {path.name for path in CAPABILITIES.iterdir() if path.is_dir()}
    if actual_directories != owners:
        errors.append(
            f"src/capabilities: capability set differs: expected {sorted(owners)}, "
            f"found {sorted(actual_directories)}"
        )

    for path in sorted(CAPABILITIES.rglob("*.rs")):
        owner = path.relative_to(CAPABILITIES).parts[0]
        if owner in owners:
            errors.extend(check_source(path.relative_to(ROOT), owner, path.read_text()))

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("Capability boundaries OK")


if __name__ == "__main__":
    main()

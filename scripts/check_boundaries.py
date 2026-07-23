#!/usr/bin/env python3
"""Enforce dependency direction between canonical capability modules."""

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


class Token(NamedTuple):
    value: str
    line: int


class Segment(NamedTuple):
    value: str
    line: int


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


def check_source(path: Path, owner: str, source: str) -> list[str]:
    production_source = source.split("\n#[cfg(test)]\nmod tests", 1)[0]
    errors = []
    for path_segments in _crate_paths(production_source):
        if len(path_segments) < 2:
            continue
        root = path_segments[1]
        if root.value in LEGACY:
            errors.append(f"{path}:{root.line}: {owner} imports through a legacy facade")
            continue
        if root.value != "capabilities" or len(path_segments) < 3:
            continue
        target = path_segments[2]
        if target.value != owner and target.value not in ALLOWED[owner]:
            errors.append(f"{path}:{target.line}: rejected edge {owner} -> {target.value}")
    return list(dict.fromkeys(errors))


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

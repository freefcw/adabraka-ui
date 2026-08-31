#!/usr/bin/env python3
"""Verify Cargo features and examples against the compatibility snapshot."""

import argparse
import json
import subprocess
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "scripts" / "cargo_contract.json"


def cargo_contract() -> dict:
    metadata = json.loads(
        subprocess.check_output(
            ["cargo", "metadata", "--no-deps", "--format-version", "1"],
            cwd=ROOT,
            text=True,
        )
    )
    package = next(
        package for package in metadata["packages"] if package["name"] == "fc-ui"
    )
    return {
        "features": package["features"],
        "examples": {
            target["name"]: target.get("required-features", [])
            for target in package["targets"]
            if "example" in target["kind"]
        },
    }


def contract_counts(contract: dict) -> tuple[int, int]:
    return len(contract["features"]), len(contract["examples"])


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update",
        action="store_true",
        help="write the current Cargo metadata as the reviewed compatibility snapshot",
    )
    args = parser.parse_args(argv)
    actual = cargo_contract()
    feature_count, example_count = contract_counts(actual)

    if args.update:
        SNAPSHOT.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
        print(
            "Cargo contract updated: "
            f"{feature_count} features and {example_count} examples"
        )
        return

    expected = json.loads(SNAPSHOT.read_text())
    if actual != expected:
        print("Cargo compatibility contract changed:")
        for key in ("features", "examples"):
            if actual[key] != expected[key]:
                print(f"- {key}: expected {len(expected[key])}, found {len(actual[key])}")
        raise SystemExit(1)

    print(f"Cargo contract OK: {feature_count} features and {example_count} examples")


if __name__ == "__main__":
    main()

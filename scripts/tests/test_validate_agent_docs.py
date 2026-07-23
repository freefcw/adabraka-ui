import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "validate_agent_docs", ROOT / "scripts" / "validate_agent_docs.py"
)
VALIDATE_AGENT_DOCS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATE_AGENT_DOCS)


class ValidateAgentDocsTests(unittest.TestCase):
    def test_reads_rust_version_from_cargo_metadata(self) -> None:
        metadata = {"packages": [{"name": "adabraka-ui", "rust_version": "1.86"}]}

        with patch.object(
            VALIDATE_AGENT_DOCS.subprocess,
            "check_output",
            return_value=json.dumps(metadata),
        ):
            package = VALIDATE_AGENT_DOCS.cargo_package(Path("/workspace"))

        self.assertEqual(package["rust_version"], "1.86")

    def test_derives_readme_requirements_from_cargo_rust_version(self) -> None:
        required = VALIDATE_AGENT_DOCS.required_text("1.86")["README.md"]

        self.assertIn("rust-1.86%2B", required)
        self.assertIn("Rust 1.86 or newer", required)
        self.assertNotIn("rust-1.85%2B", required)
        self.assertNotIn("Rust 1.85 or newer", required)

    def test_reports_the_document_and_missing_requirement(self) -> None:
        self.assertEqual(
            VALIDATE_AGENT_DOCS.validate_text(
                "README.md",
                "current content",
                required=("Rust 1.85 or newer",),
            ),
            ["README.md: missing required text: Rust 1.85 or newer"],
        )

    def test_rejects_stale_nightly_readme_claims(self) -> None:
        errors = VALIDATE_AGENT_DOCS.validate_text(
            "README.md",
            "Requires Rust nightly. cargo +nightly run --example demo",
            forbidden=("Rust nightly", "cargo +nightly"),
        )

        self.assertEqual(
            errors,
            [
                "README.md: contains forbidden text: Rust nightly",
                "README.md: contains forbidden text: cargo +nightly",
            ],
        )

    def test_accepts_stable_readme_claims(self) -> None:
        self.assertEqual(
            VALIDATE_AGENT_DOCS.validate_text(
                "README.md",
                "Requires Rust 1.85 or newer on the stable toolchain.",
                required=("Rust 1.85 or newer",),
                forbidden=("Rust nightly", "cargo +nightly"),
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "boundaries"
SPEC = importlib.util.spec_from_file_location(
    "check_boundaries", ROOT / "scripts" / "check_boundaries.py"
)
CHECK_BOUNDARIES = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK_BOUNDARIES)


class BoundaryCheckerTests(unittest.TestCase):
    def violations(self, fixture: str, owner: str = "content") -> list[str]:
        source = (FIXTURES / fixture).read_text()
        return CHECK_BOUNDARIES.check_source(Path(fixture), owner, source)

    def violations_for_source(self, path: str, owner: str, source: str) -> list[str]:
        return CHECK_BOUNDARIES.check_source(Path(path), owner, source)

    def test_rejects_direct_legacy_import(self) -> None:
        self.assertEqual(
            self.violations("direct_legacy.rs"),
            ["direct_legacy.rs:1: content imports through a legacy facade"],
        )

    def test_rejects_grouped_legacy_imports(self) -> None:
        self.assertEqual(
            self.violations("grouped_legacy.rs"),
            [
                "grouped_legacy.rs:2: content imports through a legacy facade",
                "grouped_legacy.rs:3: content imports through a legacy facade",
            ],
        )

    def test_rejects_forbidden_grouped_capability_edge(self) -> None:
        self.assertEqual(
            self.violations("forbidden_grouped.rs"),
            ["forbidden_grouped.rs:3: rejected edge content -> overlays"],
        )

    def test_accepts_allowed_grouped_capability_imports(self) -> None:
        self.assertEqual(self.violations("allowed_grouped.rs"), [])

    def test_allows_controls_to_use_shared_layout(self) -> None:
        self.assertEqual(
            self.violations_for_source(
                "controls.rs",
                "controls",
                "use crate::capabilities::layout::VStack;",
            ),
            [],
        )

    def test_rejects_scroll_dependency_from_shared_layout(self) -> None:
        self.assertEqual(
            self.violations_for_source(
                "layout.rs",
                "layout",
                "use crate::capabilities::scroll::scrollbar::Scrollbar;",
            ),
            ["layout.rs:1: rejected edge layout -> scroll"],
        )

    def test_ignores_imports_inside_comments_and_strings(self) -> None:
        self.assertEqual(self.violations("ignored_non_code.rs"), [])

    def test_accepts_nested_grouped_capability_imports(self) -> None:
        self.assertEqual(self.violations("nested_allowed.rs"), [])

    def test_rejects_nested_grouped_capability_edge(self) -> None:
        self.assertEqual(
            self.violations("nested_forbidden.rs"),
            ["nested_forbidden.rs:3: rejected edge content -> overlays"],
        )


if __name__ == "__main__":
    unittest.main()

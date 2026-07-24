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

    def test_ignores_paths_inside_comments_and_strings(self) -> None:
        self.assertEqual(self.violations("ignored_non_code.rs"), [])

    def test_accepts_nested_grouped_capability_imports(self) -> None:
        self.assertEqual(self.violations("nested_allowed.rs"), [])

    def test_rejects_nested_grouped_capability_edge(self) -> None:
        self.assertEqual(
            self.violations("nested_forbidden.rs"),
            ["nested_forbidden.rs:3: rejected edge content -> overlays"],
        )

    def test_rejects_relative_super_path_in_grouped_import(self) -> None:
        self.assertEqual(
            self.violations("relative_super_forbidden.rs"),
            [
                "relative_super_forbidden.rs:1: "
                "content uses a forbidden relative super:: path"
            ],
        )

    def test_rejects_deep_relative_super_path(self) -> None:
        self.assertEqual(
            self.violations("relative_super_legacy.rs"),
            [
                "relative_super_legacy.rs:1: "
                "content uses a forbidden relative super:: path"
            ],
        )

    def test_rejects_intra_module_relative_super_paths(self) -> None:
        self.assertEqual(
            self.violations("relative_super_intra_module.rs", "scroll"),
            [
                "relative_super_intra_module.rs:1: "
                "scroll uses a forbidden relative super:: path",
                "relative_super_intra_module.rs:2: "
                "scroll uses a forbidden relative super:: path",
            ],
        )

    def test_rejects_relative_super_paths_outside_imports(self) -> None:
        source = (
            "type Dialog = super::super::overlays::Dialog;\n"
            "fn make() { let _ = super::super::overlays::Dialog; }\n"
            "fn accept() { accept!(super::super::overlays::Dialog); }\n"
        )
        self.assertEqual(
            self.violations_for_source("relative_contexts.rs", "foundation", source),
            [
                "relative_contexts.rs:1: "
                "foundation uses a forbidden relative super:: path",
                "relative_contexts.rs:2: "
                "foundation uses a forbidden relative super:: path",
                "relative_contexts.rs:3: "
                "foundation uses a forbidden relative super:: path",
            ],
        )

    def test_rejects_self_prefixed_relative_super_path(self) -> None:
        self.assertEqual(
            self.violations_for_source(
                "self_super.rs",
                "foundation",
                "use self::super::super::overlays::Dialog;",
            ),
            [
                "self_super.rs:1: "
                "foundation uses a forbidden relative super:: path"
            ],
        )

    def test_ignores_relative_super_paths_inside_test_module(self) -> None:
        source = (
            "#[cfg(test)]\n"
            "mod tests {\n"
            "    use super::*;\n"
            "    fn helper() { let _ = super::Dialog; }\n"
            "}\n"
        )
        self.assertEqual(
            self.violations_for_source("test_module.rs", "foundation", source), []
        )

    def test_ignores_relative_super_paths_inside_feature_gated_test_module(self) -> None:
        source = (
            "#[cfg(all(test, feature = \"demo\"))]\n"
            "mod tests {\n"
            "    use super::*;\n"
            "}\n"
        )
        self.assertEqual(
            self.violations_for_source("feature_test_module.rs", "foundation", source), []
        )

    def test_checks_non_test_module_named_tests(self) -> None:
        source = (
            "#[cfg(not(test))]\n"
            "mod tests {\n"
            "    use super::super::overlays::Dialog;\n"
            "}\n"
        )
        self.assertEqual(
            self.violations_for_source("non_test_module.rs", "foundation", source),
            [
                "non_test_module.rs:3: "
                "foundation uses a forbidden relative super:: path"
            ],
        )

    def test_checks_production_code_after_test_module(self) -> None:
        source = (
            "#[cfg(test)]\n"
            "mod tests {\n"
            "    use super::*;\n"
            "}\n"
            "\n"
            "use crate::capabilities::overlays::Dialog;\n"
            "type RelativeDialog = super::super::overlays::Dialog;\n"
        )
        self.assertEqual(
            self.violations_for_source("after_tests.rs", "foundation", source),
            [
                "after_tests.rs:6: rejected edge foundation -> overlays",
                "after_tests.rs:7: "
                "foundation uses a forbidden relative super:: path",
            ],
        )


if __name__ == "__main__":
    unittest.main()

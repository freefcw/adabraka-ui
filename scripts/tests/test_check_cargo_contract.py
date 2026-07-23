import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_cargo_contract", ROOT / "scripts" / "check_cargo_contract.py"
)
CHECK_CARGO_CONTRACT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK_CARGO_CONTRACT)


CONTRACT = {
    "features": {"audio": ["rodio"], "default": []},
    "examples": {"audio_player_demo": ["audio"], "demo": []},
}


def cargo_metadata(contract: dict) -> str:
    return json.dumps(
        {
            "packages": [
                {
                    "name": "adabraka-ui",
                    "features": contract["features"],
                    "targets": [
                        {
                            "name": name,
                            "required-features": required_features,
                            "kind": ["example"],
                        }
                        for name, required_features in contract["examples"].items()
                    ],
                }
            ]
        }
    )


class CargoContractTests(unittest.TestCase):
    def test_check_reports_counts_from_the_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "cargo_contract.json"
            snapshot.write_text(json.dumps(CONTRACT))
            output = io.StringIO()

            with (
                patch.object(CHECK_CARGO_CONTRACT, "SNAPSHOT", snapshot),
                patch.object(
                    CHECK_CARGO_CONTRACT.subprocess,
                    "check_output",
                    return_value=cargo_metadata(CONTRACT),
                ),
                contextlib.redirect_stdout(output),
            ):
                CHECK_CARGO_CONTRACT.main([])

        self.assertIn("Cargo contract OK: 2 features and 2 examples", output.getvalue())

    def test_update_writes_the_current_metadata_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "cargo_contract.json"
            output = io.StringIO()

            with (
                patch.object(CHECK_CARGO_CONTRACT, "SNAPSHOT", snapshot),
                patch.object(
                    CHECK_CARGO_CONTRACT.subprocess,
                    "check_output",
                    return_value=cargo_metadata(CONTRACT),
                ),
                contextlib.redirect_stdout(output),
            ):
                CHECK_CARGO_CONTRACT.main(["--update"])

            self.assertEqual(json.loads(snapshot.read_text()), CONTRACT)

        self.assertIn(
            "Cargo contract updated: 2 features and 2 examples", output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()

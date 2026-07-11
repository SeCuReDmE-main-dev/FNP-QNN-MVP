import json
import unittest
from pathlib import Path

from core.education_manifest import list_lab_manifests
from core.education_run_contract import build_education_run_contract


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "education"


def _fixture_path(input_profile: str) -> Path:
    prefix = "fixture:education."
    if not input_profile.startswith(prefix):
        raise ValueError(f"Unsupported education fixture profile: {input_profile}")
    return FIXTURE_ROOT / f"{input_profile[len(prefix):]}.json"


def _replay_fixture(fixture: dict[str, object]):
    return build_education_run_contract(
        lab_id=fixture["lab_id"],
        seed=fixture["seed"],
        state=fixture["state"],
        completed_steps=fixture["completed_steps"],
        total_steps=fixture["total_steps"],
        trace_labels=tuple(fixture["trace_labels"]),
        export_status=fixture["export_status"],
        rejection_reason=fixture.get("rejection_reason"),
    )


class EducationReplayTests(unittest.TestCase):
    def test_every_approved_manifest_has_a_matching_fixture(self):
        for manifest in list_lab_manifests():
            with self.subTest(lab_id=manifest.lab_id):
                path = _fixture_path(manifest.input_profile)
                self.assertTrue(path.is_file(), path)
                fixture = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(fixture["lab_id"], manifest.lab_id)

    def test_every_public_fixture_replays_to_identical_contract_json(self):
        for manifest in list_lab_manifests():
            with self.subTest(lab_id=manifest.lab_id):
                fixture = json.loads(_fixture_path(manifest.input_profile).read_text(encoding="utf-8"))
                first = _replay_fixture(fixture).to_json()
                second = _replay_fixture(fixture).to_json()
                self.assertEqual(first, second)
                self.assertEqual(json.loads(first)["lab_id"], manifest.lab_id)

    def test_fixture_catalog_is_closed_to_unapproved_files(self):
        approved_paths = {_fixture_path(manifest.input_profile) for manifest in list_lab_manifests()}
        actual_paths = set(FIXTURE_ROOT.glob("*.json"))
        self.assertEqual(actual_paths, approved_paths)


if __name__ == "__main__":
    unittest.main()

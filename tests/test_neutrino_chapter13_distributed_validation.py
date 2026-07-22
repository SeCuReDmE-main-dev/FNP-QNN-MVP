from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from core.neutrino_admission_gate import neutrino_guardrail_check
from core.neutrino_chapter13_distributed_validation import neutrino_chapter13_distributed_worker
from fnp_qnn_cli.main import main


ROOT = Path(__file__).resolve().parents[1]


def _packet() -> dict:
    packet = json.loads((ROOT / "tests/fixtures/neutrino_chapter12_valid_admission.json").read_text(encoding="utf-8"))
    overlay = json.loads((ROOT / "tests/fixtures/neutrino_chapter13_profile_overlay.json").read_text(encoding="utf-8"))
    packet["LexPacket_neutrino"].update(overlay)
    packet["chapter13_worker_request"] = {
        "run_profile": "run_1_all_valid",
        "worker_index": 0,
        "shard_count": 67,
        "worker_mode": "valid",
        "tasks": [{"task_id": f"run1-worker0-task{index}"} for index in range(4)],
        "task_manifest_hash": "a" * 64,
        "expected_outcome": "accepted",
        "physical_model_validated": False,
        "real_detection_claim": False,
    }
    return packet


def _write_runtime(path: Path, *, p114_action: str = "respond_with_confidence", stable_p046: bool = True) -> None:
    package = path / "ffed_runtime"
    package.mkdir(parents=True)
    security = path / "security"
    security.mkdir(parents=True)
    (security / "__init__.py").write_text("RUNTIME_MARKER = True\n", encoding="utf-8")
    (security / "integrity.py").write_text(
        """def verify_plugin_integrity(plugin_id):
    return {"valid": True, "plugin_id": plugin_id, "errors": []}
""",
        encoding="utf-8",
    )
    source = f'''from security import RUNTIME_MARKER

def run_plugin(plugin_id, config):
    assert RUNTIME_MARKER
    if plugin_id == "p114_ffed_neutrosophic_consensus":
        return {{
            "status": "success", "plugin_id": plugin_id,
            "outputs": {{"action": "{p114_action}", "consensus": {{"truth": 0.9, "indeterminacy": 0.05, "falsity": 0.05}}}},
            "metrics": {{}}, "metadata": {{}}
        }}
    clamp = 0 if {stable_p046!r} else 3
    maximum = 12.5 if {stable_p046!r} else 1000000.0
    return {{
        "status": "success", "plugin_id": plugin_id,
        "outputs": {{"trajectory": [[0.1, 1.0, 0.0], [0.2, 1.1, 0.1], [0.3, 1.2, 0.2], [0.4, 1.3, 0.3]]}},
        "metrics": {{"clamp_hit_count": clamp, "nonfinite_reset_count": 0, "trajectory_max_abs": maximum, "simulation_stable": {stable_p046!r}}},
        "metadata": {{}}
    }}
'''
    (package / "__init__.py").write_text(source, encoding="utf-8")


def _assert_no_fnp_output(testcase: unittest.TestCase, value) -> None:
    forbidden = {"D_f", "D_f_hat", "dF", "i_fractal_candidate"}
    if isinstance(value, dict):
        testcase.assertTrue(forbidden.isdisjoint(value))
        for nested in value.values():
            _assert_no_fnp_output(testcase, nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_no_fnp_output(testcase, nested)


class Chapter13DistributedValidationTests(unittest.TestCase):
    def test_admission_preserves_distributed_profile(self):
        result = neutrino_guardrail_check(_packet())
        self.assertTrue(result["can_compute_fnp"])
        profile = result["admitted_chapter13_distributed_validation"]
        self.assertEqual(profile["DistributedValidationContract_13"]["worker_count_per_run"], 67)

    def test_valid_worker_passes_synthia_p114_and_reference_readout(self):
        with tempfile.TemporaryDirectory() as tmp:
            _write_runtime(Path(tmp))
            result = neutrino_chapter13_distributed_worker(_packet(), pluginpack_path=tmp)
        self.assertTrue(result["success"])
        self.assertEqual(result["decision"]["status"], "accepted")
        self.assertTrue(result["fnp_computation_performed"])
        self.assertEqual(result["execution_permission"]["task_count"], 4)
        self.assertFalse(result["physical_model_validated"])

    def test_p114_clarification_and_rejection_stop_before_fnp(self):
        for action, expected in (("ask_clarification", "suspended"), ("escalate_or_reject", "rejected")):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as tmp:
                _write_runtime(Path(tmp), p114_action=action)
                result = neutrino_chapter13_distributed_worker(_packet(), pluginpack_path=tmp)
                self.assertEqual(result["decision"]["status"], expected)
                self.assertFalse(result["fnp_computation_performed"])
                _assert_no_fnp_output(self, result)

    def test_bounded_chaos_returns_replayable_fault_schedule(self):
        packet = _packet()
        packet["chapter13_worker_request"]["worker_mode"] = "bounded_chaos"
        packet["chapter13_worker_request"]["expected_outcome"] = "fault_schedule_ready"
        with tempfile.TemporaryDirectory() as tmp:
            _write_runtime(Path(tmp))
            first = neutrino_chapter13_distributed_worker(packet, pluginpack_path=tmp)
            second = neutrino_chapter13_distributed_worker(packet, pluginpack_path=tmp)
        self.assertEqual(first["decision"]["status"], "fault_schedule_ready")
        self.assertEqual(first["p046_schedule"]["schedule_sha256"], second["p046_schedule"]["schedule_sha256"])
        self.assertEqual(len(first["p046_schedule"]["instructions"]), 4)
        self.assertFalse(first["fnp_computation_performed"])

    def test_saturated_p046_is_blocked(self):
        packet = _packet()
        packet["chapter13_worker_request"]["worker_mode"] = "bounded_chaos"
        with tempfile.TemporaryDirectory() as tmp:
            _write_runtime(Path(tmp), stable_p046=False)
            result = neutrino_chapter13_distributed_worker(packet, pluginpack_path=tmp)
        self.assertEqual(result["decision"]["status"], "blocked")
        self.assertIn("p046_clamp_detected", result["decision"]["reason_codes"])
        self.assertIn("p046_simulation_not_stable", result["decision"]["reason_codes"])
        self.assertFalse(result["fnp_computation_performed"])

    def test_invalid_worker_contract_blocks(self):
        packet = _packet()
        packet["chapter13_worker_request"]["worker_index"] = 67
        packet["chapter13_worker_request"]["task_manifest_hash"] = "not-a-hash"
        result = neutrino_chapter13_distributed_worker(packet)
        self.assertIn("invalid_worker_index", result["decision"]["reason_codes"])
        self.assertIn("invalid_task_manifest_hash", result["decision"]["reason_codes"])

    def test_cli_returns_same_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            _write_runtime(temporary)
            input_path = temporary / "input.json"
            input_path.write_text(json.dumps(_packet()), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main([
                    "--json", "neutrino", "chapter13-distributed-worker",
                    "--input", str(input_path), "--pluginpack-path", str(temporary),
                ])
        self.assertEqual(exit_code, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["schema_version"], "fnp.neutrino_chapter13_distributed_worker.v1")
        self.assertEqual(result["decision"]["status"], "accepted")

    def test_lightweight_sandbox_runner_avoids_optional_api_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            temporary = Path(tmp)
            _write_runtime(temporary)
            input_path = temporary / "input.json"
            input_path.write_text(json.dumps(_packet()), encoding="utf-8")
            process = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/run_chapter13_distributed_worker.py"),
                    "--input", str(input_path),
                    "--pluginpack-path", str(temporary),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["decision"]["status"], "accepted")


if __name__ == "__main__":
    unittest.main()

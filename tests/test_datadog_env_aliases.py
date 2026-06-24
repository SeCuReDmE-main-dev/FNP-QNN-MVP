import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock


def _load_audit_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "scripts" / "e2b_datadog_audit" / "audit_e2b.py"
    spec = importlib.util.spec_from_file_location("audit_e2b", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DatadogEnvAliasTests(unittest.TestCase):
    def test_e2b_auditor_accepts_dd_env_aliases(self):
        audit_e2b = _load_audit_module()
        env = {
            "DD_API_KEY": "dd-api-key",
            "DD_SITE": "us3.datadoghq.com",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            args = audit_e2b.parse_args(["--no-datadog"])

        self.assertEqual(args.datadog_api_key, "dd-api-key")
        self.assertEqual(args.datadog_site, "us3.datadoghq.com")

    def test_e2b_auditor_prefers_datadog_env_aliases(self):
        audit_e2b = _load_audit_module()
        env = {
            "DATADOG_API_KEY": "datadog-api-key",
            "DATADOG_SITE": "datadoghq.com",
            "DD_API_KEY": "dd-api-key",
            "DD_SITE": "us3.datadoghq.com",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            args = audit_e2b.parse_args(["--no-datadog"])

        self.assertEqual(args.datadog_api_key, "datadog-api-key")
        self.assertEqual(args.datadog_site, "datadoghq.com")

    def test_e2b_auditor_loads_openclaw_env_without_printing_values(self):
        audit_e2b = _load_audit_module()
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("E2B_API_KEY=e2b-secret\nDD_API_KEY=dd-secret\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=True):
                payload = audit_e2b.load_env_file(env_path)

        self.assertTrue(payload["success"])
        self.assertTrue(payload["presence"]["E2B_API_KEY"])
        self.assertTrue(payload["presence"]["DD_API_KEY"])
        self.assertFalse(payload["raw_values_printed"])
        self.assertNotIn("e2b-secret", str(payload))

    def test_e2b_auditor_records_only_qlc_bundle_fingerprint(self):
        audit_e2b = _load_audit_module()
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            bundle_path = Path(tmp) / "bundle.json"
            bundle_path.write_text('{"schema":"ffed.qlc.protection_workflow_bundle.v1"}', encoding="utf-8")
            payload = audit_e2b._fingerprint_file(bundle_path)

        self.assertTrue(payload["present"])
        self.assertIn("sha256", payload)
        self.assertFalse(payload["raw_payload_embedded"])
        self.assertNotIn("protection_workflow", str(payload))


if __name__ == "__main__":
    unittest.main()

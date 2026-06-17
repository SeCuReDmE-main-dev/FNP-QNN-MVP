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


if __name__ == "__main__":
    unittest.main()

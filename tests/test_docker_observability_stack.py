import unittest
from pathlib import Path


class DockerObservabilityStackTests(unittest.TestCase):
    def test_compose_and_datadog_configs_exist(self):
        repo_root = Path(__file__).resolve().parents[1]

        compose_file = repo_root / "docker-compose.yml"
        datadog_vllm_conf = repo_root / "observability" / "datadog" / "agent-conf.d" / "vllm.d" / "conf.yaml"
        datadog_etcd_conf = repo_root / "observability" / "datadog" / "agent-conf.d" / "etcd.d" / "conf.yaml"
        env_example = repo_root / ".env.docker.example"

        self.assertTrue(compose_file.exists(), f"missing compose file: {compose_file}")
        self.assertTrue(datadog_vllm_conf.exists(), f"missing datadog vllm conf: {datadog_vllm_conf}")
        self.assertTrue(datadog_etcd_conf.exists(), f"missing datadog etcd conf: {datadog_etcd_conf}")
        self.assertTrue(env_example.exists(), f"missing docker env example: {env_example}")

        compose_content = compose_file.read_text(encoding="utf-8")
        self.assertIn("datadog-agent:", compose_content)
        self.assertIn("e2b-auditor:", compose_content)
        self.assertIn("vllm:", compose_content)
        self.assertIn("etcd:", compose_content)
        self.assertIn("./observability/datadog/agent-conf.d:/conf.d:ro", compose_content)

        conf_content = datadog_vllm_conf.read_text(encoding="ascii")
        self.assertIn("openmetrics_endpoint: http://vllm:8000/metrics", conf_content)
        self.assertIn("service:fnp-qnn-vllm", conf_content)

        etcd_conf_content = datadog_etcd_conf.read_text(encoding="ascii")
        self.assertIn("prometheus_url: http://etcd:2379/metrics", etcd_conf_content)
        self.assertIn("service:fnp-qnn-etcd", etcd_conf_content)


if __name__ == "__main__":
    unittest.main()

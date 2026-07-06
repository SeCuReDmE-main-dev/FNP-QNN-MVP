import unittest

from fastapi.testclient import TestClient

from api.main import app


class NovakAndersonPhiPiApiTests(unittest.TestCase):
    def test_status_endpoint_returns_bounded_source_backed_payload(self):
        client = TestClient(app)

        response = client.get("/fnp-qnn/novak-anderson/status")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["feature"], "novak-anderson-phi-pi-theorem")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("not physical quantum validation", payload["source_packet"]["research_boundary"])
        self.assertIn("stim_available", payload)

    def test_convergence_endpoint_accepts_bounded_samples(self):
        client = TestClient(app)

        response = client.post(
            "/fnp-qnn/novak-anderson/convergence",
            json={"max_n": 1000, "sample_ns": [2, 10, 100, 1000]},
        )

        self.assertEqual(response.status_code, 200)
        profile = response.json()["profile"]
        self.assertEqual(profile["max_n"], 1000)
        self.assertEqual(profile["rows"][-1]["n"], 1000)
        self.assertTrue(profile["proof_checks"]["pseudopi_2_equals_5_over_phi"])

    def test_convergence_schema_rejects_out_of_bounds_samples(self):
        client = TestClient(app)

        response = client.post(
            "/fnp-qnn/novak-anderson/convergence",
            json={"max_n": 10, "sample_ns": [2, 11]},
        )

        self.assertEqual(response.status_code, 422)

    def test_command_router_exposes_novak_anderson_phi_pi(self):
        client = TestClient(app)

        response = client.post("/commands/novak-anderson-phi-pi", json={"novak_anderson_max_n": 1000})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["type"], "novak-anderson-phi-pi")
        self.assertEqual(payload["data"]["convergence"]["max_n"], 1000)

    def test_execute_command_shim_routes_novak_anderson_phi_pi(self):
        client = TestClient(app)

        response = client.post(
            "/execute-command",
            json={"command": "novak-anderson-phi-pi", "novak_anderson_max_n": 1000},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])


if __name__ == "__main__":
    unittest.main()

import unittest

from fastapi.testclient import TestClient

from api.main import app


class QNNSmokeApiTests(unittest.TestCase):
    def test_qnn_smoke_returns_json_safe_payload(self):
        client = TestClient(app)

        response = client.post("/qnn/smoke", json={"epochs": 4, "test_size": 0.0})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["result"]["backend"], "torch_surrogate")
        self.assertIn("bundle", payload["result"])
        self.assertIsInstance(payload["result"]["bundle"]["transition_matrix"], list)
        self.assertTrue(any(item["candidate"] == "torch_surrogate" for item in payload["benchmark"]))

    def test_qnn_smoke_accepts_neutrobit_basis_opt_in(self):
        client = TestClient(app)

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "state_basis": "neutrobit",
                "puncture_delta": 0.25,
                "observer_strength": 0.5,
                "fractal_dimension": 1.5,
                "fractal_dimension_min": 1.0,
                "fractal_dimension_max": 2.0,
                "fractal_measurement_method": "box-counting-provided",
                "fractal_scale": "api-test",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["result"]["state_basis"], "neutrobit")
        self.assertEqual(payload["result"]["puncture_delta"], 0.25)
        self.assertEqual(payload["result"]["observer_strength"], 0.5)
        self.assertAlmostEqual(payload["result"]["fractal_carrier"]["D_f_hat"], 0.5)
        self.assertIn("not identical to I", payload["result"]["fractal_carrier"]["interpretation"])

    def test_neurobit_api_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/neurobit/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["feature"], "neurobit-gates-and-tunnel-demo")

        gates_response = client.post(
            "/fnp-qnn/neurobit/gates/run",
            json={
                "truth": 0.6,
                "indeterminacy": 0.2,
                "falsity": 0.2,
                "dF": 0.1,
                "state_basis": "neutrobit",
                "puncture_delta": 0.25,
                "observer_strength": 0.5,
                "surface_width": 0.5,
                "surface_height": 0.5,
                "D_f": 1.5,
                "D_min": 1.0,
                "D_max": 2.0,
            },
        )
        self.assertEqual(gates_response.status_code, 200)
        gates_payload = gates_response.json()
        self.assertEqual(gates_payload["status"], "ok")
        self.assertEqual(gates_payload["profile"]["delta_falsity"], 0.1)
        self.assertIn("expectation_vector", gates_payload)
        self.assertEqual(gates_payload["state_basis"], "neutrobit")
        self.assertIsNotNone(gates_payload["punctured_wave"])
        self.assertIsNotNone(gates_payload["punctured_surface"])
        self.assertIsNotNone(gates_payload["observer_effect"])
        self.assertAlmostEqual(gates_payload["fractal_carrier"]["D_f_hat"], 0.5)
        self.assertIn("not identical to I", gates_payload["fractal_carrier"]["interpretation"])

        tunnel_response = client.post(
            "/fnp-qnn/neurobit/tunnel/demo",
            json={"truth": 0.55, "indeterminacy": 0.3, "falsity": 0.15, "data": "smoke"},
        )
        self.assertEqual(tunnel_response.status_code, 200)
        tunnel_payload = tunnel_response.json()
        self.assertEqual(tunnel_payload["status"], "ok")
        self.assertIn("not encryption", tunnel_payload["research_boundary"])

    def test_neurobit_commands_are_available(self):
        client = TestClient(app)

        gates_response = client.post("/commands/neurobit-gates", json={"neurobit": {"truth": 0.5}})
        self.assertEqual(gates_response.status_code, 200)
        self.assertTrue(gates_response.json()["success"])

        tunnel_response = client.post(
            "/commands/neurobit-tunnel-demo",
            json={"neurobit": {"truth": 0.5, "data": "abc"}},
        )
        self.assertEqual(tunnel_response.status_code, 200)
        self.assertTrue(tunnel_response.json()["success"])


if __name__ == "__main__":
    unittest.main()

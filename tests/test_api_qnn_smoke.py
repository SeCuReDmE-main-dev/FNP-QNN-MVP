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


if __name__ == "__main__":
    unittest.main()

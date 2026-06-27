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

    def test_qnn_smoke_plugin_hook_reports_impact_verification(self):
        client = TestClient(app)

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "plugin_hook_enabled": True,
                "plugin_context": {
                    "series": [0.1, 0.3, 0.2, 0.8, 0.4, 0.9],
                    "steps": 120,
                    "n_atoms": 8,
                    "depth": 2,
                    "max_terms": 8,
                    "items": [{"truth": 0.6, "indeterminacy": 0.3, "falsity": 0.1}],
                },
                "cpai_context": {
                    "nodes_visible": 3,
                    "nodes_active": 3,
                    "local_load": 0.82,
                    "route": "qnn-smoke-test",
                },
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertIn("impact_verification", result)
        self.assertIn("plugin_hook_status", result)
        if result["impact_verification"]["activated"]:
            self.assertTrue(result["impact_verification"]["all_expected_plugins_seen"])
            self.assertIsNotNone(result["plugin_fractal_carrier"])
            self.assertEqual(result["cpai_mesh_profile"]["base"], "CPAI mesh")
            self.assertEqual(result["cpai_mesh_profile"]["routing_decision"], "forward_candidate")
            self.assertFalse(result["impact_verification"]["secrets_exposed"])
            self.assertEqual(
                result["plugin_hook_status"]["effective_configs"]["p046_rossler_beaulieu_cubic_framework"]["steps"],
                120,
            )

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

    def test_nidus_idearum_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/nidus/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["feature"], "nidus-idearum-ii-math-layer")

        triplet_response = client.post(
            "/fnp-qnn/nidus/triplet/profile",
            json={"T": 0.6, "I": 0.3, "F": 0.2},
        )
        self.assertEqual(triplet_response.status_code, 200)
        triplet = triplet_response.json()["profile"]
        self.assertGreaterEqual(triplet["score"], -1.0)
        self.assertLessEqual(triplet["score"], 1.0)
        self.assertIn("dynamic triplet", triplet["interpretation"])

        fusion_response = client.post(
            "/fnp-qnn/nidus/fusion/profile",
            json={
                "sources": [
                    {"T": 0.5, "I": 0.1, "F": 0.1, "beta": 2.0},
                    {"T": 0.1, "I": 0.2, "F": 0.6, "intersection_indeterminacy": 0.3},
                ]
            },
        )
        self.assertEqual(fusion_response.status_code, 200)
        components = fusion_response.json()["fusion"]["components"]
        self.assertGreater(
            components["I_system_component"],
            components["base_indeterminacy"],
        )

        mean_response = client.post(
            "/fnp-qnn/nidus/partial-membership/mean",
            json={
                "values": [2.0, 8.0, 5.0, 11.0],
                "memberships": [1.1, 0.4, 1.0, 0.3],
            },
        )
        self.assertEqual(mean_response.status_code, 200)
        mean_payload = mean_response.json()["mean"]
        self.assertTrue(mean_payload["has_overset_membership"])
        self.assertTrue(mean_payload["has_underset_membership"])

    def test_penrose_hameroff_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/penrose-hameroff/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["feature"], "penrose-hameroff-study-layer")

        objective_response = client.post(
            "/fnp-qnn/penrose-hameroff/objective-reduction/profile",
            json={
                "objective_reduction_energy_joule": 1.054571817e-34,
                "reference_time_s": 1.0,
            },
        )
        self.assertEqual(objective_response.status_code, 200)
        objective = objective_response.json()["profile"]
        self.assertAlmostEqual(objective["tau_s"], 1.0)
        self.assertTrue(objective["finite_reduction_threshold"])

        runtime_response = client.post(
            "/fnp-qnn/penrose-hameroff/runtime/profile",
            json={
                "objective_reduction_energy_joule": 1.054571817e-34,
                "coherence_time_s": 1.0,
                "anesthetic_damping": 0.1,
                "microtubule_frequency_hz": 100000000.0,
                "spin_network_vertices": [[1.0, 1.0, 1.0]],
                "memories": [
                    {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                    {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
                ],
            },
        )
        self.assertEqual(runtime_response.status_code, 200)
        profile = runtime_response.json()["profile"]
        self.assertEqual(profile["model"], "penrose_hameroff_runtime_profile_v1")
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertIn("not a consciousness proof", profile["research_boundary"])

    def test_qnn_smoke_accepts_penrose_hameroff_opt_in(self):
        client = TestClient(app)

        baseline = client.post("/qnn/smoke", json={"epochs": 2, "test_size": 0.0})
        self.assertEqual(baseline.status_code, 200)
        baseline_dim = baseline.json()["result"]["feature_dimension"]

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "penrose_hameroff_enabled": True,
                "objective_reduction_energy_joule": 1.054571817e-34,
                "coherence_time_s": 1.0,
                "anesthetic_damping": 0.1,
                "microtubule_frequency_hz": 100000000.0,
                "spin_network_vertices": [[1.0, 1.0, 1.0]],
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertIn("penrose_hameroff_profile", result)
        self.assertGreater(result["feature_dimension"], baseline_dim)
        self.assertEqual(
            result["penrose_hameroff_profile"]["feature_dimension"],
            len(result["penrose_hameroff_profile"]["feature_vector"]),
        )

    def test_hydra_em_gpcn_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/hydra-em-gpcn/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["axiomatic_container"], "GPCN-Set_phi")

        request = {
            "objective_reduction_energy_joule": 1.054571817e-34,
            "coherence_time_s": 1.0,
            "anesthetic_damping": 0.1,
            "microtubule_frequency_hz": 100000000.0,
            "microtubule_proxy_count": 6,
            "microtubule_coupling_strength": 0.8,
            "memories": [
                {"modality": "audio", "starting_time": 0.0, "ending_time": 1.0, "value": 0.2},
                {"modality": "video", "starting_time": 0.2, "ending_time": 1.2, "value": 0.8},
            ],
        }
        orch_response = client.post("/fnp-qnn/hydra-em-gpcn/orch-profile", json=request)
        self.assertEqual(orch_response.status_code, 200)
        profile = orch_response.json()["profile"]
        self.assertEqual(profile["model"], "hydra_em_gpcn_orch_profile_v1")
        self.assertIn(profile["verdict"], ["communicates", "decoheres", "suspended", "rejected"])
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertTrue(all(0.0 <= item <= 1.0 for item in profile["feature_vector"]))
        self.assertIn("GPCN-Set_phi", profile["axiomatic_container"]["axiom"])

        sweep_response = client.post(
            "/fnp-qnn/hydra-em-gpcn/anesthesia-sweep",
            json={**request, "damping_values": [0.0, 0.5, 1.0]},
        )
        self.assertEqual(sweep_response.status_code, 200)
        sweep = sweep_response.json()["profile"]
        self.assertTrue(sweep["monotonic_nonincreasing_communication"])

        runtime_response = client.post("/fnp-qnn/hydra-em-gpcn/runtime/profile", json=request)
        self.assertEqual(runtime_response.status_code, 200)
        self.assertEqual(runtime_response.json()["profile"]["model"], "hydra_em_gpcn_orch_profile_v1")

    def test_qnn_smoke_accepts_hydra_em_gpcn_opt_in(self):
        client = TestClient(app)

        baseline = client.post("/qnn/smoke", json={"epochs": 2, "test_size": 0.0})
        self.assertEqual(baseline.status_code, 200)
        baseline_dim = baseline.json()["result"]["feature_dimension"]

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "hydra_em_enabled": True,
                "gpcn_set_phi_enabled": True,
                "orch_or_simulation_enabled": True,
                "objective_reduction_energy_joule": 1.054571817e-34,
                "coherence_time_s": 1.0,
                "anesthetic_damping": 0.1,
                "microtubule_frequency_hz": 100000000.0,
                "microtubule_proxy_count": 6,
                "microtubule_coupling_strength": 0.8,
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertIn("hydra_em_gpcn_profile", result)
        self.assertGreater(result["feature_dimension"], baseline_dim)
        self.assertEqual(
            result["hydra_em_gpcn_profile"]["feature_dimension"],
            len(result["hydra_em_gpcn_profile"]["feature_vector"]),
        )

    def test_gravity_null_test_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/gravity-null-test/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["feature"], "axiomatic-chamber-gravity-null-test")

        run_response = client.post(
            "/fnp-qnn/gravity-null-test/run",
            json={
                "seed": 11,
                "shots": 512,
                "local_noise": 0.0,
                "leakage": 0.0,
                "mass_dispersion": 0.0,
                "delta_ns_threshold": 0.12,
                "include_sequence_export": True,
                "include_qiskit_preview": True,
            },
        )
        self.assertEqual(run_response.status_code, 200)
        profile = run_response.json()["profile"]
        self.assertEqual(profile["model"], "axiomatic_chamber_gravity_null_test_v1")
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertIn(profile["classification"], {"no_detected_remote_influence", "anomaly_requires_external_validation"})
        self.assertIn("sequence_event_spec", profile)
        self.assertIn("qiskit_circuit_preview", profile)
        self.assertIn("e2b_datadog_review", profile)
        self.assertTrue(profile["bell_vs_chamber_taxonomy"]["all_invariants_hold"])
        self.assertIsNone(profile["graviton_constraint"]["exact_graviton_mass_ev"])
        self.assertIn("not physical quantum-gravity proof", profile["research_boundary"])

    def test_qnn_smoke_accepts_gravity_null_test_opt_in(self):
        client = TestClient(app)

        baseline = client.post("/qnn/smoke", json={"epochs": 2, "test_size": 0.0})
        self.assertEqual(baseline.status_code, 200)
        baseline_dim = baseline.json()["result"]["feature_dimension"]

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "gravity_null_test_enabled": True,
                "gravity_null_test_seed": 11,
                "gravity_null_test_shots": 512,
                "gravity_null_test_local_noise": 0.0,
                "gravity_null_test_leakage": 0.0,
                "gravity_null_test_mass_dispersion": 0.0,
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertIn("gravity_null_test_profile", result)
        self.assertGreater(result["feature_dimension"], baseline_dim)
        self.assertEqual(
            result["gravity_null_test_profile"]["feature_dimension"],
            len(result["gravity_null_test_profile"]["feature_vector"]),
        )
        self.assertTrue(result["gravity_null_test_profile"]["bell_vs_chamber_taxonomy"]["all_invariants_hold"])
        self.assertIn("not physical quantum-gravity proof", result["gravity_null_test_profile"]["research_boundary"])

    def test_multiverse_experiment_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/multiverse-experiments/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["feature"], "quantum-paradoxes-multiverse-experiments")

        run_response = client.post(
            "/fnp-qnn/multiverse-experiments/run",
            json={
                "experiment_id": "wigner_friend_inter_branch_communication",
                "seed": 11,
                "shots": 128,
                "memory_erasure": 0.2,
                "measurement_strength": 0.8,
                "include_qiskit_preview": True,
            },
        )
        self.assertEqual(run_response.status_code, 200)
        profile = run_response.json()["profile"]
        self.assertEqual(profile["model"], "fnp_qnn_multiverse_experiment_profile_v1")
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertEqual(profile["classification"], "inter_branch_protocol_suspended_by_memory_record_constraints")
        self.assertIn("qiskit_preview", profile)
        self.assertTrue(profile["hierarchy_integrity"]["dF_is_not_generic_I"])
        self.assertIn("not validation of many-worlds ontology", profile["research_boundary"])

        run_all_response = client.post(
            "/fnp-qnn/multiverse-experiments/run-all",
            json={"shots": 128, "experiment_ids": ["deutsch_quantum_computation_origin"]},
        )
        self.assertEqual(run_all_response.status_code, 200)
        suite = run_all_response.json()["profile"]
        self.assertEqual(suite["experiment_count"], 1)
        self.assertEqual(suite["feature_dimension"], len(suite["feature_vector"]))

    def test_multiverse_schemas_reject_bad_shots_and_ids(self):
        client = TestClient(app)

        bad_shots = client.post("/fnp-qnn/multiverse-experiments/run", json={"shots": 1})
        self.assertEqual(bad_shots.status_code, 422)

        bad_id = client.post(
            "/fnp-qnn/multiverse-experiments/run",
            json={"experiment_id": "schrodinger_cat_context_only"},
        )
        self.assertEqual(bad_id.status_code, 422)

    def test_qnn_smoke_accepts_multiverse_experiments_opt_in(self):
        client = TestClient(app)

        baseline = client.post("/qnn/smoke", json={"epochs": 2, "test_size": 0.0})
        self.assertEqual(baseline.status_code, 200)
        baseline_dim = baseline.json()["result"]["feature_dimension"]

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "multiverse_experiments_enabled": True,
                "multiverse_experiment_ids": ["deutsch_quantum_computation_origin"],
                "multiverse_experiment_seed": 11,
                "multiverse_experiment_shots": 128,
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertIn("multiverse_experiments_profile", result)
        self.assertGreater(result["feature_dimension"], baseline_dim)
        self.assertEqual(result["multiverse_experiments_profile"]["experiment_count"], 1)
        self.assertEqual(
            result["multiverse_experiments_profile"]["feature_dimension"],
            len(result["multiverse_experiments_profile"]["feature_vector"]),
        )

    def test_qnn_smoke_command_accepts_multiverse_experiments_opt_in(self):
        client = TestClient(app)

        response = client.post(
            "/execute-command",
            json={
                "command": "qnn-smoke",
                "epochs": 2,
                "test_size": 0.0,
                "multiverse_experiments_enabled": True,
                "multiverse_experiment_ids": ["deutsch_quantum_computation_origin"],
                "multiverse_experiment_shots": 128,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("multiverse_experiments_profile", payload["data"]["result"])

    def test_time_physics_experiment_endpoints_return_bounded_payloads(self):
        client = TestClient(app)

        status_response = client.get("/fnp-qnn/time-physics-experiments/status")
        self.assertEqual(status_response.status_code, 200)
        self.assertEqual(status_response.json()["feature"], "jim-alkhalili-time-physics-experiments")

        run_response = client.post(
            "/fnp-qnn/time-physics-experiments/run",
            json={
                "experiment_id": "entanglement_decoherence_arrow",
                "seed": 11,
                "shots": 128,
                "include_qiskit_preview": True,
            },
        )
        self.assertEqual(run_response.status_code, 200)
        profile = run_response.json()["profile"]
        self.assertEqual(profile["model"], "fnp_qnn_time_physics_experiment_profile_v1")
        self.assertEqual(profile["feature_dimension"], len(profile["feature_vector"]))
        self.assertEqual(profile["classification"], "decoherent_arrow_entanglement_past_hypothesis_profile")
        self.assertIn("ALKHALILI_CHEN_DECOHERENT_ARROW_2024", profile["source_ids"])
        self.assertIn("qiskit_preview", profile)
        self.assertTrue(profile["hierarchy_integrity"]["dF_is_not_generic_I"])
        self.assertIn("not operational time travel", profile["research_boundary"])

        run_all_response = client.post(
            "/fnp-qnn/time-physics-experiments/run-all",
            json={"shots": 128, "experiment_ids": ["manifest_vs_physical_time_flow"]},
        )
        self.assertEqual(run_all_response.status_code, 200)
        suite = run_all_response.json()["profile"]
        self.assertEqual(suite["experiment_count"], 1)
        self.assertEqual(suite["feature_dimension"], len(suite["feature_vector"]))
        self.assertTrue(suite["citation_integrity"]["source_sets_are_separate"])

    def test_time_physics_schemas_reject_bad_shots_and_ids(self):
        client = TestClient(app)

        bad_shots = client.post("/fnp-qnn/time-physics-experiments/run", json={"shots": 1})
        self.assertEqual(bad_shots.status_code, 422)

        bad_id = client.post(
            "/fnp-qnn/time-physics-experiments/run",
            json={"experiment_id": "quantum_gravity_proof"},
        )
        self.assertEqual(bad_id.status_code, 422)

    def test_qnn_smoke_accepts_time_physics_experiments_opt_in(self):
        client = TestClient(app)

        baseline = client.post("/qnn/smoke", json={"epochs": 2, "test_size": 0.0})
        self.assertEqual(baseline.status_code, 200)
        baseline_dim = baseline.json()["result"]["feature_dimension"]

        response = client.post(
            "/qnn/smoke",
            json={
                "epochs": 2,
                "test_size": 0.0,
                "time_physics_experiments_enabled": True,
                "time_physics_experiment_ids": ["entanglement_decoherence_arrow"],
                "time_physics_experiment_seed": 11,
                "time_physics_experiment_shots": 128,
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertIn("time_physics_experiments_profile", result)
        self.assertGreater(result["feature_dimension"], baseline_dim)
        self.assertEqual(result["time_physics_experiments_profile"]["experiment_count"], 1)
        self.assertIn(
            "ALKHALILI_CHEN_DECOHERENT_ARROW_2024",
            result["time_physics_experiments_profile"]["source_ids"],
        )

    def test_qnn_smoke_command_accepts_time_physics_experiments_opt_in(self):
        client = TestClient(app)

        response = client.post(
            "/execute-command",
            json={
                "command": "qnn-smoke",
                "epochs": 2,
                "test_size": 0.0,
                "time_physics_experiments_enabled": True,
                "time_physics_experiment_ids": ["manifest_vs_physical_time_flow"],
                "time_physics_experiment_shots": 128,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("time_physics_experiments_profile", payload["data"]["result"])


if __name__ == "__main__":
    unittest.main()

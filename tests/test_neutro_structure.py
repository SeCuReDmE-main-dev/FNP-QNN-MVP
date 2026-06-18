import unittest

from core.cerebrum_runtime_bridge import CerebrumRuntimeBridge
from core.neutro_algebra import neutroalgebra_runtime_profile
from core.neutro_structure import (
    neutro_attribute_profile,
    neutro_relation_profile,
    neutrostructure_profile,
    runtime_neutrostructure_profile,
)


class NeutroStructureTests(unittest.TestCase):
    def test_classical_structure_returns_full_system_truth(self):
        profile = neutrostructure_profile(
            ["a", "b"],
            {"connected": "A"},
            {"stable": "A"},
        )

        self.assertEqual(profile["T_system"], 1.0)
        self.assertEqual(profile["I_system"], 0.0)
        self.assertEqual(profile["F_system"], 0.0)
        self.assertEqual(profile["system_classification"], "classical_structure")

    def test_neutrostructure_appears_with_neutro_relation_or_attribute_without_anti(self):
        profile = neutrostructure_profile(
            ["a", "b"],
            {"connected": "A"},
            {"stable": lambda element: "neutroA" if element == "b" else "A"},
        )

        self.assertEqual(profile["system_classification"], "neutrostructure")
        self.assertGreater(profile["I_system"], 0.0)
        self.assertEqual(profile["F_system"], 0.0)

    def test_antistructure_appears_with_anti_relation_or_attribute(self):
        profile = neutrostructure_profile(
            ["a", "b"],
            {"connected": "antiA"},
            {"stable": "A"},
        )

        self.assertEqual(profile["system_classification"], "antistructure")
        self.assertGreater(profile["F_system"], 0.0)

    def test_relation_and_attribute_profiles_are_bounded(self):
        relations = neutro_relation_profile(["a", "b"], {"r": lambda left, right: "A" if left == right else "neutroA"})
        attributes = neutro_attribute_profile(["a", "b"], {"x": lambda item: "A" if item == "a" else "antiA"})

        for profile in (relations, attributes):
            self.assertTrue(0.0 <= profile["T"] <= 1.0)
            self.assertTrue(0.0 <= profile["I"] <= 1.0)
            self.assertTrue(0.0 <= profile["F"] <= 1.0)

    def test_runtime_profile_produces_system_metrics_and_preserves_hierarchy(self):
        bridge = CerebrumRuntimeBridge()
        events, pairs, _warnings = bridge.ingest(bridge.default_payload())
        algebra = neutroalgebra_runtime_profile(events, pairs)
        profile = runtime_neutrostructure_profile(events, pairs, algebra)

        self.assertIn(profile["system_classification"], {"classical_structure", "neutrostructure", "antistructure", "hybrid_structure"})
        self.assertTrue(0.0 <= profile["T_system"] <= 1.0)
        self.assertTrue(0.0 <= profile["I_system"] <= 1.0)
        self.assertTrue(0.0 <= profile["F_system"] <= 1.0)
        self.assertEqual(profile["hierarchy"], "I -> I_system^S -> D_f -> dF -> i_fractal")
        self.assertNotIn("D_f", profile)
        self.assertNotIn("dF", profile)
        self.assertNotIn("i_fractal", profile)


if __name__ == "__main__":
    unittest.main()

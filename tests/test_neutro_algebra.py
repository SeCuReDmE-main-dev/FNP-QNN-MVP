import unittest

from core.neutro_algebra import (
    neutro_axiom_profile,
    neutro_function_profile,
    neutro_operation_table_profile,
    neutroalgebra_structure_profile,
    tri_section_space_profile,
)


class NeutroAlgebraTests(unittest.TestCase):
    def test_tri_section_profile_is_exhaustive_and_bounded(self):
        profile = tri_section_space_profile(
            ["x", "y", "z"],
            lambda item: {"x": "A", "y": "neutroA", "z": "antiA"}[item],
        )

        self.assertEqual(profile["counts"], {"A": 1, "neutroA": 1, "antiA": 1})
        self.assertTrue(profile["exhaustive"])
        self.assertTrue(0.0 <= profile["T"] <= 1.0)
        self.assertTrue(0.0 <= profile["I"] <= 1.0)
        self.assertTrue(0.0 <= profile["F"] <= 1.0)

    def test_neutro_function_distinguishes_total_partial_outer_and_indeterminate(self):
        total = neutro_function_profile(["a", "b"], [0, 1], [0, 1, 2], {"a": 0, "b": 1})
        partial = neutro_function_profile(["a", "b"], [0, 1], [0, 1, 2], {"a": 0})
        outer = neutro_function_profile(["a", "b"], [0, 1], [0, 1, 2], {"a": 2, "b": 2})
        indeterminate = neutro_function_profile(["a"], [0, 1], [0, 1, 2], {"a": {0, 1}})

        self.assertEqual(total["classification"], "total_function")
        self.assertEqual(partial["classification"], "partial_function")
        self.assertEqual(outer["classification"], "antifunction")
        self.assertEqual(indeterminate["classification"], "indeterminate_function")

    def test_neutro_operation_detects_inner_undefined_outer_and_indeterminate_outputs(self):
        profile = neutro_operation_table_profile(
            ["a", "b"],
            ["a", "b", "outside"],
            {
                ("a", "a"): "a",
                ("a", "b"): None,
                ("b", "a"): "outside",
                ("b", "b"): {"a", "b"},
            },
        )

        self.assertEqual(profile["classification"], "neutrooperation")
        self.assertEqual(profile["counts"]["A"], 1)
        self.assertEqual(profile["counts"]["neutroA"], 2)
        self.assertEqual(profile["counts"]["antiA"], 1)

    def test_associativity_can_be_partially_true_false_and_indeterminate(self):
        table = {
            ("a", "a"): "a",
            ("a", "b"): "a",
            ("a", "c"): "a",
            ("b", "a"): "a",
            ("b", "b"): "a",
            ("b", "c"): "a",
            ("c", "a"): "a",
            ("c", "b"): "c",
            ("c", "c"): None,
        }
        profile = neutro_axiom_profile(["a", "b", "c"], table, "associativity")

        self.assertEqual(profile["classification"], "neutroaxiom")
        self.assertGreater(profile["counts"]["A"], 0)
        self.assertGreater(profile["counts"]["neutroA"], 0)
        self.assertGreater(profile["counts"]["antiA"], 0)

    def test_structure_profiles_partial_and_neutroalgebra_cases(self):
        partial = neutroalgebra_structure_profile(
            ["a", "b"],
            {"op": {("a", "a"): "a", ("b", "b"): "b"}},
            ["closure"],
        )
        neutro = neutroalgebra_structure_profile(
            ["a", "b"],
            {
                "op": {
                    ("a", "a"): "a",
                    ("a", "b"): "b",
                    ("b", "a"): "a",
                    ("b", "b"): None,
                }
            },
            ["associativity"],
        )

        self.assertEqual(partial["classification"], "partial_algebra")
        self.assertTrue(partial["is_neutroalgebra_generalization"])
        self.assertIn(neutro["classification"], {"neutroalgebra", "hybrid_neutroalgebra"})
        self.assertTrue(all(0.0 <= item <= 1.0 for item in neutro["feature_vector"]))


if __name__ == "__main__":
    unittest.main()

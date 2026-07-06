import math
import unittest

from core.novak_anderson_phi_pi import (
    PHI,
    component_ratio_profile,
    convergence_profile,
    fibonacci_vector_sequence,
    golden_number,
    inverse_pseudopi,
    novak_anderson_status,
    pseudophi,
    pseudopi,
    source_packet,
)


class NovakAndersonPhiPiTests(unittest.TestCase):
    def test_pentagon_identities_match_phi_pi_paper(self):
        self.assertAlmostEqual(golden_number(2, 2), PHI, places=15)
        self.assertAlmostEqual(pseudopi(2), 5.0 / PHI, places=15)
        self.assertAlmostEqual(inverse_pseudopi(2), PHI / 5.0, places=15)
        self.assertAlmostEqual(pseudophi(2), PHI, places=15)

    def test_pseudopi_chain_converges_toward_pi(self):
        profile = convergence_profile(max_n=1000, sample_ns=[2, 10, 100, 1000])
        rows = profile["rows"]

        self.assertLess(rows[-1]["pseudopi_error_to_pi"], rows[0]["pseudopi_error_to_pi"])
        self.assertLess(rows[-1]["pseudopi_error_to_pi"], 1e-6)
        self.assertLess(rows[-1]["inverse_error_to_one_over_pi"], 1e-7)
        self.assertTrue(all(profile["proof_checks"].values()))

    def test_rejects_invalid_orders_and_indices(self):
        with self.assertRaises(ValueError):
            golden_number(1, 1)
        with self.assertRaises(ValueError):
            golden_number(3, 4)
        with self.assertRaises(ValueError):
            pseudopi(1)
        with self.assertRaises(ValueError):
            convergence_profile(max_n=1)

    def test_fibonacci_vector_sequence_matches_anderson_novak_dim4_table(self):
        vectors = fibonacci_vector_sequence(4, 5)

        self.assertEqual(vectors[0], [0, 0, 0, 1])
        self.assertEqual(vectors[1], [1, 1, 1, 1])
        self.assertEqual(vectors[2], [1, 2, 3, 4])
        self.assertEqual(vectors[5], [30, 56, 75, 85])

    def test_component_ratios_approximate_polygon_golden_numbers(self):
        profile = component_ratio_profile(4, 40)

        self.assertLess(profile["max_abs_error"], 1e-6)
        self.assertEqual(profile["dimension"], 4)
        self.assertEqual(len(profile["ratios"]), 4)

    def test_public_source_packet_redacts_private_gmail_content(self):
        serialized = repr(source_packet()) + repr(novak_anderson_status(max_n=256))
        forbidden_terms = (
            "1991219afdf1c342",
            "19911e91c5e7a11b",
            "mail.google.com",
            "raw_private_gmail_body",
            "private_message_id",
            "attachment_id",
        )
        for term in forbidden_terms:
            self.assertNotIn(term, serialized)
        self.assertIn("private provenance confirmed", serialized)


if __name__ == "__main__":
    unittest.main()

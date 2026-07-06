"""Novak-Anderson phi/pi theorem primitives for the FNP-QNN simulator.

This module implements source-backed classical geometry formulas from the
Anderson/Novak phi-pi and Fibonacci-vector papers. It does not claim physical,
clinical, security, cosmological, or consciousness validation.
"""

from __future__ import annotations

import importlib.util
import math
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_PI_PAPER_SOURCE_ID = "ANDERSON_NOVAK_PHI_PI_2008"
FIBONACCI_VECTOR_SOURCE_ID = "ANDERSON_NOVAK_FIBONACCI_VECTOR_POLYGONS_2009"
DANI_SHEET_SOURCE_ID = "DANI_NOVAK_PHI_HIGHER_DIMENSIONS_SHEET_REDACTED"
GENESIS_ECHOES_SOURCE_ID = "GENESIS_ECHOES_PAPER_I_DRIVE_DOC"
PRIVATE_GMAIL_PROVENANCE_SOURCE_ID = "PRIVATE_DANI_NOVAK_GMAIL_PROVENANCE_REDACTED"
LOCAL_RUNTIME_SOURCE_ID = "LOCAL_RUNTIME"

SOURCE_LEDGER: Dict[str, str] = {
    PHI_PI_PAPER_SOURCE_ID: (
        "https://hascmathart.weebly.com/uploads/7/6/8/7/7687070/"
        "a_connection_between_the_numbers_phi_and_pi_2.pdf"
    ),
    FIBONACCI_VECTOR_SOURCE_ID: (
        "https://www.researchgate.net/profile/Stuart-Anderson-2/publication/228768410_"
        "Fibonacci_vector_sequences_and_regular_polygons/links/54b5ec8c0cf26833efd345f7/"
        "Fibonacci-vector-sequences-and-regular-polygons.pdf"
    ),
    DANI_SHEET_SOURCE_ID: "https://docs.google.com/spreadsheets/d/1LICbMOdp689MwMvwToTQJkKf0SQNVKMNoRMKeRP1WFw/edit",
    GENESIS_ECHOES_SOURCE_ID: "https://docs.google.com/document/d/1kDqt3WML2ev0uBNH9OKseIb7XF5k6H9ScRzusJ47gf4/edit",
    PRIVATE_GMAIL_PROVENANCE_SOURCE_ID: "private provenance confirmed; no message body or message id is stored",
    LOCAL_RUNTIME_SOURCE_ID: "local deterministic simulator implementation",
}

RESEARCH_BOUNDARY = (
    "classical geometry and numerical convergence simulator only; not physical quantum validation, "
    "not a cosmology proof, not cryptographic assurance, not clinical or diagnostic behavior, "
    "and not an autonomous scientific conclusion"
)

FORBIDDEN_CLAIMS: Tuple[str, ...] = (
    "proves cosmology",
    "proves consciousness",
    "proves quantum technology",
    "proves cryptographic security",
    "clinical validation",
    "diagnostic validation",
    "production security guarantee",
)

DEFAULT_SAMPLE_NS: Tuple[int, ...] = (2, 3, 4, 5, 10, 25, 50, 100, 256)


def _validate_order(n: Any) -> int:
    try:
        order = int(n)
    except (TypeError, ValueError):
        raise ValueError("n must be an integer")
    if order != n and not (isinstance(n, float) and order == n):
        raise ValueError("n must be an integer")
    if order < 2:
        raise ValueError("n must be at least 2")
    return order


def _validate_dimension(dimension: Any) -> int:
    try:
        value = int(dimension)
    except (TypeError, ValueError):
        raise ValueError("dimension must be an integer")
    if value != dimension and not (isinstance(dimension, float) and value == dimension):
        raise ValueError("dimension must be an integer")
    if value < 2:
        raise ValueError("dimension must be at least 2")
    return value


def _validate_steps(steps: Any, *, minimum: int = 0) -> int:
    try:
        value = int(steps)
    except (TypeError, ValueError):
        raise ValueError("steps must be an integer")
    if value != steps and not (isinstance(steps, float) and value == steps):
        raise ValueError("steps must be an integer")
    if value < minimum:
        raise ValueError(f"steps must be at least {minimum}")
    return value


def _validate_index(n: int, i: Any) -> int:
    try:
        index = int(i)
    except (TypeError, ValueError):
        raise ValueError("i must be an integer")
    if index != i and not (isinstance(i, float) and index == i):
        raise ValueError("i must be an integer")
    if index < 1 or index > n:
        raise ValueError("i must satisfy 1 <= i <= n")
    return index


def alpha(n: int) -> float:
    """Return the minimum angle alpha_n = pi / (2n + 1)."""

    order = _validate_order(n)
    return math.pi / float((2 * order) + 1)


def golden_number(n: int, i: int) -> float:
    """Return the odd-polygon Golden Number r_n(i)."""

    order = _validate_order(n)
    index = _validate_index(order, i)
    if index == 1:
        return 1.0
    angle = alpha(order)
    return math.sin(index * angle) / math.sin(angle)


def pseudopi(n: int) -> float:
    """Return the pseudopi function from the polygon periphery/diagonal ratio."""

    order = _validate_order(n)
    angle = alpha(order)
    return (((2 * order) + 1) * math.sin(angle)) / math.sin(order * angle)


def inverse_pseudopi(n: int) -> float:
    """Return the inverse pseudopi function r_n(n) / (2n + 1)."""

    order = _validate_order(n)
    return golden_number(order, order) / float((2 * order) + 1)


def pseudophi(n: int) -> float:
    """Return the pseudophi function normalized by the pentagon side length."""

    order = _validate_order(n)
    return math.sin(order * alpha(order)) / math.sin(alpha(2))


def pseudopi_product(n: int) -> float:
    """Return pseudopi(n) * pseudophi(n)."""

    order = _validate_order(n)
    return pseudopi(order) * pseudophi(order)


def fibonacci_vector_sequence(dimension: int, steps: int) -> List[List[int]]:
    """Generate Fibonacci vector sequence vectors from k=0 through k=steps."""

    dim = _validate_dimension(dimension)
    count = _validate_steps(steps)
    vectors: List[List[int]] = [[0 for _ in range(dim - 1)] + [1]]
    for _ in range(count):
        previous = vectors[-1]
        next_vector = []
        for component_index in range(dim):
            start = dim - component_index - 1
            next_vector.append(sum(previous[start:]))
        vectors.append(next_vector)
    return vectors


def component_ratio_profile(dimension: int, steps: int) -> Dict[str, Any]:
    """Compare Fibonacci-vector component ratios to polygon Golden Numbers."""

    dim = _validate_dimension(dimension)
    count = _validate_steps(steps, minimum=1)
    vectors = fibonacci_vector_sequence(dim, count)
    vector = vectors[-1]
    denominator = vector[0]
    if denominator == 0:
        raise ValueError("component ratio denominator is zero; use steps >= 1")
    ratios = [component / denominator for component in vector]
    target_ratios = [golden_number(dim, index) for index in range(1, dim + 1)]
    return {
        "dimension": dim,
        "steps": count,
        "vector": vector,
        "ratios": ratios,
        "target_golden_numbers": target_ratios,
        "max_abs_error": max(abs(left - right) for left, right in zip(ratios, target_ratios)),
        "source_ids": [FIBONACCI_VECTOR_SOURCE_ID, LOCAL_RUNTIME_SOURCE_ID],
        "claim_class": "verified_in_code_against_source_formula",
        "research_boundary": RESEARCH_BOUNDARY,
    }


def _sample_orders(max_n: int, sample_ns: Optional[Iterable[int]]) -> List[int]:
    maximum = _validate_order(max_n)
    candidates = DEFAULT_SAMPLE_NS if sample_ns is None else tuple(sample_ns)
    orders = sorted({_validate_order(item) for item in candidates if int(item) <= maximum} | {maximum})
    return [order for order in orders if order <= maximum]


def convergence_profile(max_n: int = 256, sample_ns: Optional[Iterable[int]] = None) -> Dict[str, Any]:
    """Return sampled convergence evidence for the Novak-Anderson phi/pi chain."""

    maximum = _validate_order(max_n)
    rows = []
    for order in _sample_orders(maximum, sample_ns):
        pi_n = pseudopi(order)
        inverse = inverse_pseudopi(order)
        phi_n = pseudophi(order)
        rows.append(
            {
                "n": order,
                "sides": (2 * order) + 1,
                "alpha": alpha(order),
                "largest_golden_number": golden_number(order, order),
                "pseudopi": pi_n,
                "inverse_pseudopi": inverse,
                "pseudophi": phi_n,
                "pseudopi_product": pi_n * phi_n,
                "pseudopi_error_to_pi": abs(pi_n - math.pi),
                "inverse_error_to_one_over_pi": abs(inverse - (1.0 / math.pi)),
            }
        )

    final_row = rows[-1]
    return {
        "max_n": maximum,
        "rows": rows,
        "proof_checks": {
            "golden_number_2_2_equals_phi": math.isclose(golden_number(2, 2), PHI, rel_tol=0.0, abs_tol=1e-15),
            "pseudopi_2_equals_5_over_phi": math.isclose(pseudopi(2), 5.0 / PHI, rel_tol=0.0, abs_tol=1e-15),
            "inverse_pseudopi_2_equals_phi_over_5": math.isclose(
                inverse_pseudopi(2), PHI / 5.0, rel_tol=0.0, abs_tol=1e-15
            ),
            "final_pseudopi_within_1e_4_of_pi": final_row["pseudopi_error_to_pi"] < 1e-4,
            "final_inverse_within_1e_5_of_one_over_pi": final_row["inverse_error_to_one_over_pi"] < 1e-5,
        },
        "source_ids": [
            PHI_PI_PAPER_SOURCE_ID,
            FIBONACCI_VECTOR_SOURCE_ID,
            DANI_SHEET_SOURCE_ID,
            GENESIS_ECHOES_SOURCE_ID,
            PRIVATE_GMAIL_PROVENANCE_SOURCE_ID,
            LOCAL_RUNTIME_SOURCE_ID,
        ],
        "claim_classes": {
            PHI_PI_PAPER_SOURCE_ID: "confirmed_by_primary_source",
            FIBONACCI_VECTOR_SOURCE_ID: "confirmed_by_primary_source",
            DANI_SHEET_SOURCE_ID: "confirmed_by_private_provenance_redacted",
            GENESIS_ECHOES_SOURCE_ID: "interpretive_internal_source",
            PRIVATE_GMAIL_PROVENANCE_SOURCE_ID: "private_redacted_provenance_only",
            LOCAL_RUNTIME_SOURCE_ID: "verified_in_code",
        },
        "research_boundary": RESEARCH_BOUNDARY,
    }


def source_packet() -> Dict[str, Any]:
    """Return a public-safe source packet with private email content redacted."""

    return {
        "source_ledger": dict(SOURCE_LEDGER),
        "primary_public_sources": [PHI_PI_PAPER_SOURCE_ID, FIBONACCI_VECTOR_SOURCE_ID],
        "private_provenance_sources": [DANI_SHEET_SOURCE_ID, PRIVATE_GMAIL_PROVENANCE_SOURCE_ID],
        "privacy_boundary": "private Gmail bodies, message ids, attachment ids, and display URLs are not stored",
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
        "research_boundary": RESEARCH_BOUNDARY,
    }


def novak_anderson_status(max_n: int = 256) -> Dict[str, Any]:
    """Return status, convergence checks, and environment metadata."""

    profile = convergence_profile(max_n=max_n)
    checks = profile["proof_checks"]
    return {
        "feature": "novak-anderson-phi-pi-theorem",
        "status": "ok" if all(checks.values()) else "review",
        "phi": PHI,
        "pi": math.pi,
        "stim_available": importlib.util.find_spec("stim") is not None,
        "stim_usage": "available for future quantum-circuit demos; not used for this classical geometry proof",
        "convergence": profile,
        "fibonacci_vector_dim4_step5": fibonacci_vector_sequence(4, 5)[-1],
        "dim4_ratio_profile": component_ratio_profile(4, 32),
        "source_packet": source_packet(),
    }


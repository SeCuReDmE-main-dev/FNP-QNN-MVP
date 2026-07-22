"""Crystal Chamber admission profile for bounded FNP-QNN material simulations."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Dict, Mapping, Optional

from .crystal_growth_fractal_profile import (
    HIERARCHY,
    RESEARCH_BOUNDARY,
    crystal_growth_window_profile,
)
from .dmqc_crystal_mining import DMQC_DEFINITION, run_dmqc_prediction
from .neutrosophic_quantum_primitives import FractalCarrierContext, fractal_carrier_profile
from .plithogenic_logic import plithogenic_weighted_cumulative_truth


CRYSTAL_CHAIN = "I -> I_system^S -> D_crystal -> dC -> i_crystal"
FRACTAL_CHAIN = "I -> I_system^S -> D_f -> dF -> i_fractal"
CRYSTAL_CHAMBER_BOUNDARY = (
    RESEARCH_BOUNDARY
    + "; Crystal Chamber separates i_crystal from i_fractal and treats near-chaotic growth as suspended"
)


def _clamp01(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return max(0.0, min(1.0, numeric))


@dataclass(frozen=True)
class CrystalChamberInput:
    composition_vector: tuple[float, ...] = (0.5, 0.5)
    formation_energy: float = -0.35
    lattice_symmetry_score: float = 0.72
    growth_rate: float = 0.42
    branch_drift: float = 0.38
    fractal_dimension_Df: Optional[float] = None
    surface_roughness: float = 0.24
    defect_density: float = 0.18
    phase_stability_margin: float = 0.76
    fractal_admissible: bool = False

    @classmethod
    def from_mapping(cls, payload: Optional[Mapping[str, Any]] = None) -> "CrystalChamberInput":
        data = dict(payload or {})
        composition = tuple(float(item) for item in data.get("composition_vector", (0.5, 0.5)))
        if not composition:
            raise ValueError("composition_vector must not be empty")
        fractal_value = data.get("fractal_dimension_Df", data.get("D_f"))
        return cls(
            composition_vector=composition,
            formation_energy=float(data.get("formation_energy", -0.35)),
            lattice_symmetry_score=_clamp01(data.get("lattice_symmetry_score", 0.72)),
            growth_rate=_clamp01(data.get("growth_rate", 0.42)),
            branch_drift=_clamp01(data.get("branch_drift", 0.38)),
            fractal_dimension_Df=None if fractal_value is None else float(fractal_value),
            surface_roughness=_clamp01(data.get("surface_roughness", 0.24)),
            defect_density=_clamp01(data.get("defect_density", 0.18)),
            phase_stability_margin=_clamp01(data.get("phase_stability_margin", 0.76)),
            fractal_admissible=bool(data.get("fractal_admissible", fractal_value is not None)),
        )

    def dmqc_record(self) -> Dict[str, Any]:
        return {
            "record_id": "crystal_chamber_candidate",
            "composition_vector": list(self.composition_vector),
            "formation_energy": self.formation_energy,
            "lattice_symmetry_score": self.lattice_symmetry_score,
            "defect_density": self.defect_density,
            "phase_stability_margin": self.phase_stability_margin,
        }


def crystal_chamber_admission_profile(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Return the Crystal Chamber admission profile."""

    chamber_input = CrystalChamberInput.from_mapping(payload)
    dmqc_profile = run_dmqc_prediction(candidate=chamber_input.dmqc_record())
    growth_profile = crystal_growth_window_profile(
        growth_rate=chamber_input.growth_rate,
        branch_drift=chamber_input.branch_drift,
        surface_roughness=chamber_input.surface_roughness,
        defect_density=chamber_input.defect_density,
        phase_stability_margin=chamber_input.phase_stability_margin,
    )
    d_crystal = _clamp01(
        0.35 * chamber_input.lattice_symmetry_score
        + 0.30 * chamber_input.phase_stability_margin
        + 0.20 * (1.0 - chamber_input.defect_density)
        + 0.15 * (1.0 - chamber_input.surface_roughness)
    )
    dC = _clamp01(
        0.35 * chamber_input.branch_drift
        + 0.25 * chamber_input.surface_roughness
        + 0.25 * chamber_input.defect_density
        + 0.15 * (1.0 - chamber_input.phase_stability_margin)
    )
    i_crystal = _clamp01((1.0 - d_crystal + dC + growth_profile["near_chaos_margin"]) / 3.0)
    if growth_profile["near_chaos_margin"] >= 0.80 or chamber_input.phase_stability_margin <= 0.15:
        adm = "rejected"
        classification = "crystal_growth_rejected"
    elif growth_profile["near_chaos_margin"] >= 0.55 or i_crystal >= 0.50:
        adm = "suspended"
        classification = "near-chaotic suspended crystal growth state"
    else:
        adm = "admitted"
        classification = "crystal_growth_admitted"

    fractal_carrier = None
    if chamber_input.fractal_dimension_Df is not None:
        fractal_carrier = fractal_carrier_profile(
            chamber_input.fractal_dimension_Df,
            1.0,
            2.0,
            context=FractalCarrierContext(
                system="crystal-chamber-fractal-line",
                measurement_method="provided-or-synthetic-crystal-fractal-dimension",
                scale="crystal-growth",
                domain="crystal-chamber",
                admissible=chamber_input.fractal_admissible,
            ),
        )

    plithogenic_profiles = [
        {"truth": d_crystal, "indeterminacy": i_crystal, "falsity": 1.0 - d_crystal, "weight": 0.40},
        {
            "truth": chamber_input.phase_stability_margin,
            "indeterminacy": dC,
            "falsity": 1.0 - chamber_input.phase_stability_margin,
            "weight": 0.35,
        },
        {
            "truth": 1.0 - growth_profile["near_chaos_margin"],
            "indeterminacy": growth_profile["near_chaos_margin"],
            "falsity": growth_profile["near_chaos_margin"],
            "weight": 0.25,
        },
    ]
    plithogenic = plithogenic_weighted_cumulative_truth(plithogenic_profiles)
    feature_vector = [
        *dmqc_profile["feature_vector"],
        *growth_profile["feature_vector"],
        d_crystal,
        dC,
        i_crystal,
        plithogenic["T"],
        plithogenic["I"],
        plithogenic["F"],
        0.0 if fractal_carrier is None or fractal_carrier["D_f_hat"] is None else fractal_carrier["D_f_hat"],
    ]
    return {
        "model": "crystal_chamber_admission_v1",
        "dmqc_definition": DMQC_DEFINITION,
        "source_ids": dmqc_profile["source_ids"],
        "Adm": adm,
        "classification": classification,
        "D_crystal": d_crystal,
        "dC": dC,
        "i_crystal": i_crystal,
        "i_growth": growth_profile["instability_load"],
        "i_rate": chamber_input.growth_rate,
        "near_chaos_margin": growth_profile["near_chaos_margin"],
        "crystal_coherence_score": d_crystal,
        "dmqc_crystal_profile": dmqc_profile,
        "crystal_growth_profile": growth_profile,
        "plithogenic_crystal_profile": plithogenic,
        "fractal_carrier": fractal_carrier,
        "i_fractal": None if fractal_carrier is None else fractal_carrier["i_fractal_candidate"],
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "crystal_chain": CRYSTAL_CHAIN,
        "fractal_chain": FRACTAL_CHAIN,
        "forbidden_claims": [
            "not DFT",
            "not validated material discovery",
            "not quantum hardware result",
            "suspended is not falsity",
            "i_crystal is not automatically i_fractal",
        ],
        "research_boundary": CRYSTAL_CHAMBER_BOUNDARY,
    }


def crystal_chamber_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "feature": "crystal-chamber",
        "dmqc_definition": DMQC_DEFINITION,
        "primary_chain": CRYSTAL_CHAIN,
        "optional_fractal_chain": FRACTAL_CHAIN,
        "states": ["admitted", "suspended", "rejected"],
        "near_chaos_state": "near-chaotic suspended crystal growth state",
        "variables": [
            "composition_vector",
            "formation_energy",
            "lattice_symmetry_score",
            "growth_rate",
            "branch_drift",
            "fractal_dimension_Df",
            "surface_roughness",
            "defect_density",
            "phase_stability_margin",
        ],
        "hierarchy": HIERARCHY,
        "research_boundary": CRYSTAL_CHAMBER_BOUNDARY,
    }


__all__ = [
    "CRYSTAL_CHAIN",
    "CRYSTAL_CHAMBER_BOUNDARY",
    "FRACTAL_CHAIN",
    "CrystalChamberInput",
    "crystal_chamber_admission_profile",
    "crystal_chamber_status",
]

"""DMQC crystal-mining profiles for the alpha-local simulator.

DMQC means Data Mining of Quantum Calculations in this project. It is a working
term for transforming ab-initio-like records into bounded simulator features;
it is not an official standard, not a DFT engine, and not validated material
discovery.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

import numpy as np

from .quantum_feature_transforms import (
    complex_wavefunction_to_amplitude_phase_features,
    structure_vector_to_phi_scaled_state,
)


HIERARCHY = "I -> I_system^S -> D_crystal -> dC -> i_crystal"
DMQC_DEFINITION = "Data Mining of Quantum Calculations"
RESEARCH_BOUNDARY = (
    "DMQC is a project working term; alpha-local educational simulation only; "
    "not DFT, not validated material discovery, not quantum hardware output, "
    "and not a physical proof"
)
SOURCE_IDS = [
    "DMQC_REVELATION_LOCAL_PDF",
    "CURTAROLO_MORGAN_PERSSON_RODGERS_CEDER_2003_ARXIV_COND_MAT_0307262",
    "CEDER_GROUP_MRS_DATA_MINING_AB_INITIO_CRYSTAL_STRUCTURE",
    "NSS_PLITHOGENIC_NEUTROSOPHIC_BACKGROUND",
]
DEFAULT_FIXTURE = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "dmqc" / "binary_alloy_energy_library.v1.json"


def _finite_float(value: Any, label: str, fallback: Optional[float] = None) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        if fallback is not None:
            return fallback
        raise ValueError(f"{label} must be numeric")
    if not math.isfinite(numeric):
        if fallback is not None:
            return fallback
        raise ValueError(f"{label} must be finite")
    return numeric


def _clamp01(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(numeric):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _positive_scale(value: float, scale: float) -> float:
    value = max(0.0, float(value))
    scale = max(float(scale), 1e-12)
    return _clamp01((value / scale) / (1.0 + value / scale))


@dataclass(frozen=True)
class DMQCCrystalRecord:
    record_id: str
    composition_vector: tuple[float, ...]
    formation_energy: float
    lattice_symmetry_score: float
    defect_density: float = 0.0
    phase_stability_margin: float = 1.0

    @classmethod
    def from_mapping(cls, item: Mapping[str, Any]) -> "DMQCCrystalRecord":
        composition = tuple(_finite_float(value, "composition_vector") for value in item.get("composition_vector", []))
        if not composition:
            raise ValueError("composition_vector must not be empty")
        return cls(
            record_id=str(item.get("record_id") or item.get("id") or "record"),
            composition_vector=composition,
            formation_energy=_finite_float(item.get("formation_energy", 0.0), "formation_energy"),
            lattice_symmetry_score=_clamp01(item.get("lattice_symmetry_score", 0.5)),
            defect_density=_clamp01(item.get("defect_density", 0.0)),
            phase_stability_margin=_clamp01(item.get("phase_stability_margin", 1.0)),
        )

    def feature_row(self) -> list[float]:
        return [
            *self.composition_vector,
            self.formation_energy,
            self.lattice_symmetry_score,
            self.defect_density,
            self.phase_stability_margin,
        ]


def load_dmqc_library(path: Optional[Path] = None) -> list[DMQCCrystalRecord]:
    """Load a small source-labeled educational fixture."""

    fixture = path or DEFAULT_FIXTURE
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    return [DMQCCrystalRecord.from_mapping(item) for item in payload["records"]]


def _matrix(records: Sequence[DMQCCrystalRecord]) -> np.ndarray:
    rows = [record.feature_row() for record in records]
    width = max(len(row) for row in rows)
    padded = [row + [0.0] * (width - len(row)) for row in rows]
    return np.asarray(padded, dtype=np.float32)


def pca_correlation_profile(records: Sequence[DMQCCrystalRecord], components: int = 2) -> Dict[str, Any]:
    """Return a deterministic PCA-like profile using SVD."""

    if not records:
        raise ValueError("records must not be empty")
    X = _matrix(records)
    centered = X - X.mean(axis=0, keepdims=True)
    if X.shape[0] == 1:
        singular = np.zeros(1, dtype=np.float32)
        coordinates = np.zeros((1, max(1, components)), dtype=np.float32)
        explained = np.zeros(max(1, components), dtype=np.float32)
    else:
        _, singular, vt = np.linalg.svd(centered, full_matrices=False)
        count = max(1, min(int(components), vt.shape[0]))
        coordinates = centered @ vt[:count].T
        variance = singular**2
        total = float(np.sum(variance)) or 1.0
        explained = (variance[:count] / total).astype(np.float32)
    feature_vector = [_clamp01(abs(float(item))) for item in explained[: max(1, components)]]
    return {
        "model": "dmqc_pca_correlation_profile_v1",
        "record_count": len(records),
        "component_count": len(feature_vector),
        "explained_variance_ratio": [float(item) for item in explained[: len(feature_vector)]],
        "coordinates_preview": coordinates[: min(3, len(records))].astype(float).tolist(),
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def pls_energy_profile(records: Sequence[DMQCCrystalRecord]) -> Dict[str, Any]:
    """Return a bounded PLS-style correlation between descriptors and energy."""

    if not records:
        raise ValueError("records must not be empty")
    X = _matrix(records)
    y = np.asarray([record.formation_energy for record in records], dtype=np.float32)
    descriptors = X[:, :-4] if X.shape[1] > 4 else X
    correlations = []
    for col in descriptors.T:
        if np.std(col) <= 1e-12 or np.std(y) <= 1e-12:
            correlations.append(0.0)
        else:
            correlations.append(float(np.corrcoef(col, y)[0, 1]))
    absolute = [abs(item) for item in correlations if math.isfinite(item)]
    signal = float(max(absolute)) if absolute else 0.0
    mean_signal = float(np.mean(absolute)) if absolute else 0.0
    feature_vector = [_clamp01(signal), _clamp01(mean_signal)]
    return {
        "model": "dmqc_pls_energy_profile_v1",
        "descriptor_energy_signal": signal,
        "descriptor_energy_mean_signal": mean_signal,
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def convex_hull_proxy(records: Sequence[DMQCCrystalRecord], candidate: DMQCCrystalRecord) -> Dict[str, Any]:
    """Return a conservative educational energy-above-hull proxy."""

    if not records:
        raise ValueError("records must not be empty")
    min_energy = min(record.formation_energy for record in records)
    energy_above_proxy = max(0.0, candidate.formation_energy - min_energy)
    stability_score = _clamp01(candidate.phase_stability_margin * (1.0 - _positive_scale(energy_above_proxy, 1.0)))
    if stability_score >= 0.70:
        classification = "stable_or_low_proxy_distance"
    elif stability_score >= 0.35:
        classification = "metastable_proxy_window"
    else:
        classification = "high_proxy_distance_suspended"
    feature_vector = [_positive_scale(energy_above_proxy, 1.0), stability_score]
    return {
        "model": "dmqc_convex_hull_proxy_v1",
        "candidate_id": candidate.record_id,
        "energy_above_hull_proxy": energy_above_proxy,
        "phase_stability_margin": candidate.phase_stability_margin,
        "stability_score": stability_score,
        "classification": classification,
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def dmqc_feature_bridge(records: Sequence[DMQCCrystalRecord], candidate: DMQCCrystalRecord) -> Dict[str, Any]:
    """Bridge DMQC descriptors into FNP-QNN-compatible bounded features."""

    pca = pca_correlation_profile(records)
    pls = pls_energy_profile(records)
    hull = convex_hull_proxy(records, candidate)
    structure = [
        *candidate.composition_vector,
        candidate.lattice_symmetry_score,
        candidate.defect_density,
        candidate.phase_stability_margin,
    ]
    state = structure_vector_to_phi_scaled_state(structure)
    amplitude_phase = complex_wavefunction_to_amplitude_phase_features(state)
    state_features = [_clamp01(abs(float(item))) for item in amplitude_phase[:6]]
    feature_vector = [
        *pca["feature_vector"],
        *pls["feature_vector"],
        *hull["feature_vector"],
        *state_features,
    ]
    return {
        "model": "dmqc_to_fnp_qnn_feature_bridge_v1",
        "dmqc_definition": DMQC_DEFINITION,
        "source_ids": SOURCE_IDS,
        "candidate": candidate.record_id,
        "pca_correlation_profile": pca,
        "pls_energy_profile": pls,
        "convex_hull_proxy": hull,
        "feature_vector": feature_vector,
        "feature_dimension": len(feature_vector),
        "hierarchy": HIERARCHY,
        "forbidden_claims": [
            "not DFT",
            "not validated material discovery",
            "not quantum hardware result",
            "not a physical proof",
        ],
        "research_boundary": RESEARCH_BOUNDARY,
    }


def run_dmqc_prediction(
    library: Optional[Sequence[Mapping[str, Any]]] = None,
    candidate: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Run the local DMQC fixture bridge."""

    records = [DMQCCrystalRecord.from_mapping(item) for item in library] if library is not None else load_dmqc_library()
    if not records:
        raise ValueError("library must contain at least one record")
    candidate_record = DMQCCrystalRecord.from_mapping(candidate) if candidate is not None else records[-1]
    return dmqc_feature_bridge(records, candidate_record)


def dmqc_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "feature": "dmqc-crystal-mining",
        "dmqc_definition": DMQC_DEFINITION,
        "source_ids": SOURCE_IDS,
        "fixture": str(DEFAULT_FIXTURE),
        "hierarchy": HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
        "endpoints": ["GET /dmqc/status", "POST /dmqc/run", "POST /dmqc/crystal-chamber/run"],
    }


__all__ = [
    "DMQC_DEFINITION",
    "DMQCCrystalRecord",
    "HIERARCHY",
    "RESEARCH_BOUNDARY",
    "SOURCE_IDS",
    "convex_hull_proxy",
    "dmqc_feature_bridge",
    "dmqc_status",
    "load_dmqc_library",
    "pca_correlation_profile",
    "pls_energy_profile",
    "run_dmqc_prediction",
]

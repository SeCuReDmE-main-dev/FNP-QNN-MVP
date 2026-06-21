"""
Runtime bridge for Cerebrum-shaped memory streams.

The original Cerebrum package is kept isolated because it is a Python 2 era
runtime with RethinkDB, audio, and GUI dependencies. This bridge implements the
portable contract the simulator needs: interval memories, crossmodal overlap
pairs, feature bundles, and QNN-ready observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from importlib.util import find_spec
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .cerebrum_adapter import CerebrumAdapter, CerebrumFeatureBundle, MODALITIES
from .ffed_plugin_bridge import FfeDPluginBridge
from .hydra_em_gpcn_math import hydra_em_gpcn_orch_profile
from .lvfm_runtime_graph import LVFMRuntimeGraph, RegisterBit
from .neutrosophic_quantum_primitives import fractal_carrier_profile
from .neutro_algebra import neutroalgebra_runtime_profile
from .neutro_structure import runtime_neutrostructure_profile
from .penrose_hameroff_math import penrose_hameroff_runtime_profile
from .plithogenic_logic import plithogenic_runtime_fusion_profile
from .plithogenic_probability_statistics import plithogenic_topology_wiring_profile
from .qnn_nucleus import QNNNucleus
from .revolutionary_topologies import revolutionary_topology_runtime_profile


MODALITY_ALIASES = {
    "hearing": "audio",
    "audio": "audio",
    "h": "audio",
    "vision": "video",
    "visual": "video",
    "video": "video",
    "v": "video",
    "language": "text",
    "caption": "text",
    "captions": "text",
    "text": "text",
    "l": "text",
    "stimulus": "stimuli",
    "stimuli": "stimuli",
    "s": "stimuli",
}

PAIR_CODE = {"audio": "H", "video": "V", "text": "L", "stimuli": "S"}
COLLECTION_MODALITIES = {
    "hearing_memory": "audio",
    "hearing": "audio",
    "audio": "audio",
    "vision_memory": "video",
    "vision": "video",
    "video": "video",
    "language_memory": "text",
    "language": "text",
    "text": "text",
    "stimuli": "stimuli",
    "stimulus": "stimuli",
}

PAIR_DIRECTION_ALIASES = {
    "H2V": ("audio", "video"),
    "V2H": ("video", "audio"),
    "H2L": ("audio", "text"),
    "L2H": ("text", "audio"),
    "V2L": ("video", "text"),
    "L2V": ("text", "video"),
}

LEGACY_TABLE_MODALITIES = {
    "hearing_timestamps": "audio",
    "vision_timestamps": "video",
    "language_timestamps": "text",
    "stimuli_timestamps": "stimuli",
}

MAX_RUNTIME_EVENTS = 1000
MAX_RUNTIME_PAIRS = 20000
MAX_LEGACY_SNAPSHOT_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class CerebrumMemoryEvent:
    modality: str
    starting_time: float
    ending_time: float
    value: float
    source: str = ""
    label: str = ""
    payload_ref: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.ending_time - self.starting_time)

    def to_observation(self) -> Dict[str, Any]:
        return {
            "modality": self.modality,
            "value": self.value,
            "timestamp": self.starting_time,
            "ending_time": self.ending_time,
            "weight": max(self.duration, 1.0),
            "label": self.label,
            "source": self.source,
            "payload_ref": self.payload_ref,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "modality": self.modality,
            "starting_time": self.starting_time,
            "ending_time": self.ending_time,
            "duration": self.duration,
            "value": self.value,
            "source": self.source,
            "label": self.label,
            "payload_ref": self.payload_ref,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class CrossModalPair:
    timestamp1: float
    timestamp2: float
    direction: str
    source_modality: str
    target_modality: str
    overlap_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp1": self.timestamp1,
            "timestamp2": self.timestamp2,
            "direction": self.direction,
            "source_modality": self.source_modality,
            "target_modality": self.target_modality,
            "overlap_score": self.overlap_score,
        }


@dataclass
class CerebrumRuntimeState:
    events: List[CerebrumMemoryEvent]
    pairs: List[CrossModalPair]
    observations: List[Dict[str, Any]]
    feature_bundle: CerebrumFeatureBundle
    feature_vector: np.ndarray
    qnn_result: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    lvfm: Optional[Dict[str, Any]] = None
    plithogenic: Optional[Dict[str, Any]] = None
    revolutionary_topology: Optional[Dict[str, Any]] = None
    plithogenic_topology: Optional[Dict[str, Any]] = None
    neutro_algebra: Optional[Dict[str, Any]] = None
    penrose_hameroff: Optional[Dict[str, Any]] = None
    hydra_em_gpcn: Optional[Dict[str, Any]] = None

    def to_dict(self, include_bundle: bool = True) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "events": [event.to_dict() for event in self.events],
            "pairs": [pair.to_dict() for pair in self.pairs],
            "observations": self.observations,
            "feature_vector": self.feature_vector.tolist(),
            "feature_dimension": int(self.feature_vector.shape[0]),
            "qnn_result": self.qnn_result,
            "warnings": self.warnings,
        }
        if self.lvfm is not None:
            payload["lvfm"] = self.lvfm
        if self.plithogenic is not None:
            payload["plithogenic"] = self.plithogenic
        if self.revolutionary_topology is not None:
            payload["revolutionary_topology"] = self.revolutionary_topology
        if self.plithogenic_topology is not None:
            payload["plithogenic_topology"] = self.plithogenic_topology
        if self.neutro_algebra is not None:
            payload["neutro_algebra"] = self.neutro_algebra
        if self.penrose_hameroff is not None:
            payload["penrose_hameroff"] = self.penrose_hameroff
        if self.hydra_em_gpcn is not None:
            payload["hydra_em_gpcn"] = self.hydra_em_gpcn
        if include_bundle:
            payload["bundle"] = {
                "sequence_length": self.feature_bundle.sequence_length,
                "summary": self.feature_bundle.summary,
                "modality_counts": self.feature_bundle.modality_counts,
                "modality_means": self.feature_bundle.modality_means,
                "modality_stds": self.feature_bundle.modality_stds,
                "transition_matrix": self.feature_bundle.transition_matrix.tolist(),
            }
        return payload


class CerebrumRuntimeBridge:
    """Normalize Cerebrum-shaped memory intervals and run the simulator path."""

    def __init__(
        self,
        adapter: Optional[CerebrumAdapter] = None,
        legacy_cerebrum_path: Optional[str] = None,
    ):
        self.adapter = adapter or CerebrumAdapter()
        self.legacy_cerebrum_path = Path(legacy_cerebrum_path) if legacy_cerebrum_path else None

    def status(self, qnn_nucleus: Optional[QNNNucleus] = None) -> Dict[str, Any]:
        optional_modules = {
            "rethinkdb": find_spec("rethinkdb") is not None,
            "pyaudio": find_spec("pyaudio") is not None,
            "cv2": find_spec("cv2") is not None,
            "hpelm": find_spec("hpelm") is not None,
        }
        qnn_backend = "not-attached"
        if qnn_nucleus is not None:
            fallback = next((item for item in qnn_nucleus.candidate_matrix() if item.name == "torch_surrogate"), None)
            primary = next((item for item in qnn_nucleus.candidate_matrix() if item.role == "primary"), None)
            qnn_backend = primary.backend if primary and primary.available else fallback.backend if fallback else "unknown"
        return {
            "status": "ok",
            "bridge": "operational",
            "supported_modalities": list(MODALITIES),
            "supported_pair_directions": ["H2V", "V2H", "H2L", "L2H", "V2L", "L2V"],
            "legacy_cerebrum_path": str(self.legacy_cerebrum_path) if self.legacy_cerebrum_path else None,
            "legacy_cerebrum_path_exists": bool(self.legacy_cerebrum_path and self.legacy_cerebrum_path.exists()),
            "optional_dependency_available": optional_modules,
            "qnn_backend": qnn_backend,
        }

    def ingest(self, payload: Mapping[str, Any] | Sequence[Any] | None) -> Tuple[List[CerebrumMemoryEvent], List[CrossModalPair], List[str]]:
        warnings: List[str] = []
        records = self._extract_records(payload, warnings)
        parsed = [self._parse_record(record, index, warnings) for index, record in enumerate(records)]
        events = self._normalize_event_times([event for event in parsed if event is not None])
        pairs = self._extract_pairs(payload, events, warnings)
        if not events:
            warnings.append("No runtime memory events were provided.")
        return events, pairs, warnings

    def build_state(
        self,
        payload: Mapping[str, Any] | Sequence[Any] | None,
        qnn_nucleus: Optional[QNNNucleus] = None,
        label: float = 1.0,
        max_epochs: int = 12,
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_hook_enabled: bool = False,
        plugin_set: str = "mvp5",
        plugin_context: Optional[Mapping[str, Any]] = None,
        cpai_context: Optional[Mapping[str, Any]] = None,
        include_plugin_trace: bool = True,
        plithogenic_enabled: bool = False,
        revolutionary_topology_enabled: bool = False,
        neutro_algebra_enabled: bool = False,
        penrose_hameroff_enabled: bool = False,
        objective_reduction_energy_joule: Optional[float] = None,
        coherence_time_s: Optional[float] = None,
        anesthetic_damping: Optional[float] = None,
        microtubule_frequency_hz: Optional[float] = None,
        spin_network_vertices: Optional[Sequence[Sequence[float]]] = None,
        hydra_em_enabled: bool = False,
        gpcn_set_phi_enabled: bool = False,
        orch_or_simulation_enabled: bool = False,
        microtubule_proxy_count: int = 8,
        microtubule_coupling_strength: float = 0.5,
        quasicrystal_projection_enabled: bool = True,
        plithogenic_contradiction_threshold: float = 0.35,
        lattice_seed: int = 0,
        observation_scale_min: float = 0.01,
        observation_scale_max: float = 1.0,
    ) -> CerebrumRuntimeState:
        events, pairs, warnings = self.ingest(payload)
        observations = [event.to_observation() for event in events]
        bundle = self.adapter.build_bundle(observations)
        vector = self.adapter.bundle_to_vector(bundle)
        plithogenic_profile = None
        plithogenic_features: Optional[List[float]] = None
        if plithogenic_enabled:
            plithogenic_profile = plithogenic_runtime_fusion_profile(events, pairs)
            plithogenic_features = [float(item) for item in plithogenic_profile["feature_vector"]]
            vector = np.concatenate([vector, np.asarray(plithogenic_features, dtype=np.float32)]).astype(np.float32)
        revolutionary_topology_profile = None
        revolutionary_topology_features: Optional[List[float]] = None
        if revolutionary_topology_enabled:
            revolutionary_topology_profile = revolutionary_topology_runtime_profile(events, pairs)
            revolutionary_topology_features = [
                float(item) for item in revolutionary_topology_profile["feature_vector"]
            ]
            vector = np.concatenate([vector, np.asarray(revolutionary_topology_features, dtype=np.float32)]).astype(np.float32)
        plithogenic_topology_profile = None
        plithogenic_topology_features: Optional[List[float]] = None
        plithogenic_topology_plugin_payload: Optional[Dict[str, Any]] = None
        if plithogenic_profile is not None and revolutionary_topology_profile is not None:
            if plugin_hook_enabled:
                plithogenic_topology_plugin_payload = FfeDPluginBridge().run_mvp5(
                    self._plithogenic_topology_plugin_context(
                        events,
                        pairs,
                        plithogenic_profile,
                        revolutionary_topology_profile,
                        plugin_context=plugin_context,
                        cpai_context=cpai_context,
                    ),
                    include_trace=include_plugin_trace,
                    plugin_set=plugin_set,
                )
            plithogenic_topology_profile = plithogenic_topology_wiring_profile(
                events,
                pairs,
                plithogenic_profile,
                revolutionary_topology_profile,
                plugin_payload=plithogenic_topology_plugin_payload,
            )
            plithogenic_topology_features = [
                float(item)
                for item in plithogenic_topology_profile.get(
                    "stabilized_feature_vector",
                    plithogenic_topology_profile["feature_vector"],
                )
            ]
            vector = np.concatenate([vector, np.asarray(plithogenic_topology_features, dtype=np.float32)]).astype(np.float32)
        neutro_algebra_profile = None
        neutro_algebra_features: Optional[List[float]] = None
        if neutro_algebra_enabled:
            neutro_algebra_profile = neutroalgebra_runtime_profile(events, pairs, plithogenic_topology_profile)
            neutro_structure_profile = runtime_neutrostructure_profile(
                events,
                pairs,
                neutro_algebra_profile,
                plithogenic_topology_profile,
            )
            neutro_algebra_profile["structure_system_profile"] = neutro_structure_profile
            neutro_algebra_features = [
                float(item) for item in (
                    list(neutro_algebra_profile["feature_vector"])
                    + list(neutro_structure_profile["feature_vector"])
                )
            ]
            vector = np.concatenate([vector, np.asarray(neutro_algebra_features, dtype=np.float32)]).astype(np.float32)
        penrose_hameroff_profile = None
        penrose_hameroff_features: Optional[List[float]] = None
        if penrose_hameroff_enabled:
            penrose_hameroff_profile = penrose_hameroff_runtime_profile(
                events,
                pairs,
                objective_reduction_energy_joule=objective_reduction_energy_joule,
                coherence_time_s=coherence_time_s,
                anesthetic_damping=anesthetic_damping,
                microtubule_frequency_hz=microtubule_frequency_hz,
                spin_network_vertices=spin_network_vertices,
            )
            penrose_hameroff_features = [float(item) for item in penrose_hameroff_profile["feature_vector"]]
            vector = np.concatenate([vector, np.asarray(penrose_hameroff_features, dtype=np.float32)]).astype(np.float32)
        hydra_em_gpcn_profile = None
        hydra_em_gpcn_features: Optional[List[float]] = None
        if hydra_em_enabled and gpcn_set_phi_enabled and orch_or_simulation_enabled:
            hydra_em_gpcn_profile = hydra_em_gpcn_orch_profile(
                events,
                pairs,
                microtubule_proxy_count=microtubule_proxy_count,
                microtubule_coupling_strength=microtubule_coupling_strength,
                anesthetic_damping=anesthetic_damping,
                coherence_time_s=coherence_time_s,
                objective_reduction_energy_joule=objective_reduction_energy_joule,
                microtubule_frequency_hz=microtubule_frequency_hz,
                quasicrystal_projection_enabled=quasicrystal_projection_enabled,
                plithogenic_contradiction_threshold=plithogenic_contradiction_threshold,
                lattice_seed=lattice_seed,
                observation_scale_min=observation_scale_min,
                observation_scale_max=observation_scale_max,
            )
            hydra_em_gpcn_features = [float(item) for item in hydra_em_gpcn_profile["feature_vector"]]
            vector = np.concatenate([vector, np.asarray(hydra_em_gpcn_features, dtype=np.float32)]).astype(np.float32)
        lvfm = self._build_lvfm_snapshot(events, pairs)
        if plithogenic_profile is not None:
            lvfm["plithogenic_fusion_profile"] = {
                "model": plithogenic_profile["model"],
                "feature_vector": plithogenic_profile["feature_vector"],
                "feature_dimension": plithogenic_profile["feature_dimension"],
                "cumulative_truth": plithogenic_profile["cumulative_truth"],
                "weighted_cumulative_truth": plithogenic_profile["weighted_cumulative_truth"],
                "contradiction_summary": plithogenic_profile["contradiction_summary"],
                "hierarchy": plithogenic_profile["hierarchy"],
            }
        if revolutionary_topology_profile is not None:
            lvfm["revolutionary_topology_profile"] = {
                "model": revolutionary_topology_profile["model"],
                "feature_vector": revolutionary_topology_profile["feature_vector"],
                "feature_dimension": revolutionary_topology_profile["feature_dimension"],
                "topological_axiom_profile": revolutionary_topology_profile["topological_axiom_profile"],
                "deformation_signature": revolutionary_topology_profile["deformation_signature"],
                "hierarchy": revolutionary_topology_profile["hierarchy"],
            }
        if plithogenic_topology_profile is not None:
            lvfm["plithogenic_topology_profile"] = {
                "model": plithogenic_topology_profile["model"],
                "feature_vector": plithogenic_topology_profile["feature_vector"],
                "feature_dimension": plithogenic_topology_profile["feature_dimension"],
                "deterministic_decision": plithogenic_topology_profile["deterministic_decision"],
                "deterministic_confidence": plithogenic_topology_profile["deterministic_confidence"],
                "statistical_confidence": plithogenic_topology_profile["statistical_confidence"],
                "topology_variable_completion": plithogenic_topology_profile["topology_variable_completion"],
                "hierarchy": plithogenic_topology_profile["hierarchy"],
            }
            if "plugin_stabilization_profile" in plithogenic_topology_profile:
                lvfm["plithogenic_topology_profile"]["plugin_stabilization_profile"] = plithogenic_topology_profile[
                    "plugin_stabilization_profile"
                ]
                lvfm["plithogenic_topology_profile"]["plithogenic_topology_load_profile"] = plithogenic_topology_profile[
                    "plithogenic_topology_load_profile"
                ]
                lvfm["plithogenic_topology_profile"]["stabilized_feature_vector"] = plithogenic_topology_profile[
                    "stabilized_feature_vector"
                ]
                lvfm["plithogenic_topology_profile"]["stabilized_feature_dimension"] = plithogenic_topology_profile[
                    "stabilized_feature_dimension"
                ]
        if neutro_algebra_profile is not None:
            neutro_structure_profile = neutro_algebra_profile.get("structure_system_profile")
            lvfm["neutro_algebra_profile"] = {
                "model": neutro_algebra_profile["model"],
                "classification": neutro_algebra_profile["classification"],
                "feature_vector": neutro_algebra_profile["feature_vector"],
                "feature_dimension": neutro_algebra_profile["feature_dimension"],
                "runtime_mapping": neutro_algebra_profile["runtime_mapping"],
                "hierarchy": neutro_algebra_profile["hierarchy"],
            }
            if neutro_structure_profile is not None:
                lvfm["neutro_structure_profile"] = {
                    "model": neutro_structure_profile["model"],
                    "T_system": neutro_structure_profile["T_system"],
                    "I_system": neutro_structure_profile["I_system"],
                    "F_system": neutro_structure_profile["F_system"],
                    "system_classification": neutro_structure_profile["system_classification"],
                    "feature_vector": neutro_structure_profile["feature_vector"],
                    "feature_dimension": neutro_structure_profile["feature_dimension"],
                    "runtime_mapping": neutro_structure_profile["runtime_mapping"],
                    "hierarchy": neutro_structure_profile["hierarchy"],
                }
        if penrose_hameroff_profile is not None:
            lvfm["penrose_hameroff_profile"] = {
                "model": penrose_hameroff_profile["model"],
                "source_ids": penrose_hameroff_profile["source_ids"],
                "feature_vector": penrose_hameroff_profile["feature_vector"],
                "feature_dimension": penrose_hameroff_profile["feature_dimension"],
                "objective_reduction": penrose_hameroff_profile["objective_reduction"],
                "orchestration": penrose_hameroff_profile["orchestration"],
                "spin_network": penrose_hameroff_profile["spin_network"],
                "twistor_nonlocality": penrose_hameroff_profile["twistor_nonlocality"],
                "microtubule_signal": penrose_hameroff_profile["microtubule_signal"],
                "hierarchy": penrose_hameroff_profile["hierarchy"],
                "research_boundary": penrose_hameroff_profile["research_boundary"],
            }
        if hydra_em_gpcn_profile is not None:
            lvfm["hydra_em_gpcn_profile"] = {
                "model": hydra_em_gpcn_profile["model"],
                "source_ids": hydra_em_gpcn_profile["source_ids"],
                "feature_vector": hydra_em_gpcn_profile["feature_vector"],
                "feature_dimension": hydra_em_gpcn_profile["feature_dimension"],
                "axiomatic_container": hydra_em_gpcn_profile["axiomatic_container"],
                "objective_reduction": hydra_em_gpcn_profile["objective_reduction"],
                "orchestration": hydra_em_gpcn_profile["orchestration"],
                "quasicrystal_projection": hydra_em_gpcn_profile["quasicrystal_projection"],
                "simulation_scores": hydra_em_gpcn_profile["simulation_scores"],
                "verdict": hydra_em_gpcn_profile["verdict"],
                "hierarchy": hydra_em_gpcn_profile["hierarchy"],
                "research_boundary": hydra_em_gpcn_profile["research_boundary"],
            }
        fractal_carrier = self._fractal_carrier_payload(
            fractal_dimension,
            fractal_dimension_min,
            fractal_dimension_max,
            fractal_admissible,
            fractal_measurement_method,
            fractal_scale,
            domain="lvfm-runtime-snapshot",
        )
        if fractal_carrier is not None:
            lvfm["fractal_carrier"] = fractal_carrier
            lvfm["i_fractal_candidate"] = fractal_carrier["i_fractal_candidate"]
        qnn_result = None
        if qnn_nucleus is not None:
            qnn_result = qnn_nucleus.smoke_run(
                observations,
                label=label,
                max_epochs=max_epochs,
                test_size=0.0,
                state_basis=state_basis,
                puncture_delta=puncture_delta,
                observer_strength=observer_strength,
                fractal_dimension=fractal_dimension,
                fractal_dimension_min=fractal_dimension_min,
                fractal_dimension_max=fractal_dimension_max,
                fractal_admissible=fractal_admissible,
                fractal_measurement_method=fractal_measurement_method,
                fractal_scale=fractal_scale,
                plugin_hook_enabled=plugin_hook_enabled and plithogenic_topology_plugin_payload is None,
                plugin_set=plugin_set,
                plugin_context=dict(plugin_context or {}),
                cpai_context=dict(cpai_context or {}),
                include_plugin_trace=include_plugin_trace,
                plithogenic_features=plithogenic_features,
                plithogenic_payload=plithogenic_profile,
                revolutionary_topology_features=revolutionary_topology_features,
                revolutionary_topology_payload=revolutionary_topology_profile,
                plithogenic_topology_features=plithogenic_topology_features,
                plithogenic_topology_payload=plithogenic_topology_profile,
                neutro_algebra_features=neutro_algebra_features,
                neutro_algebra_payload=neutro_algebra_profile,
                penrose_hameroff_features=penrose_hameroff_features,
                penrose_hameroff_payload=penrose_hameroff_profile,
                hydra_em_gpcn_features=hydra_em_gpcn_features,
                hydra_em_gpcn_payload=hydra_em_gpcn_profile,
                precomputed_plugin_payload=plithogenic_topology_plugin_payload,
            )
            qnn_result.pop("bundle", None)
            if qnn_result.get("plugin_fractal_carrier") is not None:
                lvfm["plugin_fractal_carrier"] = qnn_result.get("plugin_fractal_carrier")
                lvfm["plugin_tension_profile"] = qnn_result.get("plugin_tension_profile")
                lvfm["impact_verification"] = qnn_result.get("impact_verification")
        return CerebrumRuntimeState(
            events=events,
            pairs=pairs,
            observations=observations,
            feature_bundle=bundle,
            feature_vector=vector,
            qnn_result=qnn_result,
            warnings=warnings,
            lvfm=lvfm,
            plithogenic=plithogenic_profile,
            revolutionary_topology=revolutionary_topology_profile,
            plithogenic_topology=plithogenic_topology_profile,
            neutro_algebra=neutro_algebra_profile,
            penrose_hameroff=penrose_hameroff_profile,
            hydra_em_gpcn=hydra_em_gpcn_profile,
        )

    def _fractal_carrier_payload(
        self,
        fractal_dimension: Optional[float],
        fractal_dimension_min: Optional[float],
        fractal_dimension_max: Optional[float],
        fractal_admissible: bool,
        fractal_measurement_method: Optional[str],
        fractal_scale: Optional[str],
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        if fractal_dimension is None or fractal_dimension_min is None or fractal_dimension_max is None:
            return None
        return fractal_carrier_profile(
            fractal_dimension,
            fractal_dimension_min,
            fractal_dimension_max,
            measurement_method=fractal_measurement_method or "provided-fractal-dimension",
            scale=fractal_scale,
            domain=domain,
            admissible=fractal_admissible,
        )

    def _plithogenic_topology_plugin_context(
        self,
        events: Sequence[CerebrumMemoryEvent],
        pairs: Sequence[CrossModalPair],
        plithogenic_profile: Mapping[str, Any],
        revolutionary_topology_profile: Mapping[str, Any],
        *,
        plugin_context: Optional[Mapping[str, Any]],
        cpai_context: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        context = dict(plugin_context or {})
        observations = [event.to_observation() for event in events]
        attributes = list((plithogenic_profile.get("attribute_profile") or {}).get("attributes") or [])
        truth_series = [self._coerce_float(attribute.get("truth"), 0.0) for attribute in attributes]
        indeterminacy_series = [self._coerce_float(attribute.get("indeterminacy"), 0.0) for attribute in attributes]
        falsity_series = [self._coerce_float(attribute.get("falsity"), 0.0) for attribute in attributes]
        topology_features = [self._coerce_float(item, 0.0) for item in revolutionary_topology_profile.get("feature_vector", [])]
        event_values = [event.value for event in events]
        series = context.get("series") or [
            *event_values,
            *truth_series,
            *indeterminacy_series,
            *falsity_series,
            *topology_features,
        ]
        items = context.get("items") or [
            {
                "label": str(attribute.get("attribute_id", attribute.get("variable", f"attribute-{index}"))),
                "truth": self._coerce_float(attribute.get("truth"), 0.0),
                "indeterminacy": self._coerce_float(attribute.get("indeterminacy"), 0.0),
                "falsity": self._coerce_float(attribute.get("falsity"), 0.0),
            }
            for index, attribute in enumerate(attributes)
        ]
        estimated_load = min(
            1.0,
            max(
                0.0,
                len(events) / MAX_RUNTIME_EVENTS
                + len(pairs) / MAX_RUNTIME_PAIRS
                + len(topology_features) / 256.0,
            ),
        )
        merged_cpai_context = dict(cpai_context or {})
        merged_cpai_context.setdefault("local_load", estimated_load)
        context.update(
            {
                "events": observations,
                "observations": observations,
                "series": [self._coerce_float(value, 0.0) for value in list(series)[:64]],
                "items": list(items)[:16],
                "cpai_context": merged_cpai_context,
                "plithogenic_topology_load": {
                    "event_count": len(events),
                    "pair_count": len(pairs),
                    "topology_feature_count": len(topology_features),
                    "estimated_load": estimated_load,
                },
            }
        )
        return context

    def _build_lvfm_snapshot(
        self,
        events: Sequence[CerebrumMemoryEvent],
        pairs: Sequence[CrossModalPair],
    ) -> Dict[str, Any]:
        graph = LVFMRuntimeGraph()

        def _normalize_bit(event: CerebrumMemoryEvent) -> RegisterBit:
            t = float(min(1.0, max(0.0, event.value)))
            f = float(min(1.0, max(0.0, 1.0 - event.value)))
            d_f = float(min(1.0, max(0.0, 1.0 - abs(t - f))))
            duration_signal = float(min(1.0, max(0.0, event.duration / 4.0)))
            d_f = float(min(1.0, (d_f + duration_signal) / 2.0))
            return RegisterBit(t=t, d_f=d_f, f=f)

        events_by_key: Dict[Tuple[str, float], List[int]] = {}
        for idx, event in enumerate(events):
            node_id = f"{event.modality}:{idx}:{event.starting_time:.6f}"
            graph.register_node(
                node_id=node_id,
                bit=_normalize_bit(event),
                register_weight=max(1e-6, event.duration),
                metadata={
                    "modality": event.modality,
                    "source": event.source,
                    "label": event.label,
                    "payload_ref": event.payload_ref,
                },
            )
            events_by_key.setdefault((event.modality, round(event.starting_time, 6)), []).append(idx)

        def _find_node(modality: str, timestamp: float) -> str | None:
            rounded = round(timestamp, 6)
            key = (modality, rounded)
            candidates = events_by_key.get(key, [])
            if candidates:
                return f"{modality}:{candidates[0]}:{events[candidates[0]].starting_time:.6f}"
            closest_idx: Optional[int] = None
            closest_delta = float("inf")
            for candidate_idx, event in enumerate(events):
                if event.modality != modality:
                    continue
                delta = abs(event.starting_time - timestamp)
                if delta < closest_delta:
                    closest_delta = delta
                    closest_idx = candidate_idx
            if closest_idx is None or closest_delta > 1.0:
                return None
            return f"{modality}:{closest_idx}:{events[closest_idx].starting_time:.6f}"

        for pair in pairs:
            source_node = _find_node(pair.source_modality, pair.timestamp1)
            target_node = _find_node(pair.target_modality, pair.timestamp2)
            if source_node is None or target_node is None:
                continue
            if source_node == target_node:
                continue
            graph.add_edge(source_node, target_node, weight=pair.overlap_score)

        if graph.edge_count() == 0:
            ordered_nodes = sorted(graph.nodes)
            for left, right in zip(ordered_nodes, ordered_nodes[1:]):
                graph.add_edge(left, right, weight=1.0)

        return graph.to_snapshot()

    def build_pairs(self, events: Sequence[CerebrumMemoryEvent]) -> List[CrossModalPair]:
        if len(events) > MAX_RUNTIME_EVENTS:
            events = events[:MAX_RUNTIME_EVENTS]
        pairs: List[CrossModalPair] = []
        for left_index, left in enumerate(events):
            for right in events[left_index + 1 :]:
                if len(pairs) >= MAX_RUNTIME_PAIRS:
                    return sorted(pairs, key=lambda pair: (pair.timestamp1, pair.direction, pair.timestamp2))
                if left.modality == right.modality:
                    continue
                overlap_score = self._overlap_score(left, right)
                if overlap_score <= 0.0:
                    continue
                pairs.append(self._pair(left, right, overlap_score))
                pairs.append(self._pair(right, left, overlap_score))
        return sorted(pairs, key=lambda pair: (pair.timestamp1, pair.direction, pair.timestamp2))

    def _pair(self, source: CerebrumMemoryEvent, target: CerebrumMemoryEvent, overlap_score: float) -> CrossModalPair:
        direction = f"{PAIR_CODE[source.modality]}2{PAIR_CODE[target.modality]}"
        return CrossModalPair(
            timestamp1=source.starting_time,
            timestamp2=target.starting_time,
            direction=direction,
            source_modality=source.modality,
            target_modality=target.modality,
            overlap_score=overlap_score,
        )

    def _extract_records(self, payload: Mapping[str, Any] | Sequence[Any] | None, warnings: List[str]) -> List[Mapping[str, Any]]:
        if payload is None:
            if self.legacy_cerebrum_path is not None:
                legacy_records = self._load_legacy_snapshot(self.legacy_cerebrum_path, warnings=warnings)
                if legacy_records:
                    return legacy_records
            return self.default_payload()["memories"]
        if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray, Mapping)):
            if len(payload) > MAX_RUNTIME_EVENTS:
                warnings.append(f"Runtime payload truncated to {MAX_RUNTIME_EVENTS} events.")
            return [record if isinstance(record, Mapping) else {"value": record} for record in payload[:MAX_RUNTIME_EVENTS]]
        if not isinstance(payload, Mapping):
            return [{"value": payload}]

        if "memories" in payload:
            memories = payload.get("memories", [])
            if len(memories) > MAX_RUNTIME_EVENTS:
                warnings.append(f"Runtime memories truncated to {MAX_RUNTIME_EVENTS} events.")
            return [record if isinstance(record, Mapping) else {"value": record} for record in memories[:MAX_RUNTIME_EVENTS]]
        if "events" in payload:
            events = payload.get("events", [])
            if len(events) > MAX_RUNTIME_EVENTS:
                warnings.append(f"Runtime events truncated to {MAX_RUNTIME_EVENTS} events.")
            return [record if isinstance(record, Mapping) else {"value": record} for record in events[:MAX_RUNTIME_EVENTS]]
        if "observations" in payload:
            observations = payload.get("observations", [])
            if len(observations) > MAX_RUNTIME_EVENTS:
                warnings.append(f"Runtime observations truncated to {MAX_RUNTIME_EVENTS} events.")
            return [record if isinstance(record, Mapping) else {"value": record} for record in observations[:MAX_RUNTIME_EVENTS]]
        if any(table_name in payload for table_name in LEGACY_TABLE_MODALITIES) or "crossmodal_mappings" in payload:
            return self._legacy_table_payload_to_records(payload)
        if "legacy_snapshot" in payload:
            snapshot_records = self._load_legacy_snapshot(payload.get("legacy_snapshot"), warnings=warnings)
            if snapshot_records:
                return snapshot_records

        records: List[Mapping[str, Any]] = []
        for key, modality in COLLECTION_MODALITIES.items():
            items = payload.get(key)
            if items is None:
                continue
            if not isinstance(items, Sequence) or isinstance(items, (str, bytes, bytearray)):
                items = [items]
            for item in items:
                if isinstance(item, Mapping):
                    record = dict(item)
                    record.setdefault("modality", modality)
                else:
                    record = {"modality": modality, "value": item}
                records.append(record)
        return records

    def _extract_pairs(
        self,
        payload: Mapping[str, Any] | Sequence[Any] | None,
        events: Sequence[CerebrumMemoryEvent],
        warnings: List[str],
    ) -> List[CrossModalPair]:
        if isinstance(payload, Mapping) and "pairs" in payload:
            pairs = self._normalize_pairs(payload.get("pairs"), warnings)
            if pairs:
                return pairs
        if isinstance(payload, Mapping) and "crossmodal_mappings" in payload:
            pairs = self._normalize_pairs(payload.get("crossmodal_mappings"), warnings)
            if pairs:
                return pairs
        return self.build_pairs(events)

    def _parse_record(self, record: Mapping[str, Any], index: int, warnings: List[str]) -> Optional[CerebrumMemoryEvent]:
        modality_raw = str(record.get("modality") or record.get("channel") or record.get("type") or "stimuli").lower()
        modality = MODALITY_ALIASES.get(modality_raw, "stimuli")
        if modality_raw not in MODALITY_ALIASES:
            warnings.append(f"Unknown modality '{modality_raw}' mapped to stimuli.")

        start_raw = record.get("starting_time", record.get("timestamp", record.get("time", index)))
        end_raw = record.get("ending_time", record.get("end_time", record.get("ending", None)))
        start = self._parse_time(start_raw, float(index), warnings)
        if end_raw is None:
            duration = self._coerce_float(record.get("duration", 1.0), 1.0)
            end = start + max(duration, 0.0)
        else:
            end = self._parse_time(end_raw, start + 1.0, warnings)
        if end < start:
            warnings.append(f"Event {index} had ending_time before starting_time; values were swapped.")
            start, end = end, start

        value_raw = record.get("value", record.get("intensity", record.get("payload", record.get("data", 0.0))))
        value = self._coerce_value(value_raw, modality)
        label = str(record.get("label", record.get("stimulus", record.get("direction", ""))))
        source = str(record.get("source", record.get("origin", "cerebrum-runtime")))
        payload_ref = str(record.get("payload_ref", record.get("memory_id", record.get("id", ""))))
        provenance = record.get("provenance") if isinstance(record.get("provenance"), Mapping) else {}
        return CerebrumMemoryEvent(
            modality=modality,
            starting_time=start,
            ending_time=end,
            value=value,
            source=source,
            label=label,
            payload_ref=payload_ref,
            provenance=dict(provenance),
        )

    def _normalize_event_times(self, events: Sequence[CerebrumMemoryEvent]) -> List[CerebrumMemoryEvent]:
        if not events:
            return []
        origin = min(event.starting_time for event in events)
        normalized = [
            CerebrumMemoryEvent(
                modality=event.modality,
                starting_time=event.starting_time - origin,
                ending_time=event.ending_time - origin,
                value=event.value,
                source=event.source,
                label=event.label,
                payload_ref=event.payload_ref,
                provenance=event.provenance,
            )
            for event in events
        ]
        return sorted(normalized, key=lambda event: (event.starting_time, event.modality))

    def _normalize_pairs(self, payload: Any, warnings: List[str]) -> List[CrossModalPair]:
        if payload is None:
            return []
        records = payload if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)) else [payload]
        pairs: List[CrossModalPair] = []
        for record in records:
            if not isinstance(record, Mapping):
                continue
            direction = str(record.get("direction", "")).upper()
            if direction not in PAIR_DIRECTION_ALIASES:
                warnings.append(f"Unknown pair direction '{direction}' ignored.")
                continue
            source_modality, target_modality = PAIR_DIRECTION_ALIASES[direction]
            pairs.append(
                CrossModalPair(
                    timestamp1=self._coerce_float(record.get("timestamp1", record.get("starting_time", 0.0)), 0.0),
                    timestamp2=self._coerce_float(record.get("timestamp2", record.get("ending_time", 0.0)), 0.0),
                    direction=direction,
                    source_modality=source_modality,
                    target_modality=target_modality,
                    overlap_score=max(0.0, min(1.0, self._coerce_float(record.get("overlap_score", 1.0), 1.0))),
                )
            )
        return sorted(pairs, key=lambda pair: (pair.timestamp1, pair.direction, pair.timestamp2))

    def _overlap_score(self, left: CerebrumMemoryEvent, right: CerebrumMemoryEvent) -> float:
        overlap = min(left.ending_time, right.ending_time) - max(left.starting_time, right.starting_time)
        if overlap <= 0.0:
            return 0.0
        denominator = max(min(left.duration, right.duration), 1e-9)
        return float(min(1.0, overlap / denominator))

    def _parse_time(self, raw_value: Any, fallback: float, warnings: List[str]) -> float:
        if isinstance(raw_value, (int, float, np.floating, np.integer)):
            return float(raw_value)
        if isinstance(raw_value, datetime):
            return raw_value.timestamp()
        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if not stripped:
                return fallback
            try:
                return float(stripped)
            except ValueError:
                pass
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(stripped, fmt).timestamp()
                except ValueError:
                    pass
            try:
                return datetime.fromisoformat(stripped.replace("Z", "+00:00")).timestamp()
            except ValueError:
                warnings.append(f"Could not parse time '{stripped}', using fallback {fallback}.")
        return fallback

    def _coerce_value(self, raw_value: Any, modality: str) -> float:
        if raw_value is None:
            return 0.0
        if isinstance(raw_value, (int, float, np.floating, np.integer)):
            return float(raw_value)
        if isinstance(raw_value, str):
            stripped = raw_value.strip()
            if not stripped:
                return 0.0
            try:
                return float(stripped)
            except ValueError:
                return min(1.0, len(stripped) / 100.0)
        if isinstance(raw_value, Mapping):
            numeric_values = [self._coerce_float(value, np.nan) for value in raw_value.values()]
            numeric_values = [value for value in numeric_values if np.isfinite(value)]
            return float(np.mean(numeric_values)) if numeric_values else min(1.0, len(str(raw_value)) / 100.0)
        if isinstance(raw_value, Sequence) and not isinstance(raw_value, (bytes, bytearray)):
            values = [self._coerce_float(value, np.nan) for value in raw_value]
            values = [value for value in values if np.isfinite(value)]
            return float(np.mean(values)) if values else 0.0
        return min(1.0, len(str(raw_value)) / 100.0)

    def _coerce_float(self, raw_value: Any, fallback: float) -> float:
        try:
            return float(raw_value)
        except (TypeError, ValueError):
            return fallback

    def _load_legacy_snapshot(self, snapshot: Any, warnings: Optional[List[str]] = None) -> List[Mapping[str, Any]]:
        warnings = warnings if warnings is not None else []
        if snapshot is None:
            return []
        path = Path(str(snapshot)).resolve()
        project_root = Path(__file__).resolve().parent.parent
        temp_root = Path(tempfile.gettempdir()).resolve()
        if (
            project_root not in path.parents
            and path != project_root
            and temp_root not in path.parents
            and path != temp_root
        ):
            warnings.append(f"Legacy snapshot path '{path}' is outside the project tree.")
            return []
        if not path.exists():
            warnings.append(f"Legacy snapshot path '{path}' does not exist.")
            return []

        records: List[Mapping[str, Any]] = []
        candidates = [path] if path.is_file() else sorted(
            item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in {".json", ".jsonl", ".ndjson"}
        )
        for candidate in candidates:
            try:
                if candidate.stat().st_size > MAX_LEGACY_SNAPSHOT_BYTES:
                    warnings.append(f"Legacy snapshot file '{candidate}' exceeds the size limit.")
                    continue
                if candidate.suffix.lower() == ".json":
                    loaded = json.loads(candidate.read_text(encoding="utf-8"))
                    records.extend(self._legacy_payload_to_records(loaded, candidate))
                    continue
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    records.extend(self._legacy_payload_to_records(json.loads(line), candidate))
            except Exception as exc:  # pragma: no cover - best-effort legacy path
                warnings.append(f"Legacy snapshot file '{candidate}' could not be read: {exc}")
        return records

    def _legacy_payload_to_records(self, loaded: Any, source: Path) -> List[Mapping[str, Any]]:
        if isinstance(loaded, Mapping):
            if any(table_name in loaded for table_name in LEGACY_TABLE_MODALITIES):
                return self._legacy_table_payload_to_records(loaded)
            if "memories" in loaded:
                return [record if isinstance(record, Mapping) else {"value": record} for record in loaded.get("memories", [])]
            if "pairs" in loaded:
                return [record if isinstance(record, Mapping) else {"value": record} for record in loaded.get("pairs", [])]
            return [dict(loaded)]
        if isinstance(loaded, Sequence) and not isinstance(loaded, (str, bytes, bytearray)):
            records: List[Mapping[str, Any]] = []
            for item in loaded:
                if isinstance(item, Mapping):
                    records.append(dict(item))
                else:
                    records.append({"value": item, "source": source.stem})
            return records
        return [{"value": loaded, "source": source.stem}]

    def _legacy_table_payload_to_records(self, tables: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        records: List[Mapping[str, Any]] = []
        for table_name, modality in LEGACY_TABLE_MODALITIES.items():
            entries = tables.get(table_name, [])
            if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes, bytearray)):
                entries = [entries]
            for entry in entries:
                if not isinstance(entry, Mapping):
                    continue
                records.append(
                    {
                        "modality": modality,
                        "starting_time": entry.get("starting_time", entry.get("timestamp", 0.0)),
                        "ending_time": entry.get("ending_time", entry.get("timestamp", entry.get("starting_time", 0.0))),
                        "value": entry.get("value", entry.get("data", 0.0)),
                        "label": entry.get("label", table_name),
                        "source": entry.get("source", table_name),
                        "payload_ref": entry.get("payload_ref", entry.get("memory_id", "")),
                    }
                )
        return records

    def default_payload(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "memories": [
                {
                    "modality": "hearing",
                    "starting_time": 0.0,
                    "ending_time": 1.4,
                    "value": 0.73,
                    "label": "rhythm",
                    "source": "demo-hearing",
                    "payload_ref": "hearing-001",
                },
                {
                    "modality": "vision",
                    "starting_time": 0.8,
                    "ending_time": 2.2,
                    "value": 0.61,
                    "label": "motion",
                    "source": "demo-vision",
                    "payload_ref": "vision-001",
                },
                {
                    "modality": "language",
                    "starting_time": 1.6,
                    "ending_time": 2.9,
                    "value": 0.54,
                    "label": "caption",
                    "source": "demo-language",
                    "payload_ref": "language-001",
                },
                {
                    "modality": "stimuli",
                    "starting_time": 2.4,
                    "ending_time": 3.0,
                    "value": 0.82,
                    "label": "trigger",
                    "source": "demo-stimuli",
                    "payload_ref": "stimuli-001",
                },
            ]
        }

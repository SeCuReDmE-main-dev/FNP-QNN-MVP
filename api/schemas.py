"""Pydantic contracts for the local alpha API surface."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_MODALITIES = {"audio", "video", "text", "stimuli", "hearing", "vision", "language", "stimulus"}
MAX_EVENTS = 1000
MAX_LABEL_LENGTH = 120
PLUGIN_SET = Literal["mvp5"]


def _finite(value: float, field_name: str) -> float:
    if not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")
    return float(value)


def _copy_fractal_aliases(values):
    if not isinstance(values, dict):
        return values
    updated = dict(values)
    aliases = {
        "D_f": "fractal_dimension",
        "D_min": "fractal_dimension_min",
        "D_max": "fractal_dimension_max",
    }
    for alias, field_name in aliases.items():
        if alias in updated and field_name not in updated:
            updated[field_name] = updated[alias]
    return updated


class Observation(BaseModel):
    modality: str = Field(default="stimuli", max_length=32)
    value: Any = 0.0
    timestamp: Optional[float] = None
    starting_time: Optional[float] = None
    ending_time: Optional[float] = None
    end_time: Optional[float] = None
    label: str = Field(default="", max_length=MAX_LABEL_LENGTH)
    source: str = Field(default="", max_length=MAX_LABEL_LENGTH)
    weight: float = 1.0
    payload_ref: str = Field(default="", max_length=MAX_LABEL_LENGTH)
    provenance: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("modality")
    @classmethod
    def validate_modality(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in ALLOWED_MODALITIES:
            raise ValueError(f"Unsupported modality '{value}'")
        return normalized

    @field_validator("timestamp", "starting_time", "ending_time", "end_time", "weight")
    @classmethod
    def validate_finite_optional(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    @model_validator(mode="after")
    def validate_time_order(self):
        start = self.starting_time if self.starting_time is not None else self.timestamp
        end = self.ending_time if self.ending_time is not None else self.end_time
        if start is not None and end is not None and end < start:
            raise ValueError("ending_time must be greater than or equal to starting_time")
        return self


class RuntimeRunRequest(BaseModel):
    memories: Optional[List[Observation]] = None
    events: Optional[List[Observation]] = None
    observations: Optional[List[Observation]] = None
    statefield: Optional[Dict[str, Any]] = None
    label: float = 1.0
    epochs: int = Field(default=12, ge=0, le=256)
    run_qnn: bool = True
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True
    plithogenic_enabled: bool = False
    revolutionary_topology_enabled: bool = False
    neutro_algebra_enabled: bool = False

    @model_validator(mode="before")
    @classmethod
    def accept_fractal_aliases(cls, values):
        return _copy_fractal_aliases(values)

    @field_validator("memories", "events", "observations")
    @classmethod
    def validate_event_count(cls, value: Optional[List[Observation]]):
        if value is not None and len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} events are accepted")
        return value

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: float) -> float:
        return _finite(value, "label")

    @field_validator("fractal_dimension", "fractal_dimension_min", "fractal_dimension_max")
    @classmethod
    def validate_fractal_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    def to_runtime_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "label": self.label,
            "epochs": self.epochs,
            "state_basis": self.state_basis,
        }
        if self.puncture_delta is not None:
            payload["puncture_delta"] = self.puncture_delta
        if self.observer_strength is not None:
            payload["observer_strength"] = self.observer_strength
        payload.update(self.fractal_payload())
        payload.update(self.plugin_payload())
        payload["plithogenic_enabled"] = self.plithogenic_enabled
        payload["revolutionary_topology_enabled"] = self.revolutionary_topology_enabled
        payload["neutro_algebra_enabled"] = self.neutro_algebra_enabled
        if self.memories is not None:
            payload["memories"] = [item.model_dump(exclude_none=True) for item in self.memories]
        if self.events is not None:
            payload["events"] = [item.model_dump(exclude_none=True) for item in self.events]
        if self.observations is not None:
            payload["observations"] = [item.model_dump(exclude_none=True) for item in self.observations]
        if self.statefield is not None:
            payload["statefield"] = self.statefield
        return payload

    def plugin_payload(self) -> Dict[str, Any]:
        return {
            "plugin_hook_enabled": self.plugin_hook_enabled,
            "plugin_set": self.plugin_set,
            "plugin_context": self.plugin_context,
            "cpai_context": self.cpai_context,
            "include_plugin_trace": self.include_plugin_trace,
        }

    def fractal_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"fractal_admissible": self.fractal_admissible}
        if self.fractal_dimension is not None:
            payload["fractal_dimension"] = self.fractal_dimension
        if self.fractal_dimension_min is not None:
            payload["fractal_dimension_min"] = self.fractal_dimension_min
        if self.fractal_dimension_max is not None:
            payload["fractal_dimension_max"] = self.fractal_dimension_max
        if self.fractal_measurement_method is not None:
            payload["fractal_measurement_method"] = self.fractal_measurement_method
        if self.fractal_scale is not None:
            payload["fractal_scale"] = self.fractal_scale
        return payload


class EncodeRequest(BaseModel):
    observations: List[Observation] = Field(default_factory=list)

    @field_validator("observations")
    @classmethod
    def validate_observation_count(cls, value: List[Observation]):
        if len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} observations are accepted")
        return value


class QNNSmokeRequest(BaseModel):
    samples: Optional[List[List[Observation]]] = None
    labels: Optional[List[int]] = None
    epochs: int = Field(default=24, ge=0, le=256)
    test_size: float = Field(default=0.25, ge=0.0, le=0.9)
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True

    @model_validator(mode="before")
    @classmethod
    def accept_fractal_aliases(cls, values):
        return _copy_fractal_aliases(values)

    @model_validator(mode="after")
    def validate_samples_and_labels(self):
        if self.samples is None and self.labels is None:
            return self
        if not self.samples or not self.labels:
            raise ValueError("samples and labels must be provided together")
        if len(self.samples) != len(self.labels):
            raise ValueError("samples and labels must have the same length")
        if len(self.samples) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} samples are accepted")
        return self

    @field_validator("fractal_dimension", "fractal_dimension_min", "fractal_dimension_max")
    @classmethod
    def validate_fractal_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    def dump_samples(self) -> Optional[List[List[Dict[str, Any]]]]:
        if self.samples is None:
            return None
        return [[event.model_dump(exclude_none=True) for event in sample] for sample in self.samples]


class NeuroBitProfileRequest(BaseModel):
    truth: float = Field(default=0.55, ge=0.0)
    indeterminacy: float = Field(default=0.30, ge=0.0)
    falsity: float = Field(default=0.15, ge=0.0)
    delta_falsity: float = 0.0
    n_qubits: int = Field(default=4, ge=1, le=12)
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    surface_width: Optional[float] = Field(default=None, gt=0.0, le=256.0)
    surface_height: Optional[float] = Field(default=None, gt=0.0, le=256.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True

    @model_validator(mode="before")
    @classmethod
    def accept_df_alias(cls, values):
        if isinstance(values, dict) and "dF" in values and "delta_falsity" not in values:
            values = dict(values)
            values["delta_falsity"] = values.pop("dF")
        values = _copy_fractal_aliases(values)
        return values

    @field_validator(
        "truth",
        "indeterminacy",
        "falsity",
        "delta_falsity",
        "fractal_dimension",
        "fractal_dimension_min",
        "fractal_dimension_max",
    )
    @classmethod
    def validate_neurobit_numbers(cls, value: Optional[float], info):
        if value is None:
            return value
        return _finite(value, info.field_name)

    def to_profile_payload(self) -> Dict[str, Any]:
        return {
            "truth": self.truth,
            "indeterminacy": self.indeterminacy,
            "falsity": self.falsity,
            "delta_falsity": self.delta_falsity,
            "state_basis": self.state_basis,
            "puncture_delta": self.puncture_delta,
            "observer_strength": self.observer_strength,
            "surface_width": self.surface_width,
            "surface_height": self.surface_height,
            "fractal_dimension": self.fractal_dimension,
            "fractal_dimension_min": self.fractal_dimension_min,
            "fractal_dimension_max": self.fractal_dimension_max,
            "fractal_admissible": self.fractal_admissible,
            "fractal_measurement_method": self.fractal_measurement_method,
            "fractal_scale": self.fractal_scale,
            "plugin_hook_enabled": self.plugin_hook_enabled,
            "plugin_set": self.plugin_set,
            "plugin_context": self.plugin_context,
            "cpai_context": self.cpai_context,
            "include_plugin_trace": self.include_plugin_trace,
        }


class NeuroBitTunnelRequest(NeuroBitProfileRequest):
    data: str = Field(default="neurobit-demo", max_length=4096)


class NidusTripletProfileRequest(BaseModel):
    truth: float = Field(default=0.55, ge=0.0)
    indeterminacy: float = Field(default=0.30, ge=0.0)
    falsity: float = Field(default=0.15, ge=0.0)

    @model_validator(mode="before")
    @classmethod
    def accept_tif_aliases(cls, values):
        if not isinstance(values, dict):
            return values
        updated = dict(values)
        aliases = {
            "T": "truth",
            "I": "indeterminacy",
            "F": "falsity",
        }
        for alias, field_name in aliases.items():
            if alias in updated and field_name not in updated:
                updated[field_name] = updated[alias]
        return updated

    @field_validator("truth", "indeterminacy", "falsity")
    @classmethod
    def validate_triplet_numbers(cls, value: float, info):
        return _finite(value, info.field_name)


class NidusFusionSource(BaseModel):
    truth: float = Field(default=0.0, ge=0.0)
    indeterminacy: float = Field(default=0.0, ge=0.0)
    falsity: float = Field(default=0.0, ge=0.0)
    weight: float = Field(default=1.0, ge=0.0)
    intersection_indeterminacy: float = Field(default=0.0, ge=0.0)
    label: str = Field(default="", max_length=MAX_LABEL_LENGTH)

    @model_validator(mode="before")
    @classmethod
    def accept_source_aliases(cls, values):
        if not isinstance(values, dict):
            return values
        updated = dict(values)
        aliases = {
            "T": "truth",
            "I": "indeterminacy",
            "F": "falsity",
            "beta": "weight",
            "source_importance": "weight",
            "indeterminate_intersection": "intersection_indeterminacy",
            "intersection_unknown": "intersection_indeterminacy",
        }
        for alias, field_name in aliases.items():
            if alias in updated and field_name not in updated:
                updated[field_name] = updated[alias]
        return updated

    @field_validator("truth", "indeterminacy", "falsity", "weight", "intersection_indeterminacy")
    @classmethod
    def validate_source_numbers(cls, value: float, info):
        return _finite(value, info.field_name)

    def to_fusion_payload(self) -> Dict[str, Any]:
        payload = {
            "truth": self.truth,
            "indeterminacy": self.indeterminacy,
            "falsity": self.falsity,
            "weight": self.weight,
            "intersection_indeterminacy": self.intersection_indeterminacy,
        }
        if self.label:
            payload["label"] = self.label
        return payload


class NidusFusionProfileRequest(BaseModel):
    sources: List[NidusFusionSource] = Field(default_factory=list)

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, value: List[NidusFusionSource]):
        if not value:
            raise ValueError("sources must contain at least one source")
        if len(value) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} sources are accepted")
        return value

    def dump_sources(self) -> List[Dict[str, Any]]:
        return [source.to_fusion_payload() for source in self.sources]


class NidusPartialMembershipMeanRequest(BaseModel):
    values: List[float] = Field(default_factory=list)
    memberships: List[float] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lengths(self):
        if not self.values:
            raise ValueError("values must not be empty")
        if len(self.values) != len(self.memberships):
            raise ValueError("values and memberships must have the same length")
        if len(self.values) > MAX_EVENTS:
            raise ValueError(f"At most {MAX_EVENTS} values are accepted")
        return self

    @field_validator("values", "memberships")
    @classmethod
    def validate_numeric_lists(cls, value: List[float], info):
        for item in value:
            _finite(item, info.field_name)
        if info.field_name == "memberships" and any(float(item) < 0.0 for item in value):
            raise ValueError("memberships must be non-negative")
        return value


class CommandRequest(BaseModel):
    payload: Optional[RuntimeRunRequest] = None
    observations: Optional[List[Observation]] = None
    samples: Optional[List[List[Observation]]] = None
    labels: Optional[List[int]] = None
    epochs: int = Field(default=24, ge=0, le=256)
    test_size: float = Field(default=0.25, ge=0.0, le=0.9)
    state_basis: Literal["binary", "neutrobit"] = "binary"
    puncture_delta: Optional[float] = Field(default=None, gt=0.0)
    observer_strength: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    fractal_dimension: Optional[float] = None
    fractal_dimension_min: Optional[float] = None
    fractal_dimension_max: Optional[float] = None
    fractal_admissible: bool = True
    fractal_measurement_method: Optional[str] = Field(default=None, max_length=120)
    fractal_scale: Optional[str] = Field(default=None, max_length=120)
    plugin_hook_enabled: bool = False
    plugin_set: PLUGIN_SET = "mvp5"
    plugin_context: Dict[str, Any] = Field(default_factory=dict)
    cpai_context: Dict[str, Any] = Field(default_factory=dict)
    include_plugin_trace: bool = True
    neurobit: Optional[NeuroBitTunnelRequest] = None

    @model_validator(mode="before")
    @classmethod
    def accept_fractal_aliases(cls, values):
        return _copy_fractal_aliases(values)


class CommandResponse(BaseModel):
    success: bool
    output: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str
    code: Literal["validation_error", "not_found", "runtime_error"] = "runtime_error"

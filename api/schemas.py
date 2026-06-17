"""Pydantic contracts for the local alpha API surface."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_MODALITIES = {"audio", "video", "text", "stimuli", "hearing", "vision", "language", "stimulus"}
MAX_EVENTS = 1000
MAX_LABEL_LENGTH = 120


def _finite(value: float, field_name: str) -> float:
    if not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")
    return float(value)


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

    def to_runtime_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "label": self.label,
            "epochs": self.epochs,
            "state_basis": self.state_basis,
        }
        if self.puncture_delta is not None:
            payload["puncture_delta"] = self.puncture_delta
        if self.memories is not None:
            payload["memories"] = [item.model_dump(exclude_none=True) for item in self.memories]
        if self.events is not None:
            payload["events"] = [item.model_dump(exclude_none=True) for item in self.events]
        if self.observations is not None:
            payload["observations"] = [item.model_dump(exclude_none=True) for item in self.observations]
        if self.statefield is not None:
            payload["statefield"] = self.statefield
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

    @model_validator(mode="before")
    @classmethod
    def accept_df_alias(cls, values):
        if isinstance(values, dict) and "dF" in values and "delta_falsity" not in values:
            values = dict(values)
            values["delta_falsity"] = values.pop("dF")
        return values

    @field_validator("truth", "indeterminacy", "falsity", "delta_falsity")
    @classmethod
    def validate_neurobit_numbers(cls, value: float, info):
        return _finite(value, info.field_name)

    def to_profile_payload(self) -> Dict[str, Any]:
        return {
            "truth": self.truth,
            "indeterminacy": self.indeterminacy,
            "falsity": self.falsity,
            "delta_falsity": self.delta_falsity,
            "state_basis": self.state_basis,
            "puncture_delta": self.puncture_delta,
        }


class NeuroBitTunnelRequest(NeuroBitProfileRequest):
    data: str = Field(default="neurobit-demo", max_length=4096)


class CommandRequest(BaseModel):
    payload: Optional[RuntimeRunRequest] = None
    observations: Optional[List[Observation]] = None
    samples: Optional[List[List[Observation]]] = None
    labels: Optional[List[int]] = None
    epochs: int = Field(default=24, ge=0, le=256)
    test_size: float = Field(default=0.25, ge=0.0, le=0.9)
    neurobit: Optional[NeuroBitTunnelRequest] = None


class CommandResponse(BaseModel):
    success: bool
    output: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str
    code: Literal["validation_error", "not_found", "runtime_error"] = "runtime_error"

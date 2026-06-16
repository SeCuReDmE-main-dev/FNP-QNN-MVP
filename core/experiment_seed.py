"""Deterministic experiment seed manager for reproducible local demos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


PHI = (1.0 + 5.0**0.5) / 2.0


@dataclass
class ExperimentSeedManager:
    """Small deterministic seed registry for MVP experiment provenance."""

    base_seed: int = 42
    current_seed: int = 42
    experiments: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.base_seed = self._coerce_seed(self.base_seed)
        self.current_seed = self._coerce_seed(self.current_seed)

    def set_seed(self, seed: int) -> int:
        self.current_seed = self._coerce_seed(seed)
        return self.current_seed

    def get_seed(self) -> int:
        return self.current_seed

    def get_next_seed(self) -> int:
        next_seed = int((self.current_seed * PHI + self.base_seed) % (2**31 - 1))
        if next_seed <= 0:
            next_seed = self.base_seed or 1
        self.current_seed = next_seed
        return self.current_seed

    def register_experiment(self, name: str, seed: Optional[int] = None) -> int:
        if not str(name).strip():
            raise ValueError("experiment name must be non-empty")
        experiment_seed = self._coerce_seed(seed if seed is not None else self.get_next_seed())
        self.experiments[str(name)] = experiment_seed
        return experiment_seed

    def get_experiment_seed(self, name: str) -> int:
        if name not in self.experiments:
            raise KeyError(f"unknown experiment: {name}")
        return self.experiments[name]

    def get_state_summary(self) -> Dict[str, object]:
        return {
            "base_seed": self.base_seed,
            "current_seed": self.current_seed,
            "experiment_count": len(self.experiments),
            "experiments": dict(sorted(self.experiments.items())),
            "policy": "deterministic-local-research",
        }

    def _coerce_seed(self, seed: int) -> int:
        value = int(seed)
        if value < 0:
            raise ValueError("seed must be non-negative")
        return value

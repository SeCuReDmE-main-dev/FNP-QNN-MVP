"""
Dormant life-science observation port.

This module intentionally has no dependency on R or FFED-RNASeq. It only
accepts StateField-shaped payloads so later FFED/LVFM outputs can be converted
into simulator observations through an explicit opt-in path.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

import numpy as np


class LifeScienceObservationPort:
    """Convert lattice-valued state payloads into simulator observations."""

    def statefield_to_observations(
        self,
        state: Mapping[str, Any],
        modality: str = "stimuli",
        source: str = "life-science-port",
    ) -> List[Dict[str, Any]]:
        mu = self._as_vector(state.get("mu", []))
        nu = self._as_vector(state.get("nu", []))
        pi_provided = state.get("pi")
        pi = self._as_vector(pi_provided) if pi_provided is not None else None
        n = max(len(mu), len(nu), len(pi) if pi is not None else 0)
        if n == 0:
            return []
        mu = self._resize(mu, n)
        nu = self._resize(nu, n)
        pi = self._resize(pi, n) if pi is not None else np.maximum(0.0, 1.0 - mu - nu)

        observations: List[Dict[str, Any]] = []
        for index in range(n):
            value = float(np.clip(mu[index] * (1.0 - nu[index]) + 0.5 * pi[index], 0.0, 1.0))
            observations.append(
                {
                    "modality": modality,
                    "value": value,
                    "timestamp": float(index),
                    "ending_time": float(index + 1),
                    "label": str(state.get("label") or "statefield"),
                    "source": source,
                    "payload_ref": f"statefield-{index}",
                    "provenance": state.get("provenance", {}),
                }
            )
        return observations

    def _as_vector(self, value: Any) -> np.ndarray:
        if value is None:
            return np.asarray([], dtype=float)
        if isinstance(value, np.ndarray):
            return value.astype(float).reshape(-1)
        if isinstance(value, (int, float, np.floating, np.integer)):
            return np.asarray([float(value)], dtype=float)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return np.asarray(list(value), dtype=float)
        return np.asarray([], dtype=float)

    def _resize(self, values: np.ndarray, size: int) -> np.ndarray:
        if len(values) == size:
            return values
        if len(values) == 0:
            return np.zeros(size, dtype=float)
        if len(values) == 1:
            return np.repeat(values, size)
        return np.resize(values, size)

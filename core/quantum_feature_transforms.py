"""Pure amplitude/phase feature transforms for the FNP-QNN MVP."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def complex_wavefunction_to_amplitude_phase_features(wavefunction: Iterable[complex]) -> np.ndarray:
    """Convert a complex wavefunction into `[amplitudes, phases]` features."""
    values = np.asarray(list(wavefunction), dtype=complex).reshape(-1)
    if values.size == 0:
        return np.zeros(0, dtype=np.float32)
    amplitudes = np.abs(values)
    phases = np.angle(values)
    return np.concatenate([amplitudes, phases]).astype(np.float32)


def structure_vector_to_phi_scaled_state(vector: Iterable[float], phi: float = (1.0 + 5.0**0.5) / 2.0) -> np.ndarray:
    """Map a real structure vector to a normalized phi-scaled complex state."""
    values = np.asarray(list(vector), dtype=np.float32).reshape(-1)
    if values.size == 0:
        return np.zeros(0, dtype=complex)

    indexes = np.arange(values.size, dtype=np.float32)
    amplitudes = values * np.power(float(phi), indexes / max(values.size, 1))
    phases = np.exp(1j * np.pi * values)
    state = amplitudes.astype(complex) * phases
    norm = np.linalg.norm(state)
    if norm <= 0.0:
        return np.zeros(values.size, dtype=complex)
    return state / norm

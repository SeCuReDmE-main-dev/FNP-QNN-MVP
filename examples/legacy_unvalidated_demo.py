"""Legacy synthetic demo retained for local research only.

This script does not demonstrate clinical, diagnostic, therapeutic, or safety
performance. It only exercises the phi-framework simulation primitives.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.phi_framework import PhiFramework


def run_demo() -> None:
    phi_engine = PhiFramework()
    print("FNP-QNN legacy synthetic research demo")
    print("Mode: local, non-clinical, unvalidated")

    phi_engine.generate_quantum_particles(50)
    region_map = phi_engine.map_brain_region("synthetic_region", (12, 10, 8))
    synthetic_scan = np.linspace(0.0, 1.0, num=12 * 10 * 8).reshape(12, 10, 8)
    target = phi_engine.calculate_neuronal_deficit_colocation(synthetic_scan, "synthetic_region")
    profile = phi_engine.generate_response_profile(target, "legacy-synthetic-scenario")
    progression = phi_engine.simulate_response_progression(profile, 24)

    print(f"Region map shape: {region_map.shape}")
    print(f"Synthetic target coordinate: {target}")
    print(f"Response profile keys: {sorted(profile.keys())}")
    print(f"Final bounded response: {progression[-1]:.6f}")


if __name__ == "__main__":
    run_demo()

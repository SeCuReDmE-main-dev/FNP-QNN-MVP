"""CLI demo for the lightweight NeuroBit gate lane."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.neurobit_gates import (
    NeutrosophicGateProfile,
    build_gate_parameters,
    build_neutrosophic_gate_sequence,
    run_neurobit_gates,
    to_torchquantum_ops,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a deterministic NeuroBit gate demo.")
    parser.add_argument("--truth", type=float, default=0.55)
    parser.add_argument("--indeterminacy", type=float, default=0.30)
    parser.add_argument("--falsity", type=float, default=0.15)
    parser.add_argument("--dF", dest="delta_falsity", type=float, default=0.0)
    args = parser.parse_args()

    profile = NeutrosophicGateProfile(
        truth=args.truth,
        indeterminacy=args.indeterminacy,
        falsity=args.falsity,
        delta_falsity=args.delta_falsity,
    )
    normalized = profile.normalized()
    result = run_neurobit_gates(normalized)
    payload = {
        "boundary": "alpha-local non-clinical research demo; not security, clinical, or quantum-advantage proof",
        "normalized_profile": normalized.metadata,
        "gate_sequence": build_neutrosophic_gate_sequence(normalized),
        "gate_parameters": build_gate_parameters(normalized),
        "backend": result["backend"],
        "qiskit_available": result["qiskit_available"],
        "backend_neutral_ops": to_torchquantum_ops(normalized, [0, 1, 2, 3]),
        "expectation_vector": result["expectation_vector"],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

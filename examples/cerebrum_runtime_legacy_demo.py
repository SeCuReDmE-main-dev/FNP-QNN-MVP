"""Run the Cerebrum runtime bridge from a legacy-style snapshot."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CerebrumRuntimeBridge, QNNNucleus


def main() -> None:
    legacy_root = Path(__file__).resolve().parent
    bridge = CerebrumRuntimeBridge(legacy_cerebrum_path=str(legacy_root))
    nucleus = QNNNucleus(adapter=bridge.adapter)
    state = bridge.build_state(None, qnn_nucleus=nucleus, max_epochs=6)
    payload = state.to_dict()
    print(
        json.dumps(
            {
                "legacy_cerebrum_path_exists": bridge.status(qnn_nucleus=nucleus)["legacy_cerebrum_path_exists"],
                "events": len(payload["events"]),
                "pairs": len(payload["pairs"]),
                "feature_dimension": payload["feature_dimension"],
                "qnn_backend": payload["qnn_result"]["backend"] if payload["qnn_result"] else "not-run",
                "warnings": payload["warnings"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

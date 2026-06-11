"""Run the Cerebrum runtime bridge without starting the API server."""

from __future__ import annotations

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CerebrumRuntimeBridge, QNNNucleus


def main() -> None:
    bridge = CerebrumRuntimeBridge()
    nucleus = QNNNucleus(adapter=bridge.adapter)
    state = bridge.build_state(bridge.default_payload(), qnn_nucleus=nucleus, max_epochs=6)
    payload = state.to_dict()
    print(
        json.dumps(
            {
                "events": len(payload["events"]),
                "pairs": len(payload["pairs"]),
                "feature_dimension": payload["feature_dimension"],
                "bundle_summary": payload["bundle"]["summary"],
                "qnn_backend": payload["qnn_result"]["backend"] if payload["qnn_result"] else "not-run",
                "warnings": payload["warnings"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

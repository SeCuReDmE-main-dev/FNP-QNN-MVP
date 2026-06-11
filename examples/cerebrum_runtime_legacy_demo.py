"""Run the Cerebrum runtime bridge from a legacy-style snapshot."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import CerebrumRuntimeBridge, QNNNucleus


def _write_legacy_snapshot(directory: Path) -> Path:
    snapshot = directory / "legacy_cerebrum_snapshot.json"
    snapshot.write_text(
        json.dumps(
            {
                "hearing_timestamps": [
                    {"starting_time": 0.0, "ending_time": 1.2, "data": 0.71, "label": "rhythm", "source": "legacy"},
                ],
                "vision_timestamps": [
                    {"starting_time": 0.3, "ending_time": 1.5, "data": 0.49, "label": "motion", "source": "legacy"},
                ],
                "language_timestamps": [
                    {"starting_time": 0.8, "ending_time": 1.8, "data": 0.62, "label": "caption", "source": "legacy"},
                ],
                "crossmodal_mappings": [
                    {"timestamp1": 0.0, "timestamp2": 0.3, "direction": "H2V", "overlap_score": 0.75},
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return snapshot


def main() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        legacy_root = Path(tmpdir)
        _write_legacy_snapshot(legacy_root)
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

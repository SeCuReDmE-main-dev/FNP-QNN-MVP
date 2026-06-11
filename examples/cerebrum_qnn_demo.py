#!/usr/bin/env python3
"""Smoke demo for the Cerebrum -> QNN pipeline."""

from __future__ import annotations

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core import CerebrumAdapter, QNNNucleus


def main() -> None:
    adapter = CerebrumAdapter()
    nucleus = QNNNucleus(adapter=adapter)

    samples, labels = [
        adapter.default_observations(),
        [
            {"modality": "audio", "value": 0.19, "timestamp": 0.0, "label": "voice", "source": "demo"},
            {"modality": "video", "value": 0.79, "timestamp": 0.7, "label": "motion", "source": "demo"},
            {"modality": "text", "value": 0.66, "timestamp": 1.3, "label": "caption", "source": "demo"},
            {"modality": "stimuli", "value": 0.44, "timestamp": 2.0, "label": "prompt", "source": "demo"},
        ],
        [
            {"modality": "audio", "value": 0.87, "timestamp": 0.0, "label": "rhythm", "source": "demo"},
            {"modality": "video", "value": 0.31, "timestamp": 0.8, "label": "flash", "source": "demo"},
            {"modality": "text", "value": 0.51, "timestamp": 1.5, "label": "token", "source": "demo"},
            {"modality": "stimuli", "value": 0.93, "timestamp": 2.4, "label": "trigger", "source": "demo"},
        ],
    ], [0, 1, 1]

    bundle = adapter.build_bundle(samples[0])
    vector = adapter.bundle_to_vector(bundle)

    print("Cerebrum summary")
    print(bundle.summary)
    print(f"Feature dimension: {vector.shape[0]}")
    print(f"Candidate matrix: {[candidate.name for candidate in nucleus.candidate_matrix()]}")
    result = nucleus.fit_surrogate(samples, labels, max_epochs=16, test_size=0.25)
    print("QNN result")
    print(result)


if __name__ == "__main__":
    main()

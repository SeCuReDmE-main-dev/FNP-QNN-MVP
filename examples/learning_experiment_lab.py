"""Age-14+ guided learning lab for the FNP-QNN simulator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.education_labs import build_learning_pack, validate_learner_age


def _build_markdown(pack: dict) -> str:
    lines = [
        "# FNP-QNN Guided Learning Lab",
        "",
        f"Age policy: {pack['learner_policy']['status']} (minimum {pack['learner_policy']['min_age']})",
        "",
        "## Learning boundary",
        "\n".join(f"- {line}" for line in pack["boundary"]),
        "",
        "## Activities",
    ]
    for item in pack["activities"]:
        lines.extend(
            [
                f"### {item['title']}",
                f"- Concept: {item['concept']}",
                f"- Question: {item['question']}",
                f"- Expected discovery: {item['expected_discovery']}",
                "- Steps:",
            ]
        )
        for step in item["steps"]:
            lines.append(f"  - {step}")
        observation = item["expected_to_observe"]
        lines.extend(
            [
                f"- Key observation: {observation['observation']['summary']}",
                f"- Backend: {observation['backend']} (qiskit_available={observation['qiskit_available']})",
            ]
        )
        if "tunnel_preview" in item:
            lines.extend(
                [
                    "- Tunnel preview:",
                    f"  - sequence_id={item['tunnel_preview']['sequence_id']}",
                    f"  - boundary={item['tunnel_preview']['research_boundary']}",
                ]
            )
    lines.extend(["", "## Suggested next steps", ""])
    lines.extend([f"- {step}" for step in pack["next_steps"]])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a bounded educational activity pack for learners age 14+.")
    parser.add_argument("--age", type=int, default=14, help="Participant age in years.")
    parser.add_argument(
        "--with-tunnel-preview",
        action="store_true",
        help="Include deterministic tunnel fingerprint preview in each activity output.",
    )
    parser.add_argument("--markdown", action="store_true", help="Print markdown view instead of JSON.")
    args = parser.parse_args()

    validate_learner_age(args.age)
    pack = build_learning_pack(age_years=args.age, include_tunnel_demo=args.with_tunnel_preview)
    if args.markdown:
        print(_build_markdown(pack))
    else:
        print(json.dumps(pack, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

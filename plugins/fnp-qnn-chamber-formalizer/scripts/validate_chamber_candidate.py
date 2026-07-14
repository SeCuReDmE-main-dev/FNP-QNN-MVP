"""Validate only the structural ten-carrier handoff before Synthia admission."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED = ("I_source", "I_flavor", "I_mass", "I_mix", "I_phase", "I_medium", "I_interaction", "I_secondary", "I_detector", "I_uncertainty")


def main(path: str) -> int:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    carriers = payload.get("carriers", []) if isinstance(payload, dict) else []
    names = [item.get("name") for item in carriers if isinstance(item, dict)]
    valid = len(names) == 10 and set(names) == set(REQUIRED)
    print(json.dumps({"valid_structure": valid, "carrier_order": list(REQUIRED), "next_authority": "Synthia"}))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))

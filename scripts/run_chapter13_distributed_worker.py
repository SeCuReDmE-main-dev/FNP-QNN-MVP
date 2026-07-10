"""Lightweight chapter-13 worker entrypoint for disposable Linux sandboxes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import types


ROOT = Path(__file__).resolve().parents[1]


def _load_worker():
    # Avoid importing core/__init__.py, which intentionally exposes optional
    # Torch/API study layers not needed by the chapter-13 worker.
    package = types.ModuleType("core")
    package.__path__ = [str(ROOT / "core")]
    package.__package__ = "core"
    sys.modules["core"] = package
    from core.neutrino_chapter13_distributed_validation import neutrino_chapter13_distributed_worker_from_file

    return neutrino_chapter13_distributed_worker_from_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--pluginpack-path", required=True)
    args = parser.parse_args(argv)
    worker = _load_worker()
    result = worker(args.input, pluginpack_path=args.pluginpack_path)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Bootstrap loop for persisting LVFM gate state on Windows-first laptops."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import request
from urllib.parse import urlencode

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from core.lvfm_registry_anchor import compute_lock_state

DEFAULT_API_BASE = "http://127.0.0.1:8000"


@dataclass(frozen=True)
class BootstrapResult:
    gate_id: str
    verdict: str
    locked: bool
    lock_reason: str
    registry_published: bool
    source_path: str


def _post_gate_run(api_base: str, payload: Dict[str, Any], publish_to_registry: bool, registry_threshold: float) -> Dict[str, Any]:
    query = urlencode(
        {
            "publish_to_registry": "true" if publish_to_registry else "false",
            "registry_threshold": f"{registry_threshold}",
        }
    )
    url = f"{api_base.rstrip('/')}/cerebrum/runtime/gate-run?{query}"
    req = request.Request(url, method="POST")
    req.add_header("content-type", "application/json")
    with request.urlopen(req, data=json.dumps(payload).encode("utf-8"), timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _read_payload(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {"run_qnn": False, "epochs": 4}
    payload_text = Path(path).read_text(encoding="utf-8").strip()
    if not payload_text:
        return {}
    return json.loads(payload_text)


def bootstrap_once(
    api_base: str = DEFAULT_API_BASE,
    payload_path: Optional[str] = None,
    publish_to_registry: bool = False,
    registry_threshold: float = -0.1,
    output_path: Optional[str] = None,
) -> BootstrapResult:
    launcher_path = str(Path(__file__).resolve())
    payload = _read_payload(payload_path)
    response = _post_gate_run(api_base, payload, publish_to_registry=publish_to_registry, registry_threshold=registry_threshold)

    if response.get("status") != "ok":
        raise RuntimeError(f"Unexpected gate-run status: {response.get('status')}")

    gate = response["gate"]
    decision = gate.get("decision", {})
    registry_state = response.get("registry")
    if isinstance(registry_state, dict) and registry_state:
        lock_state = {
            "locked": bool(registry_state.get("locked")),
            "lock_reason": str(registry_state.get("lock_reason", "")),
            "score": float(registry_state.get("score", 0.0)),
        }
    else:
        lock_state = compute_lock_state(decision, threshold=registry_threshold)
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(response, indent=2), encoding="utf-8")

    gate_snapshot = gate.get("decision", {})
    trace = gate_snapshot.get("trace_line", "")
    register_keys = len(gate.get("snapshot", {}).get("register_keys", {}))
    print(
        f"[SeCuReDmE LVFM] launcher={launcher_path}"
    )
    print(
        f"[SeCuReDmE LVFM] api={api_base} payload_path={payload_path or '<default-demo>'} registry={publish_to_registry} "
        f"threshold={registry_threshold}"
    )
    if output_path:
        print(f"[SeCuReDmE LVFM] output={output_path}")
    print(f"[SeCuReDmE LVFM] gate_id={gate.get('gate_id', '')}")
    print(f"[SeCuReDmE LVFM] trace={trace}")
    print(f"[SeCuReDmE LVFM] register_keys={register_keys}")
    print(f"[SeCuReDmE LVFM] source_path={gate.get('source_path', '')}")
    if isinstance(registry_state, dict) and registry_state:
        print(f"[SeCuReDmE LVFM] history_event_id={registry_state.get('history_event_id', '')}")
        print(f"[SeCuReDmE LVFM] history_path={registry_state.get('history_path', '')}")

    if output_path:
        log_payload = [
            f"launcher_path={launcher_path}",
            f"api_base={api_base}",
            f"payload_path={payload_path or '<default-demo>'}",
            f"publish_to_registry={publish_to_registry}",
            f"registry_threshold={registry_threshold}",
            f"output_path={output_path}",
            f"gate_id={gate.get('gate_id', '')}",
            f"verdict={decision.get('verdict', '')}",
            f"trace_line={trace}",
            f"register_keys={register_keys}",
            f"source_path={gate.get('source_path', '')}",
        ]
        if isinstance(registry_state, dict) and registry_state:
            log_payload.extend(
                [
                    f"history_event_id={registry_state.get('history_event_id', '')}",
                    f"history_path={registry_state.get('history_path', '')}",
                    f"history_written_at={registry_state.get('history_written_at', '')}",
                    f"schema_version={registry_state.get('schema_version', '')}",
                ]
            )
        with output_file.open("a", encoding="utf-8") as handle:
            handle.write("\n----- LVFM BOOT SNAPSHOT -----\n")
            for line in log_payload:
                handle.write(f"{line}\n")

    return BootstrapResult(
        gate_id=gate.get("gate_id", ""),
        verdict=str(decision.get("verdict", "")),
        locked=bool(lock_state["locked"]),
        lock_reason=str(lock_state["lock_reason"]),
        registry_published=bool(registry_state.get("published")) if isinstance(registry_state, dict) else False,
        source_path=str(gate.get("source_path", "")),
    )


def bootstrap_loop(
    api_base: str,
    payload_path: Optional[str],
    interval_seconds: int,
    publish_to_registry: bool,
    registry_threshold: float,
    output_path: Optional[str],
) -> None:
    while True:
        if output_path:
            output_path = str(output_path)
        result = bootstrap_once(
            api_base=api_base,
            payload_path=payload_path,
            publish_to_registry=publish_to_registry,
            registry_threshold=registry_threshold,
            output_path=output_path,
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "gate_id": result.gate_id,
                    "verdict": result.verdict,
                    "locked": result.locked,
                    "lock_reason": result.lock_reason,
                    "registry_published": result.registry_published,
                    "source_path": result.source_path,
                }
            )
        )
        if interval_seconds <= 0:
            break
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="LVFM gate bootstrap for local Windows integration")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="Base URL for local simulator API.")
    parser.add_argument("--payload-path", default=None, help="Optional JSON payload for runtime gate input.")
    parser.add_argument("--interval-seconds", type=int, default=0, help="Poll interval in seconds; 0 = one-shot.")
    parser.add_argument(
        "--publish-registry",
        action="store_true",
        help="Persist gate decision in HKCU\\Software\\SeCuReDmE\\LVFM",
    )
    parser.add_argument("--registry-threshold", type=float, default=-0.1, help="Confidence threshold for lock.")
    parser.add_argument("--output-path", default=None, help="Optional path to write last gate response JSON.")
    parser.add_argument("--run-once", action="store_true", help="Run once even if interval is positive.")
    args = parser.parse_args()

    # keep compatibility: if --run-once is explicit, no loop despite interval
    interval = 0 if args.run_once else max(0, args.interval_seconds)

    bootstrap_loop(
        api_base=args.api_base,
        payload_path=args.payload_path,
        interval_seconds=interval,
        publish_to_registry=args.publish_registry,
        registry_threshold=args.registry_threshold,
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()

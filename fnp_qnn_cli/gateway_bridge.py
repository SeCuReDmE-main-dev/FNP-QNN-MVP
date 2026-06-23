"""Simulator-side bridge into the optional fnpqnn gateway package."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any


def _gateway_candidate_paths() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    candidates: list[Path] = []
    env_path = os.environ.get("FNPQNN_GATEWAY_MVP_PATH")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.append(repo_root.parent / "fnpqnn_gateway_MVP")
    return candidates


def _load_deepsearch_functions() -> tuple[Any, Any] | tuple[None, None]:
    try:
        from fnpqnn_gateway_mvp.deepsearch_skill import build_deepsearch_skill, write_deepsearch_skill

        return build_deepsearch_skill, write_deepsearch_skill
    except ModuleNotFoundError:
        pass

    for candidate in _gateway_candidate_paths():
        if candidate.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
            try:
                from fnpqnn_gateway_mvp.deepsearch_skill import build_deepsearch_skill, write_deepsearch_skill

                return build_deepsearch_skill, write_deepsearch_skill
            except ModuleNotFoundError:
                continue
    return None, None


def gateway_deepsearch_skill(
    *,
    query: str,
    research_goal: str | None = None,
    workspace: str | Path = ".",
    system: str | None = None,
    last_auth: bool = False,
    fingerprint: str | None = None,
    write: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    build_deepsearch_skill, write_deepsearch_skill = _load_deepsearch_functions()
    if build_deepsearch_skill is None or write_deepsearch_skill is None:
        return {
            "success": False,
            "type": "gateway-deepsearch-skill",
            "error": "fnpqnn_gateway_mvp is not importable",
            "next_step": (
                "Install the gateway with pip install -e ../fnpqnn_gateway_MVP, "
                "or set FNPQNN_GATEWAY_MVP_PATH to the gateway repo."
            ),
            "raw_secret_stored": False,
        }

    payload = build_deepsearch_skill(
        query=query,
        research_goal=research_goal,
        workspace=workspace,
        system=system,
        last_auth=last_auth,
        fingerprint=fingerprint,
    )
    if write:
        payload = write_deepsearch_skill(payload, force=force)
    payload["simulator_gateway_block"] = {
        "entrypoint": "fnp-qnn",
        "delegated_to": "fnpqnn_gateway_mvp.deepsearch_skill",
        "simulator_role": "user-facing CLI and LVFM/RAG consumer",
        "gateway_role": "authlog/provider routing and deepsearch contract writer",
        "raw_secret_stored": False,
    }
    return payload

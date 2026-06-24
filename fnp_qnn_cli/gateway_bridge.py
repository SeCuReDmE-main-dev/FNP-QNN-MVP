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
    return _fallback_build_deepsearch_skill, _fallback_write_deepsearch_skill


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


def _fallback_build_deepsearch_skill(
    *,
    query: str,
    research_goal: str | None = None,
    workspace: str | Path = ".",
    system: str | None = None,
    last_auth: bool = False,
    fingerprint: str | None = None,
) -> dict[str, Any]:
    selected = str(system or "antigravity").strip().lower()
    route = _fallback_route(selected)
    slug = _slug(query)
    base = Path(workspace).expanduser().resolve() / ".fnpqnn_gateway" / "deepsearch"
    return {
        "success": True,
        "type": "gateway-deepsearch-skill",
        "query": query,
        "research_goal": research_goal or query,
        "authlog_source": "simulator-local-fallback",
        "last_auth_requested": bool(last_auth),
        "fingerprint_present": bool(fingerprint),
        "search_route": route,
        "paths": {
            "contract_json": str(base / f"{slug}.json"),
            "contract_markdown": str(base / f"{slug}.md"),
        },
        "policy": {
            "no_generic_scraper_first": True,
            "no_secret_storage": True,
            "raw_secret_stored": False,
        },
        "dry_run": True,
        "raw_secret_stored": False,
    }


def _fallback_write_deepsearch_skill(payload: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    if not payload.get("success"):
        return payload
    written: list[str] = []
    skipped: list[str] = []
    for key, content in (
        ("contract_json", json_dumps({**payload, "dry_run": False})),
        ("contract_markdown", _fallback_markdown(payload)),
    ):
        path = Path(payload["paths"][key])
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            skipped.append(str(path))
            continue
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    return {**payload, "dry_run": False, "written": written, "skipped_existing": skipped}


def _fallback_route(system: str) -> dict[str, Any]:
    if system in {"ollama", "ollama-cloud"}:
        return {
            "route": "ollama-cloud-web-search",
            "provider": "ollama",
            "system": "ollama-cloud",
            "fallback_used": False,
            "provider_native_available": True,
        }
    return {
        "route": "antigravity-gemini-google-search",
        "provider": "google",
        "system": "antigravity",
        "fallback_used": system not in {"google", "antigravity"},
        "provider_native_available": system in {"google", "antigravity"},
    }


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return f"deepsearch-{cleaned or 'query'}"[:63].rstrip("-")


def json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, indent=2, sort_keys=True)


def _fallback_markdown(payload: dict[str, Any]) -> str:
    route = payload["search_route"]
    return (
        f"# Deepsearch Skill: {payload['query']}\n\n"
        f"- search_route: {route['route']}\n"
        f"- fallback_used: {route['fallback_used']}\n"
        f"- raw_secret_stored: {payload['raw_secret_stored']}\n"
    )

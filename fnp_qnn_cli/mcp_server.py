"""Minimal stdio MCP server for FNP-QNN simulator control."""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from .agent_profiles import agent_profile, wake_prompt
from .mcp_bridge import mcp_control_simulator, mcp_manifest, provider_connection_status, simulator_control_tasks
from .onboarding import apply_onboarding, onboarding_questions


def _tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "name": "fnp_qnn_provider_status",
            "description": "Check OpenAI/ChatGPT, Google/Gemini, or Ollama Cloud connection status for simulator control.",
            "inputSchema": {
                "type": "object",
                "properties": {"provider": {"type": "string", "enum": ["openai", "chatgpt", "google", "gemini", "ollama"]}},
                "required": ["provider"],
            },
        },
        {
            "name": "fnp_qnn_control_simulator",
            "description": "Control an allowlisted simulator task through Codex, Antigravity, or Ollama.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["openai", "chatgpt", "google", "gemini", "ollama"]},
                    "task": {
                        "type": "string",
                        "enum": ["status", "doctor", "runtime", "qnn", "neurobit", "validate", "external-status"],
                    },
                    "execute": {"type": "boolean", "default": False},
                    "timeout": {"type": "integer", "default": 300},
                    "prompt": {"type": "string"},
                },
                "required": ["provider", "task"],
            },
        },
        {
            "name": "fnp_qnn_control_tasks",
            "description": "List allowlisted simulator control tasks.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "fnp_qnn_onboarding_questions",
            "description": "List the directed onboarding questions used to shape simulator context.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "fnp_qnn_onboard_user",
            "description": "Apply provider-approved onboarding answers into simulator context files.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["openai", "chatgpt", "google", "gemini", "ollama"]},
                    "approve_fingerprint": {"type": "boolean"},
                    "answers": {"type": "object"},
                    "delegate": {"type": "boolean", "default": False},
                    "execute_delegate": {"type": "boolean", "default": False},
                },
                "required": ["provider", "approve_fingerprint"],
            },
        },
        {
            "name": "fnp_qnn_agent_profile",
            "description": "Return the native-system profile for Codex, Antigravity/Gemini, or Ollama/OpenClaw.",
            "inputSchema": {
                "type": "object",
                "properties": {"provider": {"type": "string", "enum": ["openai", "chatgpt", "google", "gemini", "ollama"]}},
                "required": ["provider"],
            },
        },
        {
            "name": "fnp_qnn_wake_prompt",
            "description": "Return the provider-specific wake prompt that explains FNP-QNN and the active interface.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "provider": {"type": "string", "enum": ["openai", "chatgpt", "google", "gemini", "ollama"]},
                    "answers": {"type": "object"},
                },
                "required": ["provider"],
            },
        },
    ]


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    args = arguments or {}
    if name == "fnp_qnn_provider_status":
        return provider_connection_status(str(args["provider"]))
    if name == "fnp_qnn_control_simulator":
        return mcp_control_simulator(
            str(args["provider"]),
            str(args["task"]),
            execute=bool(args.get("execute", False)),
            timeout=int(args.get("timeout", 300)),
            prompt=args.get("prompt"),
        )
    if name == "fnp_qnn_control_tasks":
        return {"success": True, "tasks": simulator_control_tasks()}
    if name == "fnp_qnn_onboard_user":
        return apply_onboarding(
            str(args["provider"]),
            approve_fingerprint=bool(args.get("approve_fingerprint", False)),
            overrides=args.get("answers") or {},
            delegate=bool(args.get("delegate", False)),
            execute_delegate=bool(args.get("execute_delegate", False)),
        )
    if name == "fnp_qnn_onboarding_questions":
        return onboarding_questions()
    if name == "fnp_qnn_agent_profile":
        return {"success": True, "profile": agent_profile(str(args["provider"]))}
    if name == "fnp_qnn_wake_prompt":
        return {
            "success": True,
            "provider": str(args["provider"]),
            "wake_prompt": wake_prompt(str(args["provider"]), args.get("answers") or {}),
        }
    raise ValueError(f"unknown MCP tool: {name}")


def handle_request(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")
    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fnp-qnn-ai-control-mcp", "version": "0.1.0"},
            }
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            result = {"tools": _tool_schema()}
        elif method == "tools/call":
            params = request.get("params") or {}
            payload = call_tool(str(params.get("name")), params.get("arguments") or {})
            result = {"content": [{"type": "text", "text": json.dumps(payload, indent=2, sort_keys=True)}]}
        elif method == "fnp-qnn/manifest":
            result = mcp_manifest()
        else:
            raise ValueError(f"unsupported method: {method}")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": f"{type(exc).__name__}: {exc}"},
        }


def _read_message(stdin: TextIO) -> dict[str, Any] | None:
    header = stdin.readline()
    if not header:
        return None
    if header.startswith("{"):
        return json.loads(header)
    content_length = None
    while header and header.strip():
        key, _, value = header.partition(":")
        if key.lower() == "content-length":
            content_length = int(value.strip())
        header = stdin.readline()
    if content_length is None:
        return None
    body = stdin.read(content_length)
    return json.loads(body)


def _write_message(stdout: TextIO, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, separators=(",", ":"))
    stdout.write(f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n{body}")
    stdout.flush()


def serve(stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> int:
    while True:
        request = _read_message(stdin)
        if request is None:
            return 0
        response = handle_request(request)
        if response is not None:
            _write_message(stdout, response)


def main() -> int:
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())

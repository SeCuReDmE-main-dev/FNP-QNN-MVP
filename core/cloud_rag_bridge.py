"""Cloud-kit bridge for encrypted RAG admissions into the LVFM runtime.

This module keeps cloud execution outside the simulator core. E2B can normalize
or inspect external data, but only an explicit, sanitized admission is converted
into Cerebrum/LVFM memory events.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from importlib.util import find_spec
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence


RAG_KEY_ENV = "FNP_QNN_RAG_ENCRYPTION_KEY"
E2B_KEY_ENV = "E2B_API_KEY"
DEFAULT_OPENCLAW_ENV = Path.home() / ".openclaw" / "workspace" / ".env"
MAX_RAG_CONTENT_CHARS = 65536


@dataclass(frozen=True)
class CloudRAGAdmission:
    title: str
    content: str
    source: str
    tool_route: str = "gateway"
    tags: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        content = self.content[:MAX_RAG_CONTENT_CHARS]
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return {
            "kind": "fnpqnn-cloud-rag-admission",
            "title": self.title[:120],
            "content": content,
            "source": self.source[:240],
            "tool_route": self.tool_route[:80],
            "tags": list(self.tags),
            "content_sha256": digest,
            "created_at": _utc_now(),
            "boundary": {
                "external_data": "sanitized-summary-only",
                "cloud_execution": "optional-e2b-upstream",
                "lvfm_ownership": "simulator",
                "raw_secret_stored": False,
            },
        }


def cloud_kit_status() -> dict[str, Any]:
    """Return secret-safe readiness for E2B and encrypted RAG transport."""
    return {
        "status": "ok",
        "cloud_kit": "optional",
        "e2b": {
            "sdk_available": find_spec("e2b") is not None,
            "code_interpreter_available": find_spec("e2b_code_interpreter") is not None,
            "api_key_present": bool(os.environ.get(E2B_KEY_ENV)),
            "api_key_value_printed": False,
        },
        "rag_encryption": {
            "provider": "cryptography.fernet",
            "available": _fernet_class() is not None,
            "key_env": RAG_KEY_ENV,
            "key_present": bool(os.environ.get(RAG_KEY_ENV)),
            "raw_key_value_printed": False,
        },
        "pipeline": [
            "external source approved by user",
            "optional E2B sandbox normalization",
            "sanitized RAG admission",
            "optional encrypted RAG envelope",
            "Cerebrum event conversion",
            "LVFMRuntimeGraph ingestion owned by simulator",
        ],
}


def load_env_file(path: str | os.PathLike[str] | None = None, keys: Sequence[str] | None = None) -> dict[str, Any]:
    """Load selected environment variables from a dotenv-style file.

    This intentionally returns only key names and presence booleans. Values are
    placed into os.environ for the current process but never serialized.
    """
    env_path = Path(path).expanduser() if path else DEFAULT_OPENCLAW_ENV
    selected = set(keys or (E2B_KEY_ENV, RAG_KEY_ENV))
    loaded: list[str] = []
    if not env_path.exists():
        return {"success": False, "path": str(env_path), "loaded": loaded, "error": "env file not found"}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in selected:
            continue
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ[key] = value
            loaded.append(key)
    return {
        "success": True,
        "path": str(env_path),
        "loaded": sorted(set(loaded)),
        "presence": {key: bool(os.environ.get(key)) for key in selected},
        "raw_values_printed": False,
    }


def e2b_smoke(env_file: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Run a minimal real E2B sandbox smoke when E2B_API_KEY is available."""
    env_result = load_env_file(env_file, keys=(E2B_KEY_ENV,))
    if not os.environ.get(E2B_KEY_ENV):
        return {
            "success": False,
            "provider": "e2b",
            "env_load": env_result,
            "error": f"{E2B_KEY_ENV} is missing or empty",
            "raw_token_stored": False,
        }
    try:
        from e2b import Sandbox
    except Exception as exc:
        return {
            "success": False,
            "provider": "e2b",
            "env_load": env_result,
            "error": f"e2b package unavailable: {type(exc).__name__}: {exc}",
            "raw_token_stored": False,
        }
    try:
        with Sandbox.create() as sandbox:
            result = sandbox.commands.run("python - <<'PY'\nprint('fnpqnn-e2b-smoke-ok')\nPY")
            sandbox_id = getattr(sandbox, "sandbox_id", None)
        stdout = str(getattr(result, "stdout", ""))
        return {
            "success": "fnpqnn-e2b-smoke-ok" in stdout,
            "provider": "e2b",
            "sandbox_id": sandbox_id,
            "stdout_contains_expected_marker": "fnpqnn-e2b-smoke-ok" in stdout,
            "raw_token_stored": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "provider": "e2b",
            "env_load": env_result,
            "error": f"{type(exc).__name__}: {exc}",
            "raw_token_stored": False,
        }


def generate_rag_key() -> dict[str, Any]:
    Fernet = _require_fernet()
    key = Fernet.generate_key().decode("ascii")
    return {
        "success": True,
        "key_env": RAG_KEY_ENV,
        "key": key,
        "usage": f"Set {RAG_KEY_ENV} to this value before encrypt/decrypt operations.",
        "raw_key_stored": False,
    }


def e2b_ingest_plan(source: str, title: str, tool_route: str = "gateway") -> dict[str, Any]:
    """Describe the E2B-to-RAG-to-LVFM flow without launching a sandbox."""
    return {
        "success": True,
        "provider": "e2b",
        "source": source,
        "title": title,
        "tool_route": tool_route,
        "confirmed_source_behavior": {
            "sandbox": "E2B SDK starts isolated sandboxes for code/data work.",
            "code_interpreter": "e2b-code-interpreter can execute Python in a sandbox.",
            "api_key": f"Use {E2B_KEY_ENV}; do not serialize it into RAG or LVFM payloads.",
        },
        "plan": [
            "Fetch or upload the external data into an approved E2B sandbox.",
            "Run only deterministic normalization/inspection code needed for the admission.",
            "Export a sanitized summary, not raw secrets or unbounded files.",
            "Create a cloud RAG admission from that summary.",
            "Encrypt the RAG admission if it must cross a gateway boundary.",
            "Decrypt inside the approved simulator boundary and convert to Cerebrum events.",
        ],
        "suggested_cli": {
            "status": "python -m fnp_qnn_cli --json cloud-kit status",
            "keygen": "python -m fnp_qnn_cli --json cloud-kit rag-keygen",
            "encrypt": (
                "python -m fnp_qnn_cli --json cloud-kit rag-encrypt "
                f"--title \"{title}\" --source \"{source}\" --tool-route {tool_route} --content-file summary.md"
            ),
        },
        "writes_files": False,
        "raw_secret_stored": False,
    }


def build_admission(
    title: str,
    content: str,
    source: str,
    tool_route: str = "gateway",
    tags: Sequence[str] | None = None,
) -> dict[str, Any]:
    return CloudRAGAdmission(
        title=title,
        content=content,
        source=source,
        tool_route=tool_route,
        tags=tuple(tags or ()),
    ).to_payload()


def encrypt_admission(payload: Mapping[str, Any], key: str | None = None) -> dict[str, Any]:
    """Encrypt an admitted RAG payload with Fernet.

    The key is read from FNP_QNN_RAG_ENCRYPTION_KEY unless explicitly provided.
    The returned envelope contains ciphertext plus integrity metadata, never the
    raw key.
    """
    Fernet = _require_fernet()
    resolved_key = _resolve_key(key)
    encoded = json.dumps(dict(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    ciphertext = Fernet(resolved_key).encrypt(encoded).decode("ascii")
    return {
        "version": 1,
        "kind": "fnpqnn-encrypted-rag-envelope",
        "algorithm": "fernet",
        "key_env": RAG_KEY_ENV,
        "ciphertext": ciphertext,
        "plaintext_sha256": digest,
        "encrypted_at": _utc_now(),
        "raw_key_stored": False,
    }


def decrypt_admission(envelope: Mapping[str, Any], key: str | None = None) -> dict[str, Any]:
    Fernet = _require_fernet()
    if envelope.get("algorithm") != "fernet":
        raise ValueError("Unsupported encrypted RAG envelope algorithm")
    ciphertext = str(envelope.get("ciphertext") or "")
    if not ciphertext:
        raise ValueError("Encrypted RAG envelope is missing ciphertext")
    plaintext = Fernet(_resolve_key(key)).decrypt(ciphertext.encode("ascii"))
    expected = str(envelope.get("plaintext_sha256") or "")
    actual = hashlib.sha256(plaintext).hexdigest()
    if expected and expected != actual:
        raise ValueError("Encrypted RAG envelope integrity check failed")
    loaded = json.loads(plaintext.decode("utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("Encrypted RAG envelope did not contain an object payload")
    return loaded


def admission_to_runtime_payload(admission: Mapping[str, Any]) -> dict[str, Any]:
    content = str(admission.get("content") or "")
    title = str(admission.get("title") or "cloud-rag-admission")
    digest = str(admission.get("content_sha256") or hashlib.sha256(content.encode("utf-8")).hexdigest())
    value = min(1.0, max(0.0, len(content) / 4000.0))
    return {
        "memories": [
            {
                "modality": "text",
                "starting_time": 0.0,
                "ending_time": max(1.0, min(60.0, len(content) / 1000.0)),
                "value": value,
                "label": title[:120],
                "source": f"cloud-rag:{admission.get('tool_route', 'gateway')}",
                "payload_ref": digest[:32],
                "provenance": {
                    "bridge": "cloud-rag-to-lvfm",
                    "external_source": admission.get("source"),
                    "tags": admission.get("tags", []),
                    "content_sha256": digest,
                    "hierarchy": "I -> I_system^S -> D_f -> dF -> i_fractal",
                },
            }
        ],
        "plugin_context": {
            "cloud_rag": {
                "title": title,
                "source": admission.get("source"),
                "tool_route": admission.get("tool_route"),
                "content_sha256": digest,
            }
        },
    }


def envelope_to_runtime_payload(envelope: Mapping[str, Any], key: str | None = None) -> dict[str, Any]:
    return admission_to_runtime_payload(decrypt_admission(envelope, key=key))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fernet_class():
    try:
        from cryptography.fernet import Fernet
    except Exception:
        return None
    return Fernet


def _require_fernet():
    Fernet = _fernet_class()
    if Fernet is None:
        raise RuntimeError(
            "cryptography is required for RAG encryption. Install the local cloud kit requirements first."
        )
    return Fernet


def _resolve_key(key: str | None) -> bytes:
    raw_key = key or os.environ.get(RAG_KEY_ENV)
    if not raw_key:
        raise ValueError(f"{RAG_KEY_ENV} is required for encrypted RAG transport")
    try:
        base64.urlsafe_b64decode(raw_key.encode("ascii"))
    except Exception as exc:
        raise ValueError(f"{RAG_KEY_ENV} must be a Fernet base64 key") from exc
    return raw_key.encode("ascii")

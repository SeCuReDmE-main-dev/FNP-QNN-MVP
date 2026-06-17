"""Optional runtime state persistence with etcd v3 HTTP gateway fallback."""

from __future__ import annotations

import base64
import copy
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib import error as urllib_error
from urllib import request as urllib_request


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class RuntimeStateStore:
    """Persist latest simulator state in etcd when available, else in memory."""

    def __init__(
        self,
        mode: Optional[str] = None,
        endpoint: Optional[str] = None,
        prefix: Optional[str] = None,
        timeout: float = 2.0,
    ) -> None:
        self.mode = (mode or os.getenv("SIMULATOR_STATE_STORE", "auto")).strip().lower()
        self.endpoint = (endpoint or os.getenv("ETCD_ENDPOINT", "http://127.0.0.1:2379")).rstrip("/")
        self.prefix = (prefix or os.getenv("ETCD_PREFIX", "/fnp-qnn")).rstrip("/")
        self.timeout = float(timeout)
        self._memory: Dict[str, Dict[str, Any]] = {}
        self._last_backend = "memory"
        self._last_error: Optional[str] = None

    def put_json(self, key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "key": key,
            "stored_at": _utc_now_iso(),
            "payload": payload,
        }
        if self.mode != "memory":
            try:
                self._etcd_put(key, record)
                self._last_backend = "etcd"
                self._last_error = None
                return {"backend": "etcd", "stored": True, "key": self._qualified_key(key)}
            except Exception as exc:
                self._last_error = str(exc)
                if self.mode == "etcd":
                    raise
        self._memory[key] = copy.deepcopy(record)
        self._last_backend = "memory"
        return {"backend": "memory", "stored": True, "key": self._qualified_key(key), "fallback": self._last_error is not None}

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        if self.mode != "memory":
            try:
                record = self._etcd_get(key)
                if record is not None:
                    self._last_backend = "etcd"
                    self._last_error = None
                    return record
            except Exception as exc:
                self._last_error = str(exc)
                if self.mode == "etcd":
                    raise
        record = self._memory.get(key)
        if record is None:
            return None
        self._last_backend = "memory"
        return copy.deepcopy(record)

    def status(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "endpoint": self.endpoint,
            "prefix": self.prefix,
            "active_backend": self._last_backend,
            "last_error": self._last_error,
        }

    def _qualified_key(self, key: str) -> str:
        normalized = key if key.startswith("/") else f"/{key}"
        return f"{self.prefix}{normalized}"

    @staticmethod
    def _encode_bytes(value: str) -> str:
        return base64.b64encode(value.encode("utf-8")).decode("ascii")

    @staticmethod
    def _decode_bytes(value: str) -> str:
        return base64.b64decode(value.encode("ascii")).decode("utf-8")

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib_request.Request(
            f"{self.endpoint}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib_request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:  # pragma: no cover - network/system variance
            raise RuntimeError(f"etcd HTTP error {exc.code}: {exc.reason}") from exc
        except urllib_error.URLError as exc:  # pragma: no cover - network/system variance
            raise RuntimeError(f"etcd network error: {exc.reason}") from exc

    def _etcd_put(self, key: str, payload: Dict[str, Any]) -> None:
        self._post_json(
            "/v3/kv/put",
            {
                "key": self._encode_bytes(self._qualified_key(key)),
                "value": self._encode_bytes(json.dumps(payload, sort_keys=True)),
            },
        )

    def _etcd_get(self, key: str) -> Optional[Dict[str, Any]]:
        response = self._post_json(
            "/v3/kv/range",
            {
                "key": self._encode_bytes(self._qualified_key(key)),
            },
        )
        kvs = response.get("kvs") or []
        if not kvs:
            return None
        raw_value = kvs[0].get("value")
        if not raw_value:
            return None
        return json.loads(self._decode_bytes(raw_value))

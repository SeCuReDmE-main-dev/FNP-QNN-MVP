"""Local FFeD plugin bridge for QNN fractal carrier features.

The bridge is intentionally non-blocking: FNP-QNN can run without the local
pluginpack, Redis, Datadog, E2B, or Docker. When enabled, it records which
allowlisted plugin saw which simulation parameters, then maps plugin outputs
into bounded D_f/D_f_hat/dF/i_fractal_candidate signals.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import threading
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from .cpai_mesh import (
    CPAI_MESH_METRICS,
    CPAI_MESH_NODES,
    CPAI_SERVICE_CHECK,
    DATADOG_MESH_DASHBOARD_ID,
    DATADOG_MESH_NOTEBOOK_ID,
    CPAIMeshState,
    cpai_mesh_profile,
)
from .neutrosophic_quantum_primitives import (
    RESEARCH_BOUNDARY,
    SOURCE_HIERARCHY,
    fractal_carrier_profile,
    neutrosophic_gate_algebra,
    normalize_fractal_dimension,
)


DEFAULT_PLUGINPACK_PATH = Path(os.getenv("FNP_QNN_FFED_PLUGINPACK_PATH", "./pluginpack")).resolve()
PLUGIN_POLICY_PATH = Path(__file__).with_name("contracts") / "ffed-plugin-policy.v1.json"


def _load_plugin_policy() -> Dict[str, Any]:
    policy = json.loads(PLUGIN_POLICY_PATH.read_text(encoding="utf-8"))
    if policy.get("schema") != "fnp-qnn.ffed-plugin-policy.v1":
        raise ValueError("Unsupported FFeD plugin policy schema")
    mvp5 = tuple(policy.get("mvp5_plugin_ids") or ())
    weights = dict(policy.get("weights") or {})
    if len(mvp5) != 5 or set(mvp5) != set(weights):
        raise ValueError("FFeD MVP5 policy must define exactly five weighted plugins")
    if abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
        raise ValueError("FFeD MVP5 plugin weights must sum to 1.0")
    return policy


PLUGIN_POLICY = _load_plugin_policy()
PLUGIN_POLICY_SCHEMA = str(PLUGIN_POLICY["schema"])
MVP5_PLUGIN_IDS = tuple(PLUGIN_POLICY["mvp5_plugin_ids"])
NEXT5_PLUGIN_IDS = tuple(PLUGIN_POLICY["next5_plugin_ids"])
PLUGIN_WEIGHTS = {key: float(value) for key, value in PLUGIN_POLICY["weights"].items()}
P114_PLUGIN_ID = "p114_ffed_neutrosophic_consensus"
P046_PLUGIN_ID = "p046_rossler_beaulieu_cubic_framework"


def _clamp01(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return float(min(1.0, max(0.0, numeric)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _compact_summary(value: Any, max_items: int = 6) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _compact_summary(item, max_items=max_items) for key, item in list(value.items())[:max_items]}
    if isinstance(value, list):
        return [_compact_summary(item, max_items=max_items) for item in value[:max_items]]
    if isinstance(value, tuple):
        return [_compact_summary(item, max_items=max_items) for item in list(value)[:max_items]]
    return value


def numeric_series_from_events(events: Optional[Iterable[Any]], limit: int = 64) -> List[float]:
    series: List[float] = []
    for event in events or []:
        value = event.get("value") if isinstance(event, Mapping) else getattr(event, "value", None)
        try:
            series.append(float(value))
        except (TypeError, ValueError):
            continue
        if len(series) >= limit:
            break
    return series or [0.12, 0.34, 0.21, 0.78, 0.43, 0.91]


def consensus_items_from_events(events: Optional[Iterable[Any]], limit: int = 8) -> List[Dict[str, Any]]:
    values = numeric_series_from_events(events, limit=limit)
    items: List[Dict[str, Any]] = []
    for index, value in enumerate(values):
        truth = _clamp01(value)
        falsity = _clamp01(1.0 - truth)
        indeterminacy = _clamp01(1.0 - abs(truth - falsity))
        items.append(
            {
                "label": f"event-{index}",
                "truth": truth,
                "indeterminacy": indeterminacy,
                "falsity": falsity,
            }
        )
    return items or [{"label": "default", "truth": 0.55, "indeterminacy": 0.30, "falsity": 0.15}]


@dataclass(frozen=True)
class PluginSignal:
    plugin_id: str
    raw_metric: float
    D_f: float
    D_min: float
    D_max: float
    D_f_hat: float
    T: float
    I: float
    F: float
    dF_contribution: float
    interpretation: str
    source_output_summary: Any

    def as_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "raw_metric": float(self.raw_metric),
            "D_f": float(self.D_f),
            "D_min": float(self.D_min),
            "D_max": float(self.D_max),
            "D_f_hat": float(self.D_f_hat),
            "T": float(self.T),
            "I_system_component": float(self.I),
            "F": float(self.F),
            "dF_contribution": float(self.dF_contribution),
            "interpretation": self.interpretation,
            "source_output_summary": self.source_output_summary,
            "hierarchy": SOURCE_HIERARCHY,
            "research_boundary": RESEARCH_BOUNDARY,
        }


class FfeDPluginBridge:
    """Allowlisted FFeD plugin router for local QNN simulations."""

    def __init__(self, pluginpack_path: Optional[str | Path] = None):
        self.pluginpack_path = Path(pluginpack_path) if pluginpack_path is not None else DEFAULT_PLUGINPACK_PATH
        self.repo_root = Path(__file__).resolve().parents[1]
        self._runtime_lock = threading.RLock()

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "router": "ffed-plugin-bridge",
            "pluginpack_path": str(self.pluginpack_path),
            "pluginpack_exists": self.pluginpack_path.exists(),
            "runtime_importable": self._runtime_importable(),
            "mvp5_plugins": list(MVP5_PLUGIN_IDS),
            "next5_plugins": list(NEXT5_PLUGIN_IDS),
            "plugin_policy_schema": PLUGIN_POLICY_SCHEMA,
            "integrity_required_before_invocation": True,
            "mcp_surface": {
                "ffed_mcp_config_present": (self.pluginpack_path / ".mcp.json").exists(),
                "ffed_mcp_callable_in_current_session": None,
                "datadog_mcp_expected": True,
                "datadog_mcp_callable_in_current_session": False,
                "e2b_mcp_expected": True,
            },
            "cpai_mesh_profile": cpai_mesh_profile(),
            "observability": self._observability_status(),
            "research_boundary": RESEARCH_BOUNDARY,
        }

    def run_mvp5(
        self,
        context: Optional[Mapping[str, Any]] = None,
        *,
        include_trace: bool = True,
        plugin_set: str = "mvp5",
    ) -> Dict[str, Any]:
        context = dict(context or {})
        cpai_state = CPAIMeshState.from_context(context.get("cpai_context") or context.get("cpai_mesh") or {})
        base_status = self.status()
        if plugin_set != "mvp5":
            return self._disabled_payload(base_status, f"unsupported plugin_set: {plugin_set}", include_trace)
        if not self.pluginpack_path.exists():
            return self._disabled_payload(base_status, "pluginpack path not found", include_trace)
        try:
            run_plugin = self._load_runtime()
        except (ImportError, OSError, ValueError) as exc:
            return self._disabled_payload(base_status, f"plugin runtime import failed: {exc}", include_trace)

        effective_configs = self._build_plugin_configs(context)
        results: Dict[str, Any] = {}
        errors: List[Dict[str, Any]] = []
        for plugin_id in MVP5_PLUGIN_IDS:
            try:
                results[plugin_id] = run_plugin(plugin_id, effective_configs[plugin_id])
                if results[plugin_id].get("status") != "success":
                    errors.append(
                        {
                            "plugin_id": plugin_id,
                            "status": results[plugin_id].get("status", "error"),
                            "message": (results[plugin_id].get("metadata") or {}).get("message", "plugin returned non-success"),
                        }
                    )
            except Exception as exc:
                results[plugin_id] = {"status": "error", "plugin_id": plugin_id, "outputs": {}, "metrics": {}, "metadata": {"message": str(exc)}}
                errors.append({"plugin_id": plugin_id, "status": "error", "message": str(exc)})

        payload = build_plugin_payload_from_results(
            results,
            status={
                **base_status,
                "enabled": True,
                "runtime_importable": True,
                "plugin_set": plugin_set,
                "effective_configs": effective_configs,
                "cpai_mesh_state": cpai_state.as_dict(),
            },
            cpai_state=cpai_state,
            include_trace=include_trace,
        )
        payload["plugin_errors"] = errors
        return payload

    def run_p114_consensus(
        self,
        items: Optional[Iterable[Any]] = None,
        *,
        mode: str = "score_evidence",
        thresholds: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run p114 as a first-class CLI/admission gate.

        The full MVP5 hook maps p114 into QNN feature carriers. This narrower
        method is for transport decisions: should a CLI admission proceed,
        proceed with caveats, ask for clarification, or be blocked before LVFM.
        """

        base_status = self.status()
        if not self.pluginpack_path.exists():
            return p114_gate_payload(
                plugin_result={
                    "status": "disabled",
                    "plugin_id": P114_PLUGIN_ID,
                    "outputs": {},
                    "metrics": {},
                    "metadata": {"message": "pluginpack path not found"},
                },
                bridge_status={**base_status, "enabled": False, "reason": "pluginpack path not found"},
            )
        try:
            run_plugin = self._load_runtime()
        except (ImportError, OSError, ValueError) as exc:
            return p114_gate_payload(
                plugin_result={
                    "status": "disabled",
                    "plugin_id": P114_PLUGIN_ID,
                    "outputs": {},
                    "metrics": {},
                    "metadata": {"message": f"plugin runtime import failed: {exc}"},
                },
                bridge_status={**base_status, "enabled": False, "reason": f"plugin runtime import failed: {exc}"},
            )

        config: Dict[str, Any] = {"mode": mode, "items": list(items or [])[:100]}
        if thresholds:
            config["thresholds"] = dict(thresholds)
        try:
            result = run_plugin(P114_PLUGIN_ID, config)
        except Exception as exc:
            result = {
                "status": "error",
                "plugin_id": P114_PLUGIN_ID,
                "outputs": {},
                "metrics": {},
                "metadata": {"message": str(exc), "mode": mode},
            }
        return p114_gate_payload(
            plugin_result=result,
            bridge_status={**base_status, "enabled": True, "runtime_importable": True, "effective_config": config},
        )

    def run_p046_schedule(self, config: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        """Run p046 as a bounded deterministic fault-schedule source."""

        base_status = self.status()
        if not self.pluginpack_path.exists():
            return p046_schedule_payload(
                {
                    "status": "disabled",
                    "plugin_id": P046_PLUGIN_ID,
                    "outputs": {},
                    "metrics": {},
                    "metadata": {"message": "pluginpack path not found"},
                },
                {**base_status, "enabled": False, "reason": "pluginpack path not found"},
            )
        try:
            run_plugin = self._load_runtime()
        except (ImportError, OSError, ValueError) as exc:
            return p046_schedule_payload(
                {
                    "status": "disabled",
                    "plugin_id": P046_PLUGIN_ID,
                    "outputs": {},
                    "metrics": {},
                    "metadata": {"message": f"plugin runtime import failed: {exc}"},
                },
                {**base_status, "enabled": False, "reason": f"plugin runtime import failed: {exc}"},
            )

        effective = {
            "mode": "trajectory",
            "steps": 2400,
            "discard": 200,
            "sample_limit": 256,
            "a": 0.2,
            "b": 0.2,
            "c": 5.7,
            "k_cubic": 0.000001,
            "dt": 0.01,
        }
        if config:
            for key in effective:
                if key in config:
                    effective[key] = config[key]
        try:
            result = run_plugin(P046_PLUGIN_ID, effective)
        except Exception as exc:
            result = {
                "status": "error",
                "plugin_id": P046_PLUGIN_ID,
                "outputs": {},
                "metrics": {},
                "metadata": {"message": str(exc)},
            }
        return p046_schedule_payload(
            result,
            {**base_status, "enabled": True, "runtime_importable": True, "effective_config": effective},
        )

    def _build_plugin_configs(self, context: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        events = context.get("events") or context.get("observations") or []
        series = context.get("series") or numeric_series_from_events(events)
        items = context.get("items") or consensus_items_from_events(events)
        # These clamps are part of the impact-verification contract: the trace
        # must show the parameters the plugins actually received, not only the
        # user's raw request. p046, for example, rejects steps below 100.
        steps = max(100, int(_safe_float(context.get("steps", 256), 256)))
        n_atoms = max(2, int(_safe_float(context.get("n_atoms", max(8, len(series) * 2)), 8)))
        depth = max(1, int(_safe_float(context.get("depth", 4), 4)))
        max_terms = max(8, int(_safe_float(context.get("max_terms", 64), 64)))
        return {
            "p011_fractales_atomiques": {"mode": "summary", "n_atoms": n_atoms, "depth": depth},
            "p046_rossler_beaulieu_cubic_framework": {"mode": "summary", "steps": steps},
            "p097_fbm_tuner": {"mode": "analyze_series", "series": [float(value) for value in series[:64]]},
            "p109_dual_triplex": {
                "mode": "summary",
                "t_value": _safe_float(context.get("t_value", 14.134725), 14.134725),
                "max_terms": max_terms,
            },
            "p114_ffed_neutrosophic_consensus": {"mode": "score_evidence", "items": list(items)[:16]},
        }

    def _load_runtime(self):
        import importlib.util

        pluginpack = self.pluginpack_path.resolve()
        package_dir = pluginpack / "ffed_runtime"
        target_file = package_dir / "__init__.py"

        if not pluginpack.is_dir():
            raise ValueError(f"Pluginpack path is not a directory: {pluginpack}")
        if not target_file.is_file():
            raise ImportError(f"ffed_runtime package not found in pluginpack: {target_file}")

        # The pluginpack runtime imports sibling packages such as ``security``.
        # Keep the explicit pluginpack root importable for the lifetime of the
        # process; no global installation is required.
        pluginpack_text = str(pluginpack)
        inserted = pluginpack_text not in sys.path
        if inserted:
            sys.path.insert(0, pluginpack_text)

        spec = importlib.util.spec_from_file_location(
            "ffed_runtime",
            str(target_file),
            submodule_search_locations=[str(package_dir)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load ffed_runtime from {target_file}")

        module_prefixes = ("ffed_runtime", "ffed_plugins")
        previous_modules = {
            name: loaded
            for name, loaded in sys.modules.items()
            if name == "ffed_runtime" or name.startswith("ffed_runtime.") or name == "ffed_plugins" or name.startswith("ffed_plugins.")
        }
        for name in previous_modules:
            sys.modules.pop(name, None)
        module = importlib.util.module_from_spec(spec)
        sys.modules["ffed_runtime"] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            for name in list(sys.modules):
                if any(name == prefix or name.startswith(f"{prefix}.") for prefix in module_prefixes):
                    sys.modules.pop(name, None)
            sys.modules.update(previous_modules)
            raise
        finally:
            if inserted and pluginpack_text in sys.path:
                sys.path.remove(pluginpack_text)
        isolated_modules = {
            name: loaded
            for name, loaded in sys.modules.items()
            if any(name == prefix or name.startswith(f"{prefix}.") for prefix in module_prefixes)
        }
        for name in isolated_modules:
            sys.modules.pop(name, None)
        sys.modules.update(previous_modules)
        if not hasattr(module, "run_plugin"):
            raise ImportError("ffed_runtime.run_plugin is missing")

        verify_plugin_integrity = self._load_integrity_verifier(pluginpack)

        def isolated_run_plugin(plugin_id, config=None):
            if plugin_id not in set(MVP5_PLUGIN_IDS) | set(NEXT5_PLUGIN_IDS):
                raise ValueError(f"Plugin is not allowlisted by {PLUGIN_POLICY_SCHEMA}: {plugin_id}")
            integrity = verify_plugin_integrity(plugin_id)
            if not integrity.get("valid"):
                errors = "; ".join(str(item) for item in integrity.get("errors") or ["integrity verification failed"])
                raise ValueError(f"Plugin integrity rejected for {plugin_id}: {errors}")
            with self._runtime_lock:
                call_previous = {
                    name: loaded
                    for name, loaded in sys.modules.items()
                    if any(name == prefix or name.startswith(f"{prefix}.") for prefix in module_prefixes)
                }
                sys.modules.update(isolated_modules)
                call_inserted = pluginpack_text not in sys.path
                if call_inserted:
                    sys.path.insert(0, pluginpack_text)
                try:
                    return module.run_plugin(plugin_id, config)
                finally:
                    for name in list(sys.modules):
                        if any(name == prefix or name.startswith(f"{prefix}.") for prefix in module_prefixes):
                            loaded = sys.modules.get(name)
                            loaded_file = str(getattr(loaded, "__file__", ""))
                            if loaded_file.startswith(pluginpack_text) or name in isolated_modules:
                                isolated_modules[name] = loaded
                                sys.modules.pop(name, None)
                    sys.modules.update(call_previous)
                    if call_inserted and pluginpack_text in sys.path:
                        sys.path.remove(pluginpack_text)

        return isolated_run_plugin

    def _load_integrity_verifier(self, pluginpack: Path):
        import importlib.util

        integrity_file = pluginpack / "security" / "integrity.py"
        if not integrity_file.is_file():
            raise ImportError(f"Plugin integrity verifier not found: {integrity_file}")
        module_name = f"_fnp_qnn_ffed_integrity_{abs(hash(str(pluginpack)))}"
        spec = importlib.util.spec_from_file_location(module_name, str(integrity_file))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin integrity verifier from {integrity_file}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        verifier = getattr(module, "verify_plugin_integrity", None)
        if not callable(verifier):
            raise ImportError("security.integrity.verify_plugin_integrity is missing")
        return verifier

    def _runtime_importable(self) -> bool:
        try:
            self._load_runtime()
            return True
        except Exception:
            return False

    def _disabled_payload(self, status: Mapping[str, Any], reason: str, include_trace: bool) -> Dict[str, Any]:
        return {
            "plugin_fractal_signals": [],
            "plugin_fractal_carrier": None,
            "plugin_tension_profile": None,
            "plugin_gate_profile": None,
            "plugin_gate_trace": [] if include_trace else None,
            "plugin_errors": [{"status": "disabled", "message": reason}],
            "plugin_hook_status": {**dict(status), "enabled": False, "reason": reason},
            "cpai_mesh_profile": cpai_mesh_profile(),
            "feature_vector": [],
            "impact_verification": {
                "router": "ffed-plugin-bridge",
                "activated": False,
                "reason": reason,
                "allowlist": list(MVP5_PLUGIN_IDS),
                "plugin_policy_schema": PLUGIN_POLICY_SCHEMA,
                "observed_plugins": [],
                "cpai_mesh_base": cpai_mesh_profile(),
            },
        }

    def _observability_status(self) -> Dict[str, Any]:
        compose = self.repo_root / "docker-compose.yml"
        compose_text = compose.read_text(encoding="utf-8") if compose.exists() else ""
        return {
            "docker_compose_present": compose.exists(),
            "datadog_agent_service_present": "datadog-agent:" in compose_text,
            "e2b_auditor_service_present": "e2b-auditor:" in compose_text,
            "plugin_engine_redis_service_present": "plugin-engine-redis:" in compose_text,
            "cpai_mesh_runbook_present": (Path.home() / ".codex" / "skills" / "dd-agent-control" / "SKILL.md").exists(),
            "cpai_mesh_expected_nodes": list(CPAI_MESH_NODES),
            "cpai_mesh_expected_metrics": list(CPAI_MESH_METRICS),
            "cpai_mesh_service_check": CPAI_SERVICE_CHECK,
            "datadog_mesh_dashboard_id": DATADOG_MESH_DASHBOARD_ID,
            "datadog_mesh_notebook_id": DATADOG_MESH_NOTEBOOK_ID,
            "datadog_config_present": (self.repo_root / "observability" / "datadog" / "agent-conf.d").exists(),
            "e2b_audit_script_present": (self.repo_root / "scripts" / "e2b_datadog_audit" / "audit_e2b.py").exists(),
            "datadog_env_present": bool(os.getenv("DD_API_KEY") or os.getenv("DATADOG_API_KEY")),
            "e2b_env_present": bool(os.getenv("E2B_API_KEY")),
            "redis_url_present": bool(os.getenv("FNP_QNN_PLUGIN_ENGINE_REDIS_URL")),
            "secrets_exposed": False,
        }


def build_plugin_payload_from_results(
    results: Mapping[str, Any],
    *,
    status: Optional[Mapping[str, Any]] = None,
    cpai_state: Optional[CPAIMeshState] = None,
    include_trace: bool = True,
) -> Dict[str, Any]:
    signals = [_signal_from_result(plugin_id, results.get(plugin_id) or {}) for plugin_id in MVP5_PLUGIN_IDS]
    active_signals = [signal for signal in signals if signal is not None]
    active_payloads = [signal.as_dict() for signal in active_signals]
    carrier = _global_carrier(active_signals)
    gate_payload = _gate_payload(active_signals, carrier)
    status_payload = dict(status or {})
    status_payload.setdefault("router", "ffed-plugin-bridge")
    status_payload.setdefault("enabled", True)
    mesh_profile = cpai_mesh_profile(cpai_state)
    return {
        "plugin_fractal_signals": active_payloads,
        "plugin_fractal_carrier": carrier,
        "plugin_tension_profile": gate_payload["plugin_tension_profile"],
        "plugin_gate_profile": gate_payload["plugin_gate_profile"],
        "plugin_gate_trace": gate_payload["plugin_gate_trace"] if include_trace else None,
        "plugin_errors": [],
        "plugin_hook_status": status_payload,
        "cpai_mesh_profile": mesh_profile,
        "feature_vector": _feature_vector(active_payloads, carrier, gate_payload["plugin_gate_profile"]),
        "impact_verification": {
            "router": "ffed-plugin-bridge",
            "activated": bool(active_signals),
            "allowlist": list(MVP5_PLUGIN_IDS),
            "plugin_policy_schema": PLUGIN_POLICY_SCHEMA,
            "observed_plugins": [signal.plugin_id for signal in active_signals],
            "expected_plugins": list(MVP5_PLUGIN_IDS),
            "all_expected_plugins_seen": [signal.plugin_id for signal in active_signals] == list(MVP5_PLUGIN_IDS),
            "effective_configs": status_payload.get("effective_configs", {}),
            "cpai_mesh_base": mesh_profile,
            "secrets_exposed": False,
        },
    }


def p114_gate_payload(plugin_result: Mapping[str, Any], bridge_status: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    outputs = dict(plugin_result.get("outputs") or {})
    metrics = dict(plugin_result.get("metrics") or {})
    consensus = dict(outputs.get("consensus") or {})
    truth = _clamp01(consensus.get("truth", metrics.get("truth")))
    indeterminacy = _clamp01(consensus.get("indeterminacy", metrics.get("indeterminacy", 1.0)))
    falsity = _clamp01(consensus.get("falsity", metrics.get("falsity")))
    action = str(outputs.get("action") or _p114_action_from_consensus(truth, indeterminacy, falsity))
    gate = _p114_cli_gate(action, truth, indeterminacy, falsity)
    status = str(plugin_result.get("status") or "error")
    return {
        "success": status == "success",
        "plugin_id": P114_PLUGIN_ID,
        "status": status,
        "consensus": {
            "truth": truth,
            "indeterminacy": indeterminacy,
            "falsity": falsity,
        },
        "action": action,
        "explanation": outputs.get("explanation") or gate["reason"],
        "items": outputs.get("items", []),
        "cli_gate": gate,
        "bridge_status": dict(bridge_status or {}),
        "metadata": dict(plugin_result.get("metadata") or {}),
        "raw_token_stored": False,
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }


def p046_schedule_payload(
    plugin_result: Mapping[str, Any],
    bridge_status: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    outputs = dict(plugin_result.get("outputs") or {})
    metrics = dict(plugin_result.get("metrics") or {})
    trajectory = outputs.get("trajectory")
    clamp_hits = int(_safe_float(metrics.get("clamp_hit_count"), -1.0))
    nonfinite_resets = int(_safe_float(metrics.get("nonfinite_reset_count"), -1.0))
    max_abs = _safe_float(metrics.get("trajectory_max_abs"), float("inf"))
    reasons: List[str] = []
    if plugin_result.get("status") != "success":
        reasons.append("p046_plugin_unavailable")
    if not isinstance(trajectory, list) or not trajectory:
        reasons.append("p046_trajectory_missing")
    if clamp_hits != 0:
        reasons.append("p046_clamp_detected")
    if nonfinite_resets != 0:
        reasons.append("p046_nonfinite_reset_detected")
    if not 0.0 <= max_abs < 100.0:
        reasons.append("p046_trajectory_out_of_bounds")
    if metrics.get("simulation_stable") is not True:
        reasons.append("p046_simulation_not_stable")
    accepted = not reasons
    return {
        "success": accepted,
        "plugin_id": P046_PLUGIN_ID,
        "status": "accepted" if accepted else "blocked",
        "reason_codes": reasons,
        "trajectory": trajectory if isinstance(trajectory, list) else [],
        "metrics": {
            "clamp_hit_count": clamp_hits,
            "nonfinite_reset_count": nonfinite_resets,
            "trajectory_max_abs": max_abs,
            "simulation_stable": metrics.get("simulation_stable") is True,
            "chaos_risk": _clamp01(metrics.get("chaos_risk")),
            "divergence_index": _clamp01(metrics.get("divergence_index")),
        },
        "bridge_status": dict(bridge_status or {}),
        "research_boundary": "bounded deterministic fault schedule; not physical evidence",
    }


def _p114_action_from_consensus(truth: float, indeterminacy: float, falsity: float) -> str:
    if indeterminacy > 0.6:
        return "ask_clarification"
    if falsity > 0.5:
        return "escalate_or_reject"
    if truth > 0.7:
        return "respond_with_confidence"
    return "respond_with_caveat"


def _p114_cli_gate(action: str, truth: float, indeterminacy: float, falsity: float) -> Dict[str, Any]:
    if action == "ask_clarification":
        return {
            "status": "needs_clarification",
            "allow_lvfm_admission": False,
            "reason": "p114 indeterminacy is high; request more evidence before admitting to LVFM.",
        }
    if action == "escalate_or_reject":
        return {
            "status": "blocked",
            "allow_lvfm_admission": False,
            "reason": "p114 falsity is high; block or escalate the admission before LVFM.",
        }
    if action == "respond_with_confidence":
        return {
            "status": "accepted",
            "allow_lvfm_admission": True,
            "reason": "p114 truth is high; admit with confidence while preserving provenance.",
        }
    return {
        "status": "accepted_with_caveat",
        "allow_lvfm_admission": True,
        "reason": "p114 did not cross a blocking threshold; admit with explicit caveats.",
    }


def _signal_from_result(plugin_id: str, result: Mapping[str, Any]) -> Optional[PluginSignal]:
    if result.get("status") != "success":
        return None
    metrics = dict(result.get("metrics") or {})
    outputs = dict(result.get("outputs") or {})
    # Each plugin has its own native metric vocabulary. The adapter maps that
    # vocabulary into a local D_f carrier while preserving the hierarchy:
    # I -> I_system^S -> D_f -> dF -> i_fractal. None of these values replace I.
    if plugin_id == "p011_fractales_atomiques":
        overload = _clamp01(metrics.get("overload_risk"))
        recomposition = _clamp01(metrics.get("recomposition_score"))
        d_f = _clamp01(0.6 * overload + 0.4 * (1.0 - recomposition))
        return _signal(plugin_id, d_f, 0.0, 1.0, 1.0 - d_f, d_f, overload, d_f, "atomic overload and recomposition tension", outputs)
    if plugin_id == "p046_rossler_beaulieu_cubic_framework":
        chaos = _clamp01(metrics.get("chaos_risk"))
        divergence = _clamp01(metrics.get("divergence_index"))
        anti_entropy = _safe_float(metrics.get("anti_entropy_balance"), 0.0)
        d_f = _clamp01(0.5 * chaos + 0.3 * divergence + 0.2 * max(0.0, -anti_entropy))
        return _signal(plugin_id, d_f, 0.0, 1.0, 1.0 - d_f, d_f, chaos, d_f, "chaos, divergence, and anti-entropy tension", outputs)
    if plugin_id == "p097_fbm_tuner":
        d_f = _clamp01(metrics.get("instability_score"))
        return _signal(plugin_id, d_f, 0.0, 1.0, 1.0 - d_f, d_f, _clamp01(d_f - 0.5), d_f, "roughness and drift instability", outputs)
    if plugin_id == "p109_dual_triplex":
        d_f = max(0.0, _safe_float(metrics.get("fractal_density"), 0.0))
        d_hat = normalize_fractal_dimension(d_f, 0.0, 2.0)
        truth = _clamp01(metrics.get("truth"))
        falsehood = _clamp01(_safe_float(metrics.get("falsehood"), 0.0) / 4.0)
        return PluginSignal(
            plugin_id=plugin_id,
            raw_metric=d_f,
            D_f=d_f,
            D_min=0.0,
            D_max=2.0,
            D_f_hat=d_hat,
            T=truth,
            I=d_hat,
            F=falsehood,
            dF_contribution=d_hat,
            interpretation="mandatory dual-triplex fractal density carrier",
            source_output_summary=_compact_summary(outputs),
        )
    if plugin_id == "p114_ffed_neutrosophic_consensus":
        consensus = dict(outputs.get("consensus") or {})
        truth = _clamp01(consensus.get("truth", metrics.get("truth")))
        indeterminacy = _clamp01(consensus.get("indeterminacy", metrics.get("indeterminacy")))
        falsity = _clamp01(consensus.get("falsity", metrics.get("falsity")))
        return _signal(plugin_id, indeterminacy, 0.0, 1.0, truth, indeterminacy, falsity, indeterminacy, "native FFeD T/I/F consensus ambiguity", outputs)
    return None


def _signal(
    plugin_id: str,
    d_f: float,
    d_min: float,
    d_max: float,
    truth: float,
    indeterminacy: float,
    falsity: float,
    d_f_contribution: float,
    interpretation: str,
    outputs: Mapping[str, Any],
) -> PluginSignal:
    d_hat = normalize_fractal_dimension(d_f, d_min, d_max)
    return PluginSignal(
        plugin_id=plugin_id,
        raw_metric=float(d_f),
        D_f=float(d_f),
        D_min=float(d_min),
        D_max=float(d_max),
        D_f_hat=d_hat,
        T=_clamp01(truth),
        I=_clamp01(indeterminacy),
        F=_clamp01(falsity),
        dF_contribution=_clamp01(d_f_contribution),
        interpretation=interpretation,
        source_output_summary=_compact_summary(outputs),
    )


def _global_carrier(signals: Sequence[PluginSignal]) -> Optional[Dict[str, Any]]:
    if not signals:
        return None
    # The global plugin carrier is a weighted view over normalized D_f_hat
    # values, so plugins with wider native scales cannot dominate by magnitude.
    weighted_total = 0.0
    total_weight = 0.0
    for signal in signals:
        weight = PLUGIN_WEIGHTS.get(signal.plugin_id, 0.0)
        weighted_total += signal.D_f_hat * weight
        total_weight += weight
    d_f_plugin = weighted_total / total_weight if total_weight > 0.0 else 0.0
    carrier = fractal_carrier_profile(
        d_f_plugin,
        0.0,
        1.0,
        measurement_method="ffed-mvp5-plugin-weighted-mean",
        scale="mvp5-router",
        domain="qnn-plugin-hook",
        admissible=True,
    )
    carrier["D_f_plugin"] = float(d_f_plugin)
    carrier["D_f_hat_plugin"] = carrier["D_f_hat"]
    carrier["plugin_weights"] = dict(PLUGIN_WEIGHTS)
    carrier["plugin_ids"] = [signal.plugin_id for signal in signals]
    return carrier


def _gate_payload(signals: Sequence[PluginSignal], carrier: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    by_id = {signal.plugin_id: signal.as_dict() for signal in signals}
    empty = {"T": 0.0, "I": 0.0, "F": 1.0}
    p011 = by_id.get("p011_fractales_atomiques", empty)
    p046 = by_id.get("p046_rossler_beaulieu_cubic_framework", empty)
    p097 = by_id.get("p097_fbm_tuner", empty)
    p109 = by_id.get("p109_dual_triplex", empty)
    p114 = by_id.get("p114_ffed_neutrosophic_consensus", empty)
    # These gates are explanatory measurement gates. They surface persistent
    # instability and local atom/fractal stress; they do not resolve ambiguity
    # and they do not authorize clinical, security, or production decisions.
    persistent_instability = neutrosophic_gate_algebra("and", _tif(p046), _tif(p097))
    fractal_atom_density = neutrosophic_gate_algebra("or", _tif(p011), _tif(p109))
    ambiguity_chaos = neutrosophic_gate_algebra("if_then", _tif(p114), _tif(p046))
    plugin_tension_profile = neutrosophic_gate_algebra("and", fractal_atom_density, ambiguity_chaos)
    d_f_hat = _clamp01((carrier or {}).get("D_f_hat_plugin"))
    d_f_plugin = _clamp01(
        0.5 * d_f_hat
        + 0.25 * _tif(p114)["F"]
        + 0.15 * _tif(p046)["F"]
        + 0.10 * _tif(p011)["F"]
    )
    stability_contrast = neutrosophic_gate_algebra("not", {"T": 1.0 - d_f_hat, "I": d_f_hat, "F": d_f_plugin})
    plugin_gate_profile = {
        "T": plugin_tension_profile["T"],
        "I_system_component": plugin_tension_profile["I"],
        "F": plugin_tension_profile["F"],
        "D_f_hat_plugin": d_f_hat,
        "dF_plugin": d_f_plugin,
        "hierarchy": SOURCE_HIERARCHY,
        "research_boundary": RESEARCH_BOUNDARY,
    }
    return {
        "plugin_tension_profile": {
            "persistent_instability": persistent_instability,
            "fractal_atom_density": fractal_atom_density,
            "ambiguity_chaos": ambiguity_chaos,
            "plugin_tension_profile": plugin_tension_profile,
            "stability_contrast": stability_contrast,
            "dF_plugin": d_f_plugin,
            "hierarchy": SOURCE_HIERARCHY,
        },
        "plugin_gate_profile": plugin_gate_profile,
        "plugin_gate_trace": [
            {"operation": "AND", "left": "p046", "right": "p097", "result": persistent_instability},
            {"operation": "OR", "left": "p011", "right": "p109", "result": fractal_atom_density},
            {"operation": "IF_THEN", "left": "p114", "right": "p046", "result": ambiguity_chaos},
            {"operation": "AND", "left": "fractal_atom_density", "right": "ambiguity_chaos", "result": plugin_tension_profile},
            {"operation": "NOT", "left": "stability", "result": stability_contrast},
        ],
    }


def _tif(signal: Mapping[str, Any]) -> Dict[str, float]:
    return {
        "T": _clamp01(signal.get("T")),
        "I": _clamp01(signal.get("I_system_component", signal.get("I"))),
        "F": _clamp01(signal.get("F")),
    }


def _feature_vector(
    signals: Sequence[Mapping[str, Any]],
    carrier: Optional[Mapping[str, Any]],
    gate_profile: Optional[Mapping[str, Any]],
) -> List[float]:
    vector = [
        _clamp01((carrier or {}).get("D_f_hat_plugin", (carrier or {}).get("D_f_hat"))),
        _clamp01((gate_profile or {}).get("dF_plugin")),
        _clamp01((gate_profile or {}).get("T")),
        _clamp01((gate_profile or {}).get("I_system_component")),
        _clamp01((gate_profile or {}).get("F")),
    ]
    vector.extend(_clamp01(signal.get("D_f_hat")) for signal in signals)
    return [float(value) for value in vector]


__all__ = [
    "DEFAULT_PLUGINPACK_PATH",
    "FfeDPluginBridge",
    "MVP5_PLUGIN_IDS",
    "NEXT5_PLUGIN_IDS",
    "P114_PLUGIN_ID",
    "P046_PLUGIN_ID",
    "PLUGIN_WEIGHTS",
    "build_plugin_payload_from_results",
    "consensus_items_from_events",
    "cpai_mesh_profile",
    "numeric_series_from_events",
    "p114_gate_payload",
    "p046_schedule_payload",
]

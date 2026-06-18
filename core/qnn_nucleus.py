"""
QNN nucleus for the Cerebrum adapter.

The preferred execution target is Qiskit Machine Learning, but the module
falls back to a deterministic PyTorch surrogate when the Qiskit stack is not
installed in the local environment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from .cerebrum_adapter import CerebrumAdapter
from .ffed_plugin_bridge import FfeDPluginBridge
from .neutrosophic_quantum_primitives import fractal_carrier_profile, neutrobit_features_from_vector

try:  # Optional Qiskit path. The repo should still run without it.
    from qiskit.circuit import QuantumCircuit
    from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap
    from qiskit.primitives import Estimator
    from qiskit_machine_learning.connectors import TorchConnector
    from qiskit_machine_learning.neural_networks import EstimatorQNN

    QISKIT_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency path
    QISKIT_AVAILABLE = False


@dataclass(frozen=True)
class QNNCandidate:
    name: str
    role: str
    available: bool
    backend: str
    notes: str


@dataclass
class QNNBenchmarkResult:
    candidate: str
    available: bool
    backend: str
    notes: str
    train_accuracy: Optional[float] = None
    test_accuracy: Optional[float] = None
    predicted_probability: Optional[float] = None
    feature_dimension: Optional[int] = None


class _SurrogateQuantumNet(nn.Module):
    def __init__(self, input_dim: int):
        super().__init__()
        hidden_dim = max(8, input_dim * 2)
        self.network = nn.Sequential(
            nn.Linear(input_dim * 3, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim // 2 if hidden_dim > 8 else 8),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2 if hidden_dim > 8 else 8, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        expanded = torch.cat([x, torch.sin(np.pi * x), torch.cos(np.pi * x)], dim=-1)
        return self.network(expanded).squeeze(-1)


class QNNNucleus:
    """Bridge the Cerebrum feature bundle to quantum/classical candidates."""

    QISKIT_QUBITS = 4
    DEFAULT_SEED = 42

    def __init__(self, adapter: Optional[CerebrumAdapter] = None):
        self.adapter = adapter or CerebrumAdapter()
        self._surrogate: Optional[_SurrogateQuantumNet] = None
        self._qiskit_model: Optional[torch.nn.Module] = None

    def candidate_matrix(self) -> List[QNNCandidate]:
        return [
            QNNCandidate(
                name="qiskit_estimator_qnn",
                role="primary",
                available=QISKIT_AVAILABLE,
                backend="qiskit-machine-learning",
                notes="Preferred target for the real QNN path.",
            ),
            QNNCandidate(
                name="qiskit_torchconnector_qnn",
                role="hybrid",
                available=QISKIT_AVAILABLE,
                backend="qiskit + torch",
                notes="Hybrid training path for a PyTorch workflow.",
            ),
            QNNCandidate(
                name="torchquantum_qnn",
                role="alternative",
                available=self._module_available("torchquantum"),
                backend="torchquantum",
                notes="Secondary candidate if the package is installed later.",
            ),
            QNNCandidate(
                name="quanvolution_baseline",
                role="baseline",
                available=QISKIT_AVAILABLE,
                backend="qiskit-machine-learning",
                notes="Useful as an image-patch or quanvolution comparison baseline.",
            ),
            QNNCandidate(
                name="torch_surrogate",
                role="fallback",
                available=True,
                backend="torch",
                notes="Deterministic local fallback so the repo remains runnable.",
            ),
        ]

    def smoke_run(
        self,
        raw_events: Iterable[Any],
        label: float = 1.0,
        max_epochs: int = 12,
        test_size: float = 0.0,
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_hook_enabled: bool = False,
        plugin_set: str = "mvp5",
        plugin_context: Optional[Dict[str, Any]] = None,
        cpai_context: Optional[Dict[str, Any]] = None,
        include_plugin_trace: bool = True,
        plithogenic_features: Optional[Sequence[float]] = None,
        plithogenic_payload: Optional[Dict[str, Any]] = None,
        revolutionary_topology_features: Optional[Sequence[float]] = None,
        revolutionary_topology_payload: Optional[Dict[str, Any]] = None,
        plithogenic_topology_features: Optional[Sequence[float]] = None,
        plithogenic_topology_payload: Optional[Dict[str, Any]] = None,
        neutro_algebra_features: Optional[Sequence[float]] = None,
        neutro_algebra_payload: Optional[Dict[str, Any]] = None,
        precomputed_plugin_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raw_events = list(raw_events)
        plugin_payload = precomputed_plugin_payload
        if plugin_payload is None:
            plugin_payload = self._plugin_hook_payload(
                raw_events,
                enabled=plugin_hook_enabled,
                plugin_set=plugin_set,
                plugin_context=plugin_context,
                cpai_context=cpai_context,
                include_plugin_trace=include_plugin_trace,
            )
        external_features = list(plugin_payload.get("feature_vector", [])) if plugin_payload is not None else []
        external_features.extend(list(plithogenic_features or []))
        external_features.extend(list(revolutionary_topology_features or []))
        external_features.extend(list(plithogenic_topology_features or []))
        external_features.extend(list(neutro_algebra_features or []))
        plugin_kwargs = {
            "plugin_features": external_features or None,
            "plugin_payload": plugin_payload,
        }
        fractal_kwargs = {
            "fractal_dimension": fractal_dimension,
            "fractal_dimension_min": fractal_dimension_min,
            "fractal_dimension_max": fractal_dimension_max,
            "fractal_admissible": fractal_admissible,
            "fractal_measurement_method": fractal_measurement_method,
            "fractal_scale": fractal_scale,
        }
        if QISKIT_AVAILABLE:
            try:
                result = self.fit_qiskit_hybrid(
                    [raw_events],
                    [int(label)],
                    max_epochs=max_epochs,
                    test_size=test_size,
                    state_basis=state_basis,
                    puncture_delta=puncture_delta,
                    observer_strength=observer_strength,
                    **plugin_kwargs,
                    **fractal_kwargs,
                )
                self._attach_plithogenic_payload(result, plithogenic_payload)
                self._attach_revolutionary_topology_payload(result, revolutionary_topology_payload)
                self._attach_plithogenic_topology_payload(result, plithogenic_topology_payload)
                self._attach_neutro_algebra_payload(result, neutro_algebra_payload)
                return result
            except Exception as exc:  # pragma: no cover - runtime safety path
                fallback = self.fit_surrogate(
                    [raw_events],
                    [label],
                    max_epochs=max_epochs if max_epochs > 0 else 32,
                    test_size=test_size,
                    return_bundle=True,
                    state_basis=state_basis,
                    puncture_delta=puncture_delta,
                    observer_strength=observer_strength,
                    **plugin_kwargs,
                    **fractal_kwargs,
                )
                fallback["qiskit_error"] = str(exc)
                fallback["backend"] = "torch_surrogate_fallback_after_qiskit_error"
                self._attach_plithogenic_payload(fallback, plithogenic_payload)
                self._attach_revolutionary_topology_payload(fallback, revolutionary_topology_payload)
                self._attach_plithogenic_topology_payload(fallback, plithogenic_topology_payload)
                self._attach_neutro_algebra_payload(fallback, neutro_algebra_payload)
                return fallback
        result = self.fit_surrogate(
            [raw_events],
            [label],
            max_epochs=max_epochs if max_epochs > 0 else 32,
            test_size=test_size,
            return_bundle=True,
            state_basis=state_basis,
            puncture_delta=puncture_delta,
            observer_strength=observer_strength,
            **plugin_kwargs,
            **fractal_kwargs,
        )
        self._attach_plithogenic_payload(result, plithogenic_payload)
        self._attach_revolutionary_topology_payload(result, revolutionary_topology_payload)
        self._attach_plithogenic_topology_payload(result, plithogenic_topology_payload)
        self._attach_neutro_algebra_payload(result, neutro_algebra_payload)
        return result

    def benchmark(self, samples: Sequence[Sequence[Any]], labels: Sequence[int]) -> List[QNNBenchmarkResult]:
        candidate_results: List[QNNBenchmarkResult] = []
        for candidate in self.candidate_matrix():
            if candidate.name == "qiskit_estimator_qnn":
                if not candidate.available:
                    candidate_results.append(
                        QNNBenchmarkResult(
                            candidate=candidate.name,
                            available=False,
                            backend=candidate.backend,
                            notes=f"Skipped: {candidate.notes}",
                        )
                    )
                else:
                    try:
                        candidate_results.append(self._benchmark_qiskit_estimator(samples, labels))
                    except Exception as exc:  # pragma: no cover - runtime safety path
                        candidate_results.append(
                            QNNBenchmarkResult(
                                candidate=candidate.name,
                                available=False,
                                backend=candidate.backend,
                                notes=f"Qiskit estimator lane failed: {exc}",
                            )
                        )
                continue

            if candidate.name == "qiskit_torchconnector_qnn":
                if not candidate.available:
                    candidate_results.append(
                        QNNBenchmarkResult(
                            candidate=candidate.name,
                            available=False,
                            backend=candidate.backend,
                            notes=f"Skipped: {candidate.notes}",
                        )
                    )
                else:
                    try:
                        candidate_results.append(self._benchmark_qiskit_hybrid(samples, labels))
                    except Exception as exc:  # pragma: no cover - runtime safety path
                        candidate_results.append(
                            QNNBenchmarkResult(
                                candidate=candidate.name,
                                available=False,
                                backend=candidate.backend,
                                notes=f"Qiskit hybrid lane failed: {exc}",
                            )
                        )
                continue

            if candidate.name == "torch_surrogate":
                result = self._benchmark_surrogate(samples, labels)
                candidate_results.append(result)
                continue

            if not candidate.available:
                candidate_results.append(
                    QNNBenchmarkResult(
                        candidate=candidate.name,
                        available=False,
                        backend=candidate.backend,
                        notes=f"Skipped: {candidate.notes}",
                    )
                )
                continue

            candidate_results.append(
                QNNBenchmarkResult(
                    candidate=candidate.name,
                    available=True,
                    backend=candidate.backend,
                    notes="Candidate available but not explicitly benchmarked in this lane.",
                )
            )
        return candidate_results

    def fit_surrogate(
        self,
        samples: Sequence[Sequence[Any]],
        labels: Sequence[int],
        max_epochs: int = 48,
        test_size: float = 0.25,
        return_bundle: bool = False,
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_features: Optional[Sequence[float]] = None,
        plugin_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        np.random.seed(self.DEFAULT_SEED)
        torch.manual_seed(self.DEFAULT_SEED)
        if torch.cuda.is_available():  # pragma: no cover - local CPU path is expected
            torch.cuda.manual_seed_all(self.DEFAULT_SEED)
        vectors = self._vectorize_samples(
            samples,
            state_basis=state_basis,
            puncture_delta=puncture_delta,
            observer_strength=observer_strength,
            fractal_dimension=fractal_dimension,
            fractal_dimension_min=fractal_dimension_min,
            fractal_dimension_max=fractal_dimension_max,
            fractal_admissible=fractal_admissible,
            fractal_measurement_method=fractal_measurement_method,
            fractal_scale=fractal_scale,
            plugin_features=plugin_features,
        )
        fractal_carrier = self._fractal_carrier_payload(
            fractal_dimension,
            fractal_dimension_min,
            fractal_dimension_max,
            fractal_admissible,
            fractal_measurement_method,
            fractal_scale,
            domain="qnn-surrogate",
        )
        y = np.asarray(labels, dtype=np.float32)

        if len(vectors) == 1 or test_size <= 0.0:
            X_train, X_test, y_train, y_test = vectors, vectors, y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                vectors,
                y,
                test_size=test_size,
                random_state=42,
                stratify=y if len(np.unique(y)) > 1 and len(y) >= 4 else None,
            )

        model = self._surrogate_model(input_dim=X_train.shape[1])
        optimizer = torch.optim.Adam(model.parameters(), lr=0.03)
        loss_fn = nn.BCEWithLogitsLoss()

        x_train = torch.tensor(X_train, dtype=torch.float32)
        y_train_tensor = torch.tensor(y_train, dtype=torch.float32)

        model.train()
        for _ in range(max_epochs):
            optimizer.zero_grad()
            logits = model(x_train)
            loss = loss_fn(logits, y_train_tensor)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            train_logits = model(torch.tensor(X_train, dtype=torch.float32)).cpu().numpy()
            test_logits = model(torch.tensor(X_test, dtype=torch.float32)).cpu().numpy()
            train_prob = self._sigmoid(train_logits)
            test_prob = self._sigmoid(test_logits)

        train_pred = (train_prob >= 0.5).astype(int)
        test_pred = (test_prob >= 0.5).astype(int)
        result = {
            "backend": "torch_surrogate",
            "feature_dimension": int(X_train.shape[1]),
            "train_accuracy": float(accuracy_score(y_train, train_pred)),
            "test_accuracy": float(accuracy_score(y_test, test_pred)),
            "predicted_probability": float(test_prob[-1] if len(test_prob) else train_prob[-1]),
            "feature_vector": vectors[-1].tolist(),
            "bundle_summary": self.adapter.build_bundle(samples[-1]).summary,
            "state_basis": state_basis,
            "puncture_delta": puncture_delta,
            "observer_strength": observer_strength,
            "fractal_carrier": fractal_carrier,
            "i_fractal_candidate": None if fractal_carrier is None else fractal_carrier["i_fractal_candidate"],
        }
        self._attach_plugin_payload(result, plugin_payload)

        self._surrogate = model
        if return_bundle:
            result["bundle"] = self.adapter.build_bundle(samples[-1])
        return result

    def fit_qiskit_hybrid(
        self,
        samples: Sequence[Sequence[Any]],
        labels: Sequence[int],
        max_epochs: int = 18,
        test_size: float = 0.25,
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_features: Optional[Sequence[float]] = None,
        plugin_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Qiskit Machine Learning is not installed in this environment")

        vectors = self._vectorize_samples(
            samples,
            target_dim=self.QISKIT_QUBITS,
            state_basis=state_basis,
            puncture_delta=puncture_delta,
            observer_strength=observer_strength,
            fractal_dimension=fractal_dimension,
            fractal_dimension_min=fractal_dimension_min,
            fractal_dimension_max=fractal_dimension_max,
            fractal_admissible=fractal_admissible,
            fractal_measurement_method=fractal_measurement_method,
            fractal_scale=fractal_scale,
            plugin_features=plugin_features,
        )
        fractal_carrier = self._fractal_carrier_payload(
            fractal_dimension,
            fractal_dimension_min,
            fractal_dimension_max,
            fractal_admissible,
            fractal_measurement_method,
            fractal_scale,
            domain="qnn-qiskit-hybrid",
        )
        y = np.asarray(labels, dtype=np.float32)

        if len(vectors) == 1 or test_size <= 0.0:
            X_train, X_test, y_train, y_test = vectors, vectors, y, y
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                vectors,
                y,
                test_size=test_size,
                random_state=42,
                stratify=y if len(np.unique(y)) > 1 and len(y) >= 4 else None,
            )

        model, qnn, initial_weights = self._build_qiskit_hybrid_model(self.QISKIT_QUBITS)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.04)
        loss_fn = nn.MSELoss()

        x_train = torch.tensor(X_train, dtype=torch.float32)
        y_train_tensor = torch.tensor(y_train, dtype=torch.float32)

        model.train()
        for _ in range(max_epochs):
            optimizer.zero_grad()
            probabilities = self._probability_from_qnn_output(model(x_train).squeeze())
            loss = loss_fn(probabilities, y_train_tensor)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            train_prob = self._probability_from_qnn_output(model(torch.tensor(X_train, dtype=torch.float32)).squeeze()).cpu().numpy()
            test_prob = self._probability_from_qnn_output(model(torch.tensor(X_test, dtype=torch.float32)).squeeze()).cpu().numpy()

        train_pred = (train_prob >= 0.5).astype(int)
        test_pred = (test_prob >= 0.5).astype(int)
        result = {
            "backend": "qiskit_torchconnector",
            "feature_dimension": int(X_train.shape[1]),
            "train_accuracy": float(accuracy_score(y_train, train_pred)),
            "test_accuracy": float(accuracy_score(y_test, test_pred)),
            "predicted_probability": float(test_prob[-1] if len(test_prob) else train_prob[-1]),
            "feature_vector": vectors[-1].tolist(),
            "bundle_summary": self.adapter.build_bundle(samples[-1]).summary,
            "initial_weights": initial_weights.detach().cpu().numpy().tolist(),
            "qiskit_num_weights": int(qnn.num_weights),
            "state_basis": state_basis,
            "puncture_delta": puncture_delta,
            "observer_strength": observer_strength,
            "fractal_carrier": fractal_carrier,
            "i_fractal_candidate": None if fractal_carrier is None else fractal_carrier["i_fractal_candidate"],
        }
        self._attach_plugin_payload(result, plugin_payload)
        self._qiskit_model = model
        return result

    def encode_sample(
        self,
        raw_events: Sequence[Any],
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_features: Optional[Sequence[float]] = None,
    ) -> np.ndarray:
        bundle = self.adapter.build_bundle(raw_events)
        base_vector = self.adapter.bundle_to_vector(bundle)
        return self._quantum_style_encoding(
            base_vector,
            state_basis=state_basis,
            puncture_delta=puncture_delta,
            observer_strength=observer_strength,
            fractal_dimension=fractal_dimension,
            fractal_dimension_min=fractal_dimension_min,
            fractal_dimension_max=fractal_dimension_max,
            fractal_admissible=fractal_admissible,
            fractal_measurement_method=fractal_measurement_method,
            fractal_scale=fractal_scale,
            plugin_features=plugin_features,
        )

    def _benchmark_surrogate(self, samples: Sequence[Sequence[Any]], labels: Sequence[int]) -> QNNBenchmarkResult:
        outcome = self.fit_surrogate(samples, labels, max_epochs=36, test_size=0.25)
        return QNNBenchmarkResult(
            candidate="torch_surrogate",
            available=True,
            backend="torch",
            notes="Operational fallback benchmark completed.",
            train_accuracy=outcome["train_accuracy"],
            test_accuracy=outcome["test_accuracy"],
            predicted_probability=outcome["predicted_probability"],
            feature_dimension=outcome["feature_dimension"],
        )

    def _benchmark_qiskit_estimator(
        self, samples: Sequence[Sequence[Any]], labels: Sequence[int]
    ) -> QNNBenchmarkResult:
        vectors = self._vectorize_samples(samples, target_dim=self.QISKIT_QUBITS)
        qnn, initial_weights = self._build_qiskit_estimator(self.QISKIT_QUBITS)
        outputs = np.asarray(
            qnn.forward(vectors, initial_weights.detach().cpu().numpy()),
            dtype=np.float32,
        ).reshape(-1)
        probabilities = self._probability_from_qnn_output(outputs).cpu().numpy()
        predictions = (probabilities >= 0.5).astype(int)
        accuracy = float(accuracy_score(labels, predictions))
        return QNNBenchmarkResult(
            candidate="qiskit_estimator_qnn",
            available=True,
            backend="qiskit-machine-learning",
            notes="Zero-shot EstimatorQNN forward pass completed.",
            train_accuracy=accuracy,
            test_accuracy=accuracy,
            predicted_probability=float(probabilities[-1] if len(probabilities) else 0.5),
            feature_dimension=int(vectors.shape[1]),
        )

    def _benchmark_qiskit_hybrid(
        self, samples: Sequence[Sequence[Any]], labels: Sequence[int]
    ) -> QNNBenchmarkResult:
        outcome = self.fit_qiskit_hybrid(samples, labels, max_epochs=10, test_size=0.25)
        return QNNBenchmarkResult(
            candidate="qiskit_torchconnector_qnn",
            available=True,
            backend=outcome["backend"],
            notes="Hybrid TorchConnector training completed.",
            train_accuracy=outcome["train_accuracy"],
            test_accuracy=outcome["test_accuracy"],
            predicted_probability=outcome["predicted_probability"],
            feature_dimension=outcome["feature_dimension"],
        )

    def _build_qiskit_estimator(self, num_qubits: int) -> Tuple[EstimatorQNN, torch.Tensor]:
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Qiskit Machine Learning is not installed in this environment")

        feature_map = ZZFeatureMap(num_qubits, reps=1)
        ansatz = RealAmplitudes(num_qubits, reps=1, entanglement="linear")
        circuit = QuantumCircuit(num_qubits)
        circuit.compose(feature_map, inplace=True)
        circuit.compose(ansatz, inplace=True)

        qnn = EstimatorQNN(
            circuit=circuit,
            estimator=Estimator(),
            input_params=list(feature_map.parameters),
            weight_params=list(ansatz.parameters),
            input_gradients=True,
        )
        if qnn.num_weights <= 0:
            raise RuntimeError("Qiskit QNN produced no trainable weights")
        initial_weights = torch.linspace(-0.2, 0.2, steps=qnn.num_weights, dtype=torch.float32)
        return qnn, initial_weights

    def _build_qiskit_hybrid_model(self, num_qubits: int) -> Tuple[nn.Module, EstimatorQNN, torch.Tensor]:
        qnn, initial_weights = self._build_qiskit_estimator(num_qubits)
        model = TorchConnector(qnn, initial_weights=initial_weights)
        return model, qnn, initial_weights

    def _surrogate_model(self, input_dim: int) -> _SurrogateQuantumNet:
        if self._surrogate is None or self._surrogate.network[0].in_features != input_dim * 3:
            self._surrogate = _SurrogateQuantumNet(input_dim=input_dim)
        return self._surrogate

    def _vectorize_samples(
        self,
        samples: Sequence[Sequence[Any]],
        target_dim: Optional[int] = None,
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_features: Optional[Sequence[float]] = None,
    ) -> np.ndarray:
        vectors = [
            self.encode_sample(
                sample,
                state_basis=state_basis,
                puncture_delta=puncture_delta,
                observer_strength=observer_strength,
                fractal_dimension=fractal_dimension,
                fractal_dimension_min=fractal_dimension_min,
                fractal_dimension_max=fractal_dimension_max,
                fractal_admissible=fractal_admissible,
                fractal_measurement_method=fractal_measurement_method,
                fractal_scale=fractal_scale,
                plugin_features=plugin_features,
            )
            for sample in samples
        ]
        matrix = np.asarray(vectors, dtype=np.float32)
        if target_dim is None:
            return matrix
        reduced = [self._compact_vector(vector, target_dim) for vector in matrix]
        return np.asarray(reduced, dtype=np.float32)

    def _compact_vector(self, vector: np.ndarray, target_dim: int) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32).reshape(-1)
        if target_dim <= 0:
            raise ValueError("target_dim must be positive")
        if vector.size == 0:
            return np.zeros(target_dim, dtype=np.float32)
        if vector.size == target_dim:
            return vector
        if vector.size < target_dim:
            return np.pad(vector, (0, target_dim - vector.size), mode="constant").astype(np.float32)

        chunks = np.array_split(vector, target_dim)
        compact = [float(chunk.mean()) if chunk.size else 0.0 for chunk in chunks]
        return np.asarray(compact, dtype=np.float32)

    def _quantum_style_encoding(
        self,
        vector: np.ndarray,
        state_basis: str = "binary",
        puncture_delta: Optional[float] = None,
        observer_strength: Optional[float] = None,
        fractal_dimension: Optional[float] = None,
        fractal_dimension_min: Optional[float] = None,
        fractal_dimension_max: Optional[float] = None,
        fractal_admissible: bool = True,
        fractal_measurement_method: Optional[str] = None,
        fractal_scale: Optional[str] = None,
        plugin_features: Optional[Sequence[float]] = None,
    ) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32)
        if vector.size == 0:
            return np.zeros(1, dtype=np.float32)
        base = np.tanh(vector)
        fourier = np.sin(np.pi * vector)
        envelope = np.cos(np.pi * vector)
        encoded = np.concatenate([base, fourier, envelope]).astype(np.float32)
        plugin_array = np.asarray(list(plugin_features or []), dtype=np.float32).reshape(-1)
        if state_basis == "binary":
            return np.concatenate([encoded, plugin_array]).astype(np.float32) if plugin_array.size else encoded
        if state_basis != "neutrobit":
            raise ValueError("state_basis must be 'binary' or 'neutrobit'")
        neutrobit_features = neutrobit_features_from_vector(
            encoded,
            puncture_delta=puncture_delta,
            observer_strength=observer_strength,
            fractal_dimension=fractal_dimension,
            fractal_dimension_min=fractal_dimension_min,
            fractal_dimension_max=fractal_dimension_max,
            fractal_admissible=fractal_admissible,
            fractal_measurement_method=fractal_measurement_method,
            fractal_scale=fractal_scale,
        )
        parts = [encoded, neutrobit_features]
        if plugin_array.size:
            parts.append(plugin_array)
        return np.concatenate(parts).astype(np.float32)

    def _plugin_hook_payload(
        self,
        raw_events: Sequence[Any],
        *,
        enabled: bool,
        plugin_set: str,
        plugin_context: Optional[Dict[str, Any]],
        cpai_context: Optional[Dict[str, Any]],
        include_plugin_trace: bool,
    ) -> Optional[Dict[str, Any]]:
        if not enabled:
            return None
        context = dict(plugin_context or {})
        context.setdefault("events", raw_events)
        context.setdefault("cpai_context", dict(cpai_context or {}))
        return FfeDPluginBridge().run_mvp5(
            context,
            include_trace=include_plugin_trace,
            plugin_set=plugin_set,
        )

    def _attach_plugin_payload(self, result: Dict[str, Any], plugin_payload: Optional[Dict[str, Any]]) -> None:
        if not plugin_payload:
            return
        for key in (
            "plugin_fractal_signals",
            "plugin_fractal_carrier",
            "plugin_tension_profile",
            "plugin_gate_profile",
            "plugin_gate_trace",
            "plugin_errors",
            "plugin_hook_status",
            "cpai_mesh_profile",
            "impact_verification",
        ):
            result[key] = plugin_payload.get(key)

    def _attach_plithogenic_payload(self, result: Dict[str, Any], plithogenic_payload: Optional[Dict[str, Any]]) -> None:
        if not plithogenic_payload:
            return
        result["plithogenic_fusion_profile"] = {
            "model": plithogenic_payload["model"],
            "feature_vector": plithogenic_payload["feature_vector"],
            "feature_dimension": plithogenic_payload["feature_dimension"],
            "cumulative_truth": plithogenic_payload["cumulative_truth"],
            "weighted_cumulative_truth": plithogenic_payload["weighted_cumulative_truth"],
            "contradiction_summary": plithogenic_payload["contradiction_summary"],
            "hierarchy": plithogenic_payload["hierarchy"],
        }

    def _attach_revolutionary_topology_payload(
        self,
        result: Dict[str, Any],
        revolutionary_topology_payload: Optional[Dict[str, Any]],
    ) -> None:
        if not revolutionary_topology_payload:
            return
        result["revolutionary_topology_profile"] = {
            "model": revolutionary_topology_payload["model"],
            "feature_vector": revolutionary_topology_payload["feature_vector"],
            "feature_dimension": revolutionary_topology_payload["feature_dimension"],
            "topological_axiom_profile": revolutionary_topology_payload["topological_axiom_profile"],
            "deformation_signature": revolutionary_topology_payload["deformation_signature"],
            "hierarchy": revolutionary_topology_payload["hierarchy"],
        }

    def _attach_plithogenic_topology_payload(
        self,
        result: Dict[str, Any],
        plithogenic_topology_payload: Optional[Dict[str, Any]],
    ) -> None:
        if not plithogenic_topology_payload:
            return
        result["plithogenic_topology_profile"] = {
            "model": plithogenic_topology_payload["model"],
            "feature_vector": plithogenic_topology_payload["feature_vector"],
            "feature_dimension": plithogenic_topology_payload["feature_dimension"],
            "deterministic_decision": plithogenic_topology_payload["deterministic_decision"],
            "deterministic_confidence": plithogenic_topology_payload["deterministic_confidence"],
            "statistical_confidence": plithogenic_topology_payload["statistical_confidence"],
            "topology_variable_completion": plithogenic_topology_payload["topology_variable_completion"],
            "hierarchy": plithogenic_topology_payload["hierarchy"],
        }
        if "plugin_stabilization_profile" in plithogenic_topology_payload:
            result["plithogenic_topology_profile"]["plugin_stabilization_profile"] = plithogenic_topology_payload[
                "plugin_stabilization_profile"
            ]
            result["plithogenic_topology_profile"]["plithogenic_topology_load_profile"] = plithogenic_topology_payload[
                "plithogenic_topology_load_profile"
            ]
            result["plithogenic_topology_profile"]["stabilized_feature_vector"] = plithogenic_topology_payload[
                "stabilized_feature_vector"
            ]
            result["plithogenic_topology_profile"]["stabilized_feature_dimension"] = plithogenic_topology_payload[
                "stabilized_feature_dimension"
            ]

    def _attach_neutro_algebra_payload(
        self,
        result: Dict[str, Any],
        neutro_algebra_payload: Optional[Dict[str, Any]],
    ) -> None:
        if not neutro_algebra_payload:
            return
        result["neutro_algebra_profile"] = {
            "model": neutro_algebra_payload["model"],
            "classification": neutro_algebra_payload["classification"],
            "feature_vector": neutro_algebra_payload["feature_vector"],
            "feature_dimension": neutro_algebra_payload["feature_dimension"],
            "runtime_mapping": neutro_algebra_payload["runtime_mapping"],
            "hierarchy": neutro_algebra_payload["hierarchy"],
        }
        neutro_structure_payload = neutro_algebra_payload.get("structure_system_profile")
        if neutro_structure_payload:
            result["neutro_algebra_profile"]["structure_system_profile"] = neutro_structure_payload
            result["neutro_structure_profile"] = {
                "model": neutro_structure_payload["model"],
                "T_system": neutro_structure_payload["T_system"],
                "I_system": neutro_structure_payload["I_system"],
                "F_system": neutro_structure_payload["F_system"],
                "system_classification": neutro_structure_payload["system_classification"],
                "feature_vector": neutro_structure_payload["feature_vector"],
                "feature_dimension": neutro_structure_payload["feature_dimension"],
                "runtime_mapping": neutro_structure_payload["runtime_mapping"],
                "hierarchy": neutro_structure_payload["hierarchy"],
            }

    def _fractal_carrier_payload(
        self,
        fractal_dimension: Optional[float],
        fractal_dimension_min: Optional[float],
        fractal_dimension_max: Optional[float],
        fractal_admissible: bool,
        fractal_measurement_method: Optional[str],
        fractal_scale: Optional[str],
        domain: str,
    ) -> Optional[Dict[str, Any]]:
        if fractal_dimension is None or fractal_dimension_min is None or fractal_dimension_max is None:
            return None
        return fractal_carrier_profile(
            fractal_dimension,
            fractal_dimension_min,
            fractal_dimension_max,
            measurement_method=fractal_measurement_method or "provided-fractal-dimension",
            scale=fractal_scale,
            domain=domain,
            admissible=fractal_admissible,
        )

    def _module_available(self, module_name: str) -> bool:
        try:
            __import__(module_name)
            return True
        except Exception:
            return False

    def _sigmoid(self, values: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-values))

    def _probability_from_qnn_output(self, values: Any) -> torch.Tensor:
        tensor = torch.as_tensor(values, dtype=torch.float32)
        return torch.clamp((tensor + 1.0) / 2.0, 0.0, 1.0)

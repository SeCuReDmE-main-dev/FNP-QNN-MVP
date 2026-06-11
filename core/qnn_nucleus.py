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

try:  # Optional Qiskit path. The repo should still run without it.
    from qiskit_machine_learning.circuit.library import QNNCircuit
    from qiskit_machine_learning.connectors import TorchConnector
    from qiskit_machine_learning.neural_networks import EstimatorQNN
    from qiskit.primitives import Estimator

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

    def smoke_run(self, raw_events: Iterable[Any], label: float = 1.0) -> Dict[str, Any]:
        if QISKIT_AVAILABLE:
            return self.fit_qiskit_hybrid([raw_events], [int(label)], max_epochs=12, test_size=0.0)
        return self.fit_surrogate([raw_events], [label], max_epochs=32, test_size=0.0, return_bundle=True)

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
                    candidate_results.append(self._benchmark_qiskit_estimator(samples))
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
                    candidate_results.append(self._benchmark_qiskit_hybrid(samples, labels))
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
    ) -> Dict[str, Any]:
        vectors = self._vectorize_samples(samples)
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
        }

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
    ) -> Dict[str, Any]:
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Qiskit Machine Learning is not installed in this environment")

        vectors = self._vectorize_samples(samples, target_dim=self.QISKIT_QUBITS)
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
        loss_fn = nn.BCEWithLogitsLoss()

        x_train = torch.tensor(X_train, dtype=torch.float32)
        y_train_tensor = torch.tensor(y_train, dtype=torch.float32)

        model.train()
        for _ in range(max_epochs):
            optimizer.zero_grad()
            logits = model(x_train).squeeze()
            loss = loss_fn(logits, y_train_tensor)
            loss.backward()
            optimizer.step()

        model.eval()
        with torch.no_grad():
            train_logits = model(torch.tensor(X_train, dtype=torch.float32)).squeeze().cpu().numpy()
            test_logits = model(torch.tensor(X_test, dtype=torch.float32)).squeeze().cpu().numpy()
            train_prob = self._sigmoid(train_logits)
            test_prob = self._sigmoid(test_logits)

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
        }
        self._qiskit_model = model
        return result

    def encode_sample(self, raw_events: Sequence[Any]) -> np.ndarray:
        bundle = self.adapter.build_bundle(raw_events)
        base_vector = self.adapter.bundle_to_vector(bundle)
        return self._quantum_style_encoding(base_vector)

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

    def _surrogate_model(self, input_dim: int) -> _SurrogateQuantumNet:
        if self._surrogate is None or self._surrogate.network[0].in_features != input_dim * 3:
            self._surrogate = _SurrogateQuantumNet(input_dim=input_dim)
        return self._surrogate

    def _vectorize_samples(self, samples: Sequence[Sequence[Any]]) -> np.ndarray:
        vectors = [self.encode_sample(sample) for sample in samples]
        return np.asarray(vectors, dtype=np.float32)

    def _quantum_style_encoding(self, vector: np.ndarray) -> np.ndarray:
        vector = np.asarray(vector, dtype=np.float32)
        if vector.size == 0:
            return np.zeros(1, dtype=np.float32)
        base = np.tanh(vector)
        fourier = np.sin(np.pi * vector)
        envelope = np.cos(np.pi * vector)
        return np.concatenate([base, fourier, envelope]).astype(np.float32)

    def _module_available(self, module_name: str) -> bool:
        try:
            __import__(module_name)
            return True
        except Exception:
            return False

    def _sigmoid(self, values: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-values))

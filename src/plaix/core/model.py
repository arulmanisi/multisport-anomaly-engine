"""Model wrapper design for anomaly-focused prediction (no implementation)."""

from __future__ import annotations

from typing import Any, Dict, Optional


class AnomalyModel:
    """Framework-agnostic model wrapper for anomaly detection.

    Designed to handle UPS Score (Unexpected Performance Spike) and other anomaly labels,
    supporting binary anomaly targets and score-based outputs. This class is sport- and
    task-aware via config, but does not commit to a specific ML library.
    """

    def __init__(self, model_type: str, model_config: Optional[Dict[str, Any]] = None, sport: Optional[str] = None):
        """
        Initialize the model wrapper.

        Args:
            model_type: identifier for backend (e.g., "random_forest", "gradient_boosting", "isolation_forest").
            model_config: hyperparameters for the chosen backend.
            sport: optional sport identifier for multi-sport setups.
        """
        self.model_type = model_type
        self.model_config = model_config or {}
        self.sport = sport
        # TODO: instantiate the actual model backend based on model_type and model_config.

    def fit(self, X: Any, y: Any) -> None:
        """
        Train the model on features and labels.

        Args:
            X: feature matrix/structure (e.g., dataframe, array).
            y: labels, expected to include anomaly targets (binary or score-based, e.g., UPS Score).
        """
        # TODO: delegate to backend model's fit.
        raise NotImplementedError

    def predict(self, X: Any) -> Any:
        """
        Predict anomaly labels (binary or score-based).

        Args:
            X: feature matrix/structure.
        Returns:
            Predictions aligned to the anomaly task (e.g., UPS binary labels or scores).
        """
        # TODO: delegate to backend model's predict.
        raise NotImplementedError

    def predict_proba(self, X: Any) -> Any:
        """
        Predict class probabilities or anomaly scores where applicable.

        Args:
            X: feature matrix/structure.
        Returns:
            Probabilities or scores (for detectors that support it).
        Notes:
            - Some anomaly detectors output scores rather than probabilities.
            - Implement conditional support depending on backend capabilities.
        """
        # TODO: delegate to backend model's predict_proba or equivalent anomaly scoring.
        raise NotImplementedError

    def save_model(self, path: str) -> None:
        """
        Persist the trained model to disk.

        Args:
            path: destination path for the serialized model artifact.
        Notes:
            - Keep serialization backend flexible (pickle/joblib/onnx) depending on model_type.
        """
        # TODO: implement model serialization strategy.
        raise NotImplementedError

    def load_model(self, path: str) -> None:
        """
        Load a model from disk.

        Args:
            path: source path of the serialized model artifact.
        Notes:
            - Should restore the model in a ready-to-predict state.
        """
        # TODO: implement model deserialization strategy.
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"AnomalyModel(type={self.model_type}, sport={self.sport}, config={self.model_config})"


# Notes for extension:
# - Add factory functions to create specific backends (e.g., tree ensembles, isolation forests).
# - Add support for calibration layers if probability outputs are required.
# - Add multi-task support when multiple anomaly labels (e.g., UPS, momentum shift) are predicted jointly.

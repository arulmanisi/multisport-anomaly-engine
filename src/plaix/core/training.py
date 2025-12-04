"""Training engine design wiring pipeline and model (structure only)."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from plaix.core.model import AnomalyModel
from plaix.core.pipeline import DataPipeline


class TrainingEngine:
    """Anomaly-focused training/evaluation orchestrator."""

    def __init__(self, data_pipeline: DataPipeline, model_wrapper: AnomalyModel, config: Dict[str, Any]) -> None:
        """
        Initialize the training engine.

        Args:
            data_pipeline: orchestrates load/clean/features/labels/splits.
            model_wrapper: anomaly-aware model wrapper (UPS Score, anomaly labels).
            config: configuration dict (hyperparameters, paths, evaluation settings).
        """
        self.data_pipeline = data_pipeline
        self.model_wrapper = model_wrapper
        self.config = config
        # TODO: wire in logger/telemetry if needed.

    def run_training(self) -> Tuple[Any, Any]:
        """
        Execute training workflow.

        Steps:
            - Use data_pipeline to produce (X, y) and train/validation split.
            - Fit model_wrapper on training data.
        Returns:
            Trained model and validation data (X_val, y_val) for downstream evaluation.
        Input/Output shapes:
            X_train, y_train tailored to anomaly labels (e.g., UPS Score, binary anomaly flags).
            Supports extension to multi-label anomaly targets in the future.
        """
        # TODO: call pipeline.load_raw_data/clean/features/labels/assemble_dataset/train_validation_split
        # TODO: call model_wrapper.fit(X_train, y_train)
        # TODO: return model and validation sets.
        raise NotImplementedError

    def run_evaluation(self, X_val: Any, y_val: Any) -> Dict[str, Any]:
        """
        Evaluate model on validation data.

        Steps (design only):
            - model_wrapper.predict / predict_proba on X_val.
            - Compute anomaly-relevant metrics:
                * precision/recall for anomalous cases (e.g., UPS positives)
                * PR-AUC for anomaly detection
                * recall at fixed false positive rate
            - Support multiple labels (binary anomaly + score-based labels) in future.
        Returns:
            Dict of metric_name -> metric_value (placeholders for now).
        """
        # TODO: implement prediction and metric computation when backend is chosen.
        raise NotImplementedError

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Log evaluation metrics.

        Args:
            metrics: dict of metric_name -> value.
        Notes:
            - Placeholder for console logging or external telemetry (e.g., MLflow).
        """
        # TODO: implement logging.
        raise NotImplementedError

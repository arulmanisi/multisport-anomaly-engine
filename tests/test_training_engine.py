from typing import Any, Dict, Tuple

from plaix.core.model import AnomalyModel
from plaix.core.training import TrainingEngine


class StubPipeline:
    def __init__(self):
        self.split_called = False

    def assemble_dataset(self, features, labels):
        return features, labels

    def train_validation_split(self, dataset, test_size: float = 0.2, shuffle: bool = True):
        self.split_called = True
        X, y = dataset
        return X, X, y, y

    def load_raw_data(self, source: Any) -> Any:
        return source

    def clean(self, raw_data: Any) -> Any:
        return raw_data

    def generate_features(self, cleaned_data: Any):
        return {"X": cleaned_data}

    def generate_labels(self, cleaned_data: Any):
        return {"y": cleaned_data}


class StubModel(AnomalyModel):
    def __init__(self):
        super().__init__(model_type="logistic_regression", model_config={}, sport="cricket")
        self.model = DummyBackend()
        self.fit_called = False
        self.predict_called = False

    def fit(self, X: Any, y: Any) -> None:
        self.fit_called = True

    def predict(self, X: Any) -> Any:
        self.predict_called = True
        return [0 for _ in range(len(X))]

    def predict_proba(self, X: Any) -> Any:
        return None

    def save_model(self, path: str) -> None:
        return None

    def load_model(self, path: str) -> None:
        return None


class DummyBackend:
    def __init__(self):
        self.fitted = False

    def fit(self, X: Any, y: Any) -> None:
        self.fitted = True

    def predict(self, X: Any) -> Any:
        return [0 for _ in range(len(X))]


class StubTrainingEngine(TrainingEngine):
    def run_training(self):
        raw = self.data_pipeline.load_raw_data("src")
        cleaned = self.data_pipeline.clean(raw)
        feats = self.data_pipeline.generate_features(cleaned)
        labs = self.data_pipeline.generate_labels(cleaned)
        dataset = self.data_pipeline.assemble_dataset(feats, labs)
        X_train, X_val, y_train, y_val = self.data_pipeline.train_validation_split(dataset)
        self.model_wrapper.fit(X_train, y_train)
        return X_val, y_val

    def run_evaluation(self, X_val, y_val):
        preds = self.model_wrapper.predict(X_val)
        # TODO: compute real metrics like precision/recall/PR-AUC
        return {"preds": preds, "y_true": y_val}

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        # TODO: integrate with logger/telemetry
        return None


def test_training_engine_flow() -> None:
    pipeline = StubPipeline()
    model = StubModel()
    engine = StubTrainingEngine(pipeline, model, config={})

    X_val, y_val = engine.run_training()
    metrics = engine.run_evaluation(X_val, y_val)
    engine.log_metrics(metrics)

    assert pipeline.split_called is True
    assert model.fit_called is True
    assert model.predict_called is True
    assert "preds" in metrics

from typing import Any

from plaix.core.model import AnomalyModel


class DummyBackend:
    def __init__(self):
        self.fitted = False

    def fit(self, X: Any, y: Any) -> None:
        self.fitted = True

    def predict(self, X: Any) -> Any:
        return [0 for _ in range(len(X))]

    def predict_proba(self, X: Any) -> Any:
        return [[0.1, 0.9] for _ in range(len(X))]


class FakeModel(AnomalyModel):
    def __init__(self):
        super().__init__(model_type="logistic_regression", model_config={}, sport="cricket")
        self.model = DummyBackend()
        self.fitted = False

    def fit(self, X: Any, y: Any) -> None:
        self.fitted = True
        self.model.fit(X, y)

    def predict(self, X: Any) -> Any:
        return self.model.predict(X)

    def predict_proba(self, X: Any) -> Any:
        return self.model.predict_proba(X)


def test_model_fit_and_predict() -> None:
    model = FakeModel()
    X = [[1], [2]]
    y = [0, 1]

    model.fit(X, y)
    preds = model.predict(X)
    probas = model.predict_proba(X)

    assert model.fitted is True
    assert preds == [0, 0]
    assert len(probas) == 2
    assert probas[0][1] == 0.9


def test_model_save_and_load_callable() -> None:
    model = FakeModel()
    model.save_model("path")
    model.load_model("path")

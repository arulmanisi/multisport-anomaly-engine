from typing import Any, Dict, Tuple

from plaix.core.pipeline import DataPipeline


class FakePipeline(DataPipeline):
    def __init__(self):
        super().__init__(data_loader=self._load, cleaner=self._clean, feature_extractor=None, label_creator=None)

    def _load(self, source: Any) -> Any:
        return {"raw": source}

    def _clean(self, raw_data: Any) -> Any:
        return {"clean": raw_data["raw"]}

    def load_raw_data(self, source: Any) -> Any:
        return self.data_loader(source)

    def clean(self, raw_data: Any) -> Any:
        return self.cleaner(raw_data)

    def generate_features(self, cleaned_data: Any) -> Dict[str, Any]:
        return {"features": cleaned_data}

    def generate_labels(self, cleaned_data: Any):
        return {"labels": cleaned_data}

    def assemble_dataset(self, features: Dict[str, Any], labels: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        return features, labels

    def train_validation_split(self, dataset, test_size: float = 0.2, shuffle: bool = True):
        X, y = dataset
        return X, X, y, y


def test_pipeline_flow() -> None:
    pipeline = FakePipeline()
    raw = pipeline.load_raw_data("source")
    cleaned = pipeline.clean(raw)
    feats = pipeline.generate_features(cleaned)
    labs = pipeline.generate_labels(cleaned)
    dataset = pipeline.assemble_dataset(feats, labs)
    X_train, X_val, y_train, y_val = pipeline.train_validation_split(dataset)

    assert raw == {"raw": "source"}
    assert cleaned == {"clean": "source"}
    assert feats["features"]["clean"] == "source"
    assert y_train["labels"]["clean"] == "source"

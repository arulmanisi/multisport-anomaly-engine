import pytest

from plaix.core.labels import label_registry


def test_label_registry_register_and_get() -> None:
    def dummy_label(match_json):
        return {"ups_score": 0.0}

    label_registry.register_label("test.ups", dummy_label)

    result = label_registry.get_label_output("test.ups", {"payload": "x"})

    assert result == {"ups_score": 0.0}


def test_label_registry_unknown_label() -> None:
    with pytest.raises(KeyError):
        label_registry.get_label_output("missing.label", {})


def test_ups_label_placeholder() -> None:
    # Placeholder UPS score label function
    def ups_label(match_json):
        # TODO: compute real UPS
        return 1.23

    label_registry.register_label("cricket.ups_score.test", ups_label)
    value = label_registry.get_label_output("cricket.ups_score.test", {"foo": "bar"})

    assert isinstance(value, float)
    assert value == 1.23

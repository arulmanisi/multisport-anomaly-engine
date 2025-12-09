from plaix.utils.logger import get_logger


def test_get_logger_does_not_duplicate_handlers() -> None:
    logger1 = get_logger("plaix.test")
    logger2 = get_logger("plaix.test")

    assert logger1 is logger2
    assert len(logger1.handlers) == 1
    assert logger1.handlers[0].formatter is not None

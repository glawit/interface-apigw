import logging
import sys


def set_up(level):
    top_logger = logging.getLogger(
        name=None,
    )

    for existing_handler in top_logger.handlers:
        top_logger.removeHandler(
            existing_handler,
        )

    handler = logging.StreamHandler(
        stream=sys.stderr,
    )

    formatter = logging.Formatter(
        datefmt=None,
        fmt='%(name)s: %(levelname)s: %(message)s',
        style='%',
    )

    handler.setFormatter(
        formatter,
    )

    top_logger.addHandler(
        handler,
    )

    top_logger.setLevel(
        level,
    )

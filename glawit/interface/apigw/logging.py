import logging
import sys

# Top logger object based on whether everything should be logged
top_logger_names = {
    False: 'glawit',
    True: None,
}


def set_up(level, log_everything):
    top_logger_name = top_logger_names[log_everything]

    top_logger = logging.getLogger(
        name=top_logger_name,
    )

    top_logger.setLevel(
        level,
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

import logging
from .constants import DIRECTORY_LOGS
import sys

LOG_FILE = logging.FileHandler(DIRECTORY_LOGS)

CONSOLE_STREAM = logging.StreamHandler(sys.stdout)

LOGGING_FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

LOG_FILE.setFormatter(LOGGING_FORMATTER)
CONSOLE_STREAM.setFormatter(LOGGING_FORMATTER)

LOGGERS = {}


def get_logger(logger_id):
    global LOGGERS
    new_logger = LOGGERS.get(logger_id, None)
    if new_logger is not None:
        return new_logger

    new_logger = logging.getLogger(logger_id)
    new_logger.setLevel(logging.INFO)
    new_logger.addHandler(LOG_FILE)
    new_logger.addHandler(CONSOLE_STREAM)
    LOGGERS[logger_id] = new_logger
    return new_logger


def log(*args, level=logging.INFO, logger_id="core"):
    target_logger = get_logger(logger_id)

    msg = " ".join(list(map(str, args)))
    target_logger.log(level, msg)

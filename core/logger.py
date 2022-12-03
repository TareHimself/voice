from queue import Queue
from threading import Thread
import logging
import time
from .constants import DIRECTORY_LOGS
import sys
log_buffer = Queue()

CORE_LOGGER = logging.getLogger('core')
CORE_LOGGER.setLevel(logging.INFO)

LOG_FILE = logging.FileHandler(DIRECTORY_LOGS)

CONSOLE_STREAM = logging.StreamHandler(sys.stdout)

LOGGING_FORMATTER = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

LOG_FILE.setFormatter(LOGGING_FORMATTER)
CONSOLE_STREAM.setFormatter(LOGGING_FORMATTER)
CORE_LOGGER.addHandler(LOG_FILE)
CORE_LOGGER.addHandler(CONSOLE_STREAM)


def log(*args, level=logging.INFO):
    global CORE_LOGGER
    msg = " ".join(list(map(str, args)))
    CORE_LOGGER.log(level, msg)

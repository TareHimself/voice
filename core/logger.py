from queue import Queue
from threading import Thread
log_buffer = Queue()


def _process_log_buffer():
    while True:
        d = log_buffer.get()
        if d == None:
            return
        args, should_print = d
        if should_print:
            print(*args)


_logger_buffer_handler = Thread(
    target=_process_log_buffer, group=None, daemon=True)
_logger_buffer_handler.start()


def log(*args, print_to_screen=True):
    log_buffer.put([args, print_to_screen])

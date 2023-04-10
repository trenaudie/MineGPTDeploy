import sys
from contextlib import contextmanager


@contextmanager
def redirect_stdout_to_logger(logger):
    class LoggerWriter:
        def __init__(self, logger):
            self.logger = logger

        def write(self, message):
            if message.rstrip():
                self.logger.info(message.rstrip())

        def flush(self):
            pass

    original_stdout = sys.stdout
    sys.stdout = LoggerWriter(logger)
    try:
        yield
    finally:
        sys.stdout = original_stdout

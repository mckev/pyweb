import logging
import traceback


class Log:
    """ Log events """

    # Error level
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, filename=None):
        self._logger = logging.getLogger('myapp')
        self._logger.setLevel(logging.DEBUG)
        formatting = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
        # Ref: https://docs.python.org/3/howto/logging-cookbook.html
        self._logger_console = logging.StreamHandler()
        self._logger_console.setFormatter(formatting)
        self._logger.addHandler(self._logger_console)
        if filename:
            self._is_logged_to_file = True
            self._logger_file = logging.FileHandler(filename)
            self._logger_file.setFormatter(formatting)
            self._logger.addHandler(self._logger_file)
        else:
            self._is_logged_to_file = False

    def set_level(self, level):
        self._logger.setLevel(level)

    def log(self, msg, level=logging.INFO, print_stack=False):
        self._logger.log(level, msg)
        if print_stack:
            self._logger.log(logging.INFO, ''.join(traceback.format_stack()))

    def shutdown(self):
        self._logger.removeHandler(self._logger_console)
        if self._is_logged_to_file:
            self._logger.removeHandler(self._logger_file)
        logging.shutdown()

from datetime import datetime
from os import path


class _LogLevel:
    OFF = 0
    FATAL = 1
    ERROR = 2
    WARN = 3
    INFO = 4
    DEBUG = 5

    title = {
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARN: "WARNING",
        ERROR: "ERROR",
        FATAL: "FATAL"
    }


class Logger:

    def __init__(self, writer, location, _log_level=_LogLevel.INFO):
        self.writer = writer
        self.location = location
        self.log_level = _log_level
        self.file = "{}.log".format(datetime.now().replace(microsecond=0)).replace(":", "_")

    def __log(self, log_level, text):
        if self.log_level >= log_level:
            self.writer.append("[{}][{}]: {}\n".format(datetime.now().replace(microsecond=0),
                                                       _LogLevel.title[log_level], text),
                               path.join(self.location, self.file))

    def log_debug(self, text):
        self.__log(_LogLevel.DEBUG, text)

    def log_info(self, text):
        self.__log(_LogLevel.INFO, text)

    def log_warn(self, text):
        self.__log(_LogLevel.WARN, text)

    def log_error(self, text):
        self.__log(_LogLevel.ERROR, text)

    def log_fatal(self, text):
        self.__log(_LogLevel.FATAL, text)

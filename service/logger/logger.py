import logging 
from .formatter import OneLineExceptionFormatter

class Logger():

    @staticmethod
    def makelogger(name):
        """
        name: logger name
        """
        datefmt = r"[%Y-%m-%d %H:%M:%S %z]"

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = OneLineExceptionFormatter(logging.BASIC_FORMAT, datefmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger


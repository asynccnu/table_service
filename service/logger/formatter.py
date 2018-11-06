import logging
import time

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)
 
    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\\n", " ||| ")

        result = result + " | " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        return result

import logging
import sys, os


def start_logger() -> logging:
    # LOGGING
    file_handler = logging.FileHandler(filename=os.path.join("logs", "data.log"))
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] <%(funcName)s> %(message)s",
        handlers=handlers,
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    return logging.getLogger()

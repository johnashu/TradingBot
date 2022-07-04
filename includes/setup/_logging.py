import logging
import sys, os, datetime


def start_logger(verbose: bool = False) -> logging:
    ts = datetime.datetime.now()
    # LOGGING
    file_handler = logging.FileHandler(
        filename=os.path.join("logs", f"{ts.day}-{ts.month}-{ts.year}.log")
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] <%(funcName)s> %(message)s",
        handlers=handlers,
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # disable external Logging (kucoin, asyncio, ...)
    if not verbose:
        for v in logging.Logger.manager.loggerDict.values():
            v.disabled = True

    return logging.getLogger(__name__)

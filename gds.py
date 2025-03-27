import sys
import os
sys.path.append(os.getcwd())

import server
import logging
logger = logging.getLogger()


def color_logger( record: logging.LogRecord) -> bool:
    # 当有新日志需要被记录时，此函数会被调用，用于判断是否记录该日志
    # 返回True代表允许记录，False代表不允许记录。
    if record.levelno == logging.DEBUG:
        record.color = "\033[0;36;49m"  # Cyan
    elif record.levelno == logging.INFO:
        record.color = "\033[0m"  # Default
    elif record.levelno == logging.WARNING:
        record.color = "\033[0;33;49m"  # Yellow
    elif record.levelno == logging.ERROR:
        record.color = "\033[0;31;49m"  # Red
    elif record.levelno == logging.CRITICAL:
        record.color = "\033[0;91;49m"  # Red Bold
    else:
        record.color = "\033[0m"
    return True


import signal
import sys
def exit(signum,frame):
    sys.exit(0)
signal.signal(signal.SIGINT,exit)
signal.signal(signal.SIGTERM,exit)

if __name__ == "__main__":

    if not os.path.exists(os.getcwd() + "/log"):
        os.mkdir(os.getcwd() + "/log")

    logger.setLevel(logging.DEBUG)

    deubgformatter = logging.Formatter("%(color)s%(levelname)s : %(message)s\033[0m")
    # logfilename = f"{os.getcwd()}/log/gds-debug-{int(time.time())}.log"
    # deubgHandler = logging.FileHandler(logfilename, encoding="utf-8")
    deubgHandler = logging.StreamHandler()
    deubgHandler.setLevel(logging.DEBUG)
    deubgHandler.setFormatter(deubgformatter)
    deubgHandler.addFilter(color_logger)
    logger.addHandler(deubgHandler)

    infoformatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")
    logfilename = f"{os.getcwd()}/log/gds.log"
    infoHandler = logging.FileHandler(logfilename, encoding="utf-8")
    infoHandler.setLevel(logging.INFO)
    infoHandler.setFormatter(infoformatter)
    logger.addHandler(infoHandler)

    logger.info("Hi 你好")
    try:
        server.main()
    except SystemExit as e:
        pass
    logger.info("Hi 再见")

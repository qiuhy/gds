import logging
import os
import game
import time

logger = logging.getLogger()
if __name__ == "__main__":
    if not os.path.exists(os.getcwd()+"/log"):
        os.mkdir(os.getcwd()+"/log")
     
    logger.setLevel(logging.DEBUG)

    deubgformatter = logging.Formatter("%(levelname)s : %(message)s")
    logfilename = f"{os.getcwd()}/log/gds-{int(time.time())}.log"
    deubgHandler = logging.FileHandler(logfilename, encoding="utf-8")
    deubgHandler.setLevel(logging.DEBUG)
    deubgHandler.setFormatter(deubgformatter)
    logger.addHandler(deubgHandler)

    infoformatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")
    logfilename = f"{os.getcwd()}/log/gds.log"
    infoHandler = logging.FileHandler(logfilename, encoding="utf-8")
    infoHandler.setLevel(logging.INFO)
    infoHandler.setFormatter(infoformatter)
    logger.addHandler(infoHandler)

    logger.info("Hi 你好")
    game.main()
    logger.info("Hi 再见")

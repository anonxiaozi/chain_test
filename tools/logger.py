# -*- coding: utf-8 -*-
# @Time: 2019/1/29
# @File: logger.py

import os
import sys

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGDIR = os.path.join(BASEDIR, "logs")
sys.path.insert(0, BASEDIR)
import logging
import datetime


def Logger(log_name):
    logger = logging.getLogger("Block")
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] %(message)s")
    fh = logging.FileHandler(os.path.join(LOGDIR, log_name), "w")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


if __name__ == "__main__":
    logger = Logger("{}.log".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
    logger.setLevel(logging.DEBUG)
    logger.info("[%s]: info test", "I")
    logger.warning("[%s]: warning test", "O")
    logger.error("error test")
    logger.debug("debug test")

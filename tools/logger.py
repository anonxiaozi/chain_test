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


def Logger(log_name=None):
    if not log_name:
        log_name = "{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d"))
    logger = logging.getLogger("Block")
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s   [%(filename)s:%(lineno)s]")
    fh = logging.FileHandler(os.path.join(LOGDIR, log_name), "a")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    return logger


if __name__ == "__main__":
    logger = Logger("{}.log".format(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
    logger.setLevel(logging.DEBUG)
    logger.info("[%s]: info test", "I")
    logger.warning("[%s]: warning test", "O")
    logger.error("error test")
    logger.debug("debug test")

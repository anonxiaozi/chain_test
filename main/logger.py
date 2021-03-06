# -*- coding: utf-8 -*-
# @Time: 2019/1/29
# @File: logger.py

"""level
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
"""

import os
import sys

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGDIR = os.path.join(BASEDIR, "logs")
sys.path.insert(0, BASEDIR)
import logging
import datetime


def Logger(log_name="{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d")), level=10):
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)
    logger = logging.getLogger("Block")
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s   [%(filename)s:%(lineno)s]")
    fh = logging.FileHandler(os.path.join(LOGDIR, log_name), "a")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(level)
    return logger

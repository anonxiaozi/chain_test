# -*- coding: utf-8 -*-
# @Time: 2019/1/23
# @File: CreateAccount

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.base import RPCTest


class CreateAccount(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "CreateAccount"
        self.start_sign = None

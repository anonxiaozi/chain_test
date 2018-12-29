# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: base.py

import argparse
import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.test_api import RunApi


class RPCTest(object):
    """
    RPC测试基类，继承时只需编写status方法即可
    """

    def __init__(self):
        self.start_method = ""
        self.start_sign = ""
        self.stop_method = ""
        self.stop_sign = ""
        self.status_method = ""
        self.status_sign = ""
        self.arg = self.get_args()

    @staticmethod
    def get_args():
        arg = argparse.ArgumentParser(prog="测试")
        arg.add_argument("host", type=str, help="服务器地址")
        arg.add_argument("port", type=int, help="服务器端口")
        return arg

    def get_test_obj(self, method, sign):
        func = RunApi(self.args["host"], self.args["port"], method, sign)
        return func

    def start(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        start_result = func.cli_api()
        self.check(self.start_method, start_result)

    def status(self):
        """
        每个继承的RPC测试，都需要重写status方法
        """
        pass

    def check(self, method, result):
        if result:
            print("%s start failed: %s" % (method, result))
            sys.exit()
        else:
            print("%s started..." % method)

    def stop(self):
        func = self.get_test_obj(self.stop_method, self.stop_sign)
        stop_result = func.cli_api()
        self.check(self.stop_method, stop_result)

    def run(self):
        self.start()
        self.status()
        self.stop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

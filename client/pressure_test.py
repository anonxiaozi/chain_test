# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: pressure_test.py

import argparse
import sys
import os
import time

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.test_api import RunApi


class PressureTest(object):

    def __init__(self):
        self.start_method, self.start_sign = "StartTxTest", "pressure_test"
        self.status_method, self.status_sign = "GetNodeStatus", None
        self.stop_method, self.stop_sign = "StopTxTest", None
        self.args = vars(self.get_args().parse_args())

    @staticmethod
    def get_args():
        arg = argparse.ArgumentParser(prog="测试")
        arg.add_argument("host", type=str, help="服务器地址")
        arg.add_argument("port", type=int, help="服务器端口")
        arg.add_argument("-t", "--totaltime", type=int, help="测试总时间，单位秒，默认: %(default)s s", default=300)
        arg.add_argument("-i", "--interval", type=int, help="多长时间打印一次状态，默认: %(default)s s", default=2)
        arg.add_argument("-s", "--fetch", type=str, help="需要打印的字段，多个字段用逗号分隔，默认: %(default)s，表示所有", default=[])
        return arg

    def get_test_obj(self, method, sign):
        func = RunApi(self.args["host"], self.args["port"], method, sign)
        return func

    def start(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        start_result = func.cli_api()
        self.check(self.start_method, start_result)

    def status(self):
        basic = 0
        count = 0
        func = self.get_test_obj(self.status_method, self.status_sign)
        while basic < self.args["totaltime"]:
            time.sleep(self.args["interval"])
            status_result = func.cli_api()
            print(str(count).center(50, "*"))

            RunApi.echo_monit_result(status_result, self.args["fetch"])
            basic += self.args["interval"]
            count += 1

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


if __name__ == "__main__":
    pressure = PressureTest()
    try:
        pressure.run()
    except KeyboardInterrupt:
        print("Exit.")
    finally:
        pressure.stop()

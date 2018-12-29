# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: pressure_test.py

import sys
import os
import time
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.test_api import RunApi
from client.base import RPCTest


class PressureTest(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "StartTxTest"
        self.start_sign = "pressure_test"
        self.status_method = "GetNodeStatus"
        self.status_sign = None
        self.stop_method = "StopTxTest"
        self.stop_sign = None
        self.arg.add_argument("-t", "--totaltime", type=int, help="测试总时间，单位秒，默认: %(default)s s", default=300)
        self.arg.add_argument("-i", "--interval", type=int, help="多长时间打印一次状态，默认: %(default)s s", default=2)
        self.arg.add_argument("-s", "--fetch", type=str, help="需要打印的字段，多个字段用逗号分隔，默认: %(default)s，表示所有", default=None)
        self.args = vars(self.arg.parse_args())

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


if __name__ == "__main__":
    pressure = PressureTest()
    try:
        pressure.run()
    except KeyboardInterrupt:
        print("Exit.")
    finally:
        pressure.stop()

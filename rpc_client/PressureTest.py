# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: PressureTest.py

"""
测试StartTxTest接口，压力测试，在间隔时间内打印节点信息
"""

import sys
import os
import time

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.test_api import RunApi
from rpc_client.base import RPCTest
from main.logger import Logger


class PressureTest(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.start_method = "StartTxTest"
        self.start_sign = "pressure_test"
        self.status_method = "GetTxTestStatus"
        self.status_sign = None
        self.stop_method = "StopTxTest"
        self.stop_sign = None
        self.arg.add_argument("-t", "--totaltime", type=int, help="测试总时间，单位秒，默认: %(default)s s", default=300)
        self.arg.add_argument("-i", "--interval", type=int, help="多长时间打印一次状态，默认: %(default)s s", default=2)
        self.arg.add_argument("-s", "--fetch", type=str, help="需要打印的字段，多个字段用逗号分隔，默认: %(default)s，表示所有", default=None)

    def status(self):
        basic = 0
        count = 0
        func = self.get_test_obj(self.status_method, self.status_sign)
        while basic < self.args["totaltime"]:
            time.sleep(self.args["interval"])
            status_result = func.cli_api()
            print(str(count).center(50, "*"))
            RunApi.echo_monit_result(result=status_result["TestResults"] if "TestResults" in status_result else status_result, field=self.args["fetch"])
            basic += self.args["interval"]
            count += 1


if __name__ == "__main__":
    logger = Logger()
    pressure = PressureTest(logger)
    pressure.args = vars(pressure.arg.parse_args())
    try:
        pressure.run()
    except KeyboardInterrupt:
        print("Exit.")
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        pressure.stop()

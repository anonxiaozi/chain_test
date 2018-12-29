# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: unit_test.py

import sys
import os
import time

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.pressure_test import PressureTest
from main.test_api import RunApi
import argparse
import threading


class UnitTest(PressureTest):

    def __init__(self):
        super().__init__()
        self.start_method, self.start_sign = "StartTxTest", "unit_test"
        self.status_method, self.status_sign = "GetNodeStatus", None
        self.stop_method, self.stop_sign = "StopTxTest", None
        self.args = vars(self.get_args().parse_args())

    def get_args(self):
        arg = argparse.ArgumentParser(prog="测试")
        arg.add_argument("host", type=str, help="服务器地址")
        arg.add_argument("port", type=int, help="服务器端口")
        # arg.add_argument("-t", "--totaltime", type=int, help="测试总时间，单位秒，默认: %(default)s s", default=300)
        # arg.add_argument("-i", "--interval", type=int, help="多长时间打印一次状态，默认: %(default)s s", default=2)
        # arg.add_argument("-s", "--fetch", type=str, help="需要打印的字段，多个字段用逗号分隔，默认: %(default)s，表示所有", default=[])
        return arg

    @staticmethod
    def cost():
        num = 0
        while True:
            time.sleep(1)
            num += 1
            sys.stdout.write("Cost %d s\r" % num)
            sys.stdout.flush()

    def status(self):
        self.start_cost()
        func = self.get_test_obj(self.status_method, self.status_sign)
        while True:
            time.sleep(5)
            status_result = func.cli_api()
            if not isinstance(status_result, dict):
                print(status_result)
                return status_result
            else:
                if "teststatus" in status_result["TestResults"]:
                    RunApi.echo_monit_result(status_result)
                    break
                else:
                    continue

    def start_cost(self):
        cost = threading.Thread(target=self.cost)
        cost.setDaemon(True)
        cost.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


if __name__ == "__main__":
    unittest = UnitTest()
    try:
        unittest.run()
    except KeyboardInterrupt:
        print("Exit.")
    except Exception as e:
        print("Error: %s" % e)
    finally:
        unittest.stop()

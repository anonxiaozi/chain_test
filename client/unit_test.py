# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: unit_test.py

import sys
import os
import time
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.test_api import RunApi
import threading
from client.base import RPCTest


class UnitTest(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "StartTxTest"
        self.start_sign = "unit_test"
        self.status_method = "GetTxTestStatus"
        self.status_sign = None
        self.stop_method = "StopTxTest"
        self.stop_sign = None
        self.args = vars(self.arg.parse_args())

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
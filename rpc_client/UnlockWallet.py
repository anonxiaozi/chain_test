# -*- coding: utf-8 -*-
# @Time: 2019/1/23
# @File: UnlockWallet.py

"""
解锁给定地址的钱包，解锁成功，返回"{}"，否则返回错误信息
"""

import sys
import os
import json

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from rpc_client.base import RPCTest
from main.logger import Logger


class UnlockWallet(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.start_method = "UnlockWallet"
        self.start_sign = None
        self.arg.add_argument("-d", "--addr", help="要解锁的钱包地址", required=True)
        self.arg.add_argument("-s", "--password", help="钱包密码，默认为: %(default)s", default="123456")
        self.arg.add_argument("-t", "--time", type=int, help="解锁时长，单位秒，默认为：%(default)s s", default=100)

    def status(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        body = {"Addr": self.args["addr"], "Password": self.args["password"], "TimeSpan": self.args["time"]}
        result = func.cli_api(json.dumps(body).encode("utf-8"))
        return result

    def run(self):
        return self.status()


if __name__ == "__main__":
    logger = Logger()
    unlockwallet = UnlockWallet(logger)
    unlockwallet.args = vars(unlockwallet.arg.parse_args())
    result = unlockwallet.run()
    if result: print(result)

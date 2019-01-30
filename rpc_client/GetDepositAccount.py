# -*- coding: utf-8 -*-
# @Time: 2019/1/17
# @File: GetDepositAccount

"""
通过质押ID获取账户的质押信息，使用GetDepositAccount接口，返回结果：
{'root': {'DepositID': {'Value': '6051053228330400958'}, 'Amount': '10000'}, '3006': {'DepositID': {'Value': '9384355224946534474'}, 'Amount': '10000'}}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from rpc_client.base import RPCTest
from tools.logger import Logger


class GetDepositAccount(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.start_method = "GetDepositAccount"
        self.start_sign = None
        self.arg.add_argument("-a", "--accounts", help="质押账号，多个账号用逗号分隔", required=True)
        self.arg.add_argument("-f", "--field", help="需要返回的字段", required=False)

    @staticmethod
    def change_body(values):
        for value in values:
            body = {
                "ID": value
            }
            yield value, body

    def status(self):
        deposit_map = {}
        func = self.get_test_obj(self.start_method, self.start_sign)
        data = self.change_body(self.args["accounts"].split(","))
        for value, body in data:
            deposit_map[value] = {}
            result = func.cli_api(body)
            if "DepositID" in result:
                if "field" in self.args:
                    if self.args["field"]:
                        deposit_map[value] = result[self.args["field"]]
                    else:
                        deposit_map[value] = result
        return deposit_map

    def run(self):
        return self.status()


if __name__ == "__main__":
    logger = Logger()
    get_info = GetDepositAccount(logger)
    get_info.args = vars(get_info.arg.parse_args())
    deposit_map = get_info.run()
    for key, value in deposit_map.items():
        print(key, value, sep=" -> ")

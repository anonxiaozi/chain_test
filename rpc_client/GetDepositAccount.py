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


class GetDepositAccount(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "GetDepositAccount"
        self.start_sign = None
        self.arg.add_argument("-a", "--accounts", help="质押账号，多个账号用逗号分隔", required=True)

    @staticmethod
    def change_body(values):
        for value in values:
            body = {
                "ID": value
            }
            yield value, body

    def status(self):
        deposit_map, sub_deposit_map = {}, {}
        func = self.get_test_obj(self.start_method, self.start_sign)
        data = self.change_body(self.args["accounts"].split(","))
        for value, body in data:
            result = func.cli_api(body)
            if "DepositID" in result:
                deposit_map[value] = result
                sub_deposit_map[value] = {"DepositID": result["DepositID"], "Amount": result["Amount"]}
            else:
                deposit_map[value] = None
                sub_deposit_map[value] = None
        return deposit_map

    def run(self):
        return self.status()


if __name__ == "__main__":
    get_info = GetDepositAccount()
    get_info.args = vars(get_info.arg.parse_args())
    deposit_map = get_info.run()
    for key, value in deposit_map.items():
        print(key, value, sep=" -> ")

# -*- coding: utf-8 -*-
# @Time: 2019/1/17
# @File: GetDepositAccount

"""
通过质押ID获取账户的质押信息，使用GetDepositAccount接口
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.base import RPCTest


class GetDepositAccount(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "GetDepositAccount"
        self.start_sign = None
        self.append_args()

    def append_args(self):
        self.arg.add_argument("-d", "--dest", help="需要查找的质押ID，多个ID用逗号分隔", required=True)

    @staticmethod
    def change_body(values):
        for value in values:
            body = {
                "DepositID": {
                    "Value": value
                }
            }
            yield value, body

    def status(self, dict_data):
        deposit_id = dict_data["dest"].split(",")
        deposit_map = {x: {"Deposit": False, "Amount": 0} for x in deposit_id}
        func = self.get_test_obj(self.start_method, self.start_sign)
        data = self.change_body(deposit_id)
        for value, body in data:
            result = func.cli_api(body)
            if "DepositID" in result:
                if value == result["DepositID"]["Value"]:
                    deposit_map[value]["Deposit"] = True
                    deposit_map[value]["Amount"] = result["Amount"]
        return deposit_map


if __name__ == "__main__":
    get_info = GetDepositAccount()
    get_info.args = vars(get_info.arg.parse_args())
    deposit_map = get_info.status(get_info.args)
    for key, value in deposit_map.items():
        print(key, value, sep=" --> ")

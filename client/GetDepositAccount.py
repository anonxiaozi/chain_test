# -*- coding: utf-8 -*-
# @Time: 2019/1/17
# @File: GetDepositAccount

"""
通过质押ID获取账户的质押信息，使用GetDepositAccount接口，返回结果：
{'root': {'Deposit': True, 'Amount': '10000'}, '3005': {'Deposit': False, 'Amount': 0}}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.base import RPCTest
from client.GetDepositID import GetDepositID


class GetDepositAccount(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "GetDepositAccount"
        self.start_sign = None
        self.append_args()

    def append_args(self):
        self.arg.add_argument("-a", "--accounts", help="质押账号，多个账号用逗号分隔", required=True)

    def get_block_depositid(self, args):
        deposit = GetDepositID()
        dict_data = args["args"]
        deposit.args["accounts"] = dict_data["accounts"].split(",")
        self.deposit_id_map = deposit.status(args)
        self.deposit_id_info_map = {x: {"Deposit": False, "Amount": 0} for x in self.deposit_id_map.values()}

    @staticmethod
    def change_body(values):
        for value in values:
            body = {
                "DepositID": {
                    "Value": value
                }
            }
            yield value, body

    def status(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        data = self.change_body(self.deposit_id_map.values())
        for value, body in data:
            result = func.cli_api(body)
            if "DepositID" in result:
                if value == result["DepositID"]["Value"]:
                    self.deposit_id_info_map[value]["Deposit"] = True
                    self.deposit_id_info_map[value]["Amount"] = result["Amount"]
        reverse_deposit_id_map = {x: y for y, x in self.deposit_id_map.items()}
        account_info_map = {reverse_deposit_id_map[x]: self.deposit_id_info_map[x] for x in reverse_deposit_id_map}
        return account_info_map

    def run(self, **kwargs):
        self.get_block_depositid(kwargs)
        return self.status()


if __name__ == "__main__":
    get_info = GetDepositAccount()
    get_info.args = vars(get_info.arg.parse_args())
    deposit_map = get_info.run(args=get_info.args)
    print(deposit_map)

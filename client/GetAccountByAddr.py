# -*- coding: utf-8 -*-
# @Time: 2019/1/23
# @File: GetAccountByAddr

"""
通过账户地址获取账户信息，返回结果示例：
{'0x11fd6f0a3b96ac630d9cb67c49bad2c41696b914': {'Name': 'root', 'AccountAddr': '0x11fd6f0a3b96ac630d9cb67c49bad2c41696b914', 'CreatorAddr': '', 'CreationDate': '2019-01-23T06:53:57.960412331Z', 'Balance': '100104872'}}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.base import RPCTest


class GetAccountByAddr(RPCTest):

    def __init__(self):
        super().__init__()
        self.start_method = "GetAccountByAddr"
        self.start_sign = None
        self.arg.add_argument("-a", "--addr", help="账户地址，多个账户地址用逗号分隔", required=True)

    @staticmethod
    def change_body(values):
        for value in values:
            body = {
                "ID": value
            }
            yield value, body

    def status(self):
        final_result = {}
        func = self.get_test_obj(self.start_method, self.start_sign)
        values = self.args["addr"].split(",")
        data = self.change_body(values)
        for value, body in data:
            result = func.cli_api(body)
            final_result[value] = result
        else:
            return final_result

    def run(self):
        return self.status()


if __name__ == "__main__":
    getaccount = GetAccountByAddr()
    getaccount.args = vars(getaccount.arg.parse_args())
    result = getaccount.run()
    for account, info in result.items():
        print(account, info, sep=": ")

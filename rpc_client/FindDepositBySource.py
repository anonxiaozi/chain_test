# -*- coding: utf-8 -*-
# @Time: 2019/1/23
# @File: FindDepositBySource

"""
通过给定的地址获取质押ID，返回结果：
{'0x11fd6f0a3b96ac630d9cb67c49bad2c41696b914': [{'Value': '6051053228330400958'}]}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from rpc_client.base import RPCTest
from tools.logger import Logger


class FindDepositBySource(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.start_method = "FindDepositBySource"
        self.start_sign = None
        self.arg.add_argument("-a", "--addr", help="address,多个地址用逗号分隔", required=True)

    @staticmethod
    def change_body(values):
        for value in values:
            body = {
                "ID": value
            }
            yield value, body

    def status(self):
        info_dict = {}
        func = self.get_test_obj(self.start_method, self.start_sign)
        data = self.change_body(self.args["addr"].split(","))
        for addr, body in data:
            result = func.cli_api(body)
            info_dict[addr] = result["Value"] if "Value" in result else None
        return info_dict

    def run(self):
        return self.status()


if __name__ == "__main__":
    logger = Logger()
    finddeposit = FindDepositBySource(logger)
    finddeposit.args = vars(finddeposit.arg.parse_args())
    result = finddeposit.run()
    print(result)

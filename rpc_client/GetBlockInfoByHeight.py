# -*- coding: utf-8 -*-
# @Time: 2019/2/12
# @File: GetBlockInfoByHeight

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from rpc_client.base import RPCTest
from main.logger import Logger


class GetBlockInfoByHeight(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.start_method = "GetBlockInfoByHeight"
        self.start_sign = None
        self.arg.add_argument("-n", "--number", type=int, help="块高度,默认为: %(default)s", default=0)

    @staticmethod
    def change_body(height):
        return {
            "Key": height
        }

    def status(self):
        body = self.change_body(self.args["number"])
        func = self.get_test_obj(self.start_method, self.start_sign)
        result = func.cli_api(body=body)
        return result

    def run(self):
        return self.status()


if __name__ == "__main__":
    logger = Logger()
    getblockinfobyheight = GetBlockInfoByHeight(logger)
    getblockinfobyheight.args = vars(getblockinfobyheight.arg.parse_args())
    result = getblockinfobyheight.run()
    print(result)

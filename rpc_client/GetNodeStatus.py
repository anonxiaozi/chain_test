# -*- coding: utf-8 -*-
# @Time: 2019/2/12
# @File: GetNodeStatus

"""
获取节点信息，返回结果：
{'Code': 'NODE_MISS_DB_CONNECTION', 'Height': '218', 'TxSerial': '2705938592756349760', \
'BlockTime': '2019-02-12T02:41:13.101276590Z', 'BlockTxCount': 2, 'BlockPerSecond': 0, 'TxPerSecond': 0, 'TxQueueLength': 0}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASEDIR)
from rpc_client.base import RPCTest
from main.logger import Logger


class GetNodeStatus(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.start_method = "GetNodeStatus"
        self.start_sign = None

    def status(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        result = func.cli_api()
        return result

    def run(self):
        return self.status()


if __name__ == "__main__":
    logger = Logger()
    getnodestatus = GetNodeStatus(logger)
    getnodestatus.args = vars(getnodestatus.arg.parse_args())
    result = getnodestatus.run()
    print(result)

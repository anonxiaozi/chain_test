# -*- coding: utf-8 -*-
# @Time: 2019/1/15
# @File: GetDepositScale

"""
获取当前块高度，计算每个质押账户的出块数，接口包括：GetBlockInfoByHeight、GetNodeStatus，返回结果：
{'root': 2815, '3006': 2966, '3007': 2663}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.base import RPCTest
from client.GetDepositID import GetDepositID
import json


class GetDepositScale(RPCTest):

    def __init__(self):
        super().__init__()
        self.arg.add_argument("-a", "--accounts", help="质押账号，多个账号用逗号分隔", required=True)

    def get_block_depositid(self):
        """
        获取块信息中的质押ID
        :param dict_data: 命令行参数信息
        """
        deposit = GetDepositID()
        deposit.args = self.args
        self.deposit_id_map = deposit.status()
        self.deposit_id_count_map = {x: 0 for x in self.deposit_id_map.values()}

    @staticmethod
    def change_height_body(height):
        for key in range(height + 1):
            body = {
                "Key": str(key)
            }
            yield key, body

    def get_block_info(self):
        """
        首先根据get_current_height来获取当前块高度，然后循环每个块信息
        """
        sign = 1
        height = self.get_current_height()
        method = "GetBlockInfoByHeight"
        func = self.get_test_obj(method, None)
        bodys = self.change_height_body(height)
        for key, body in bodys:
            if sign > 10:
                sys.exit(1)  # 出现10次获取块信息错误，停止获取块信息
            body = json.dumps(body).encode("utf-8")
            result = func.cli_api(body)
            if not self.check_result(result):
                print("Retry...".center(50, "*"))
                self.check_result(result)
            try:
                deposit_id = result["DepositID"]["Value"]
                if deposit_id in self.deposit_id_count_map:
                    self.deposit_id_count_map[deposit_id] += 1
                else:
                    self.deposit_id_count_map[deposit_id] = 1
                print(str(key).center(10), end=' -->    ')
                print("[%s]" % deposit_id)
            except Exception:
                print(result)
                sign += 1
        else:
            print(("Block Height [ %s ]" % height).center(100, "="))
            reverse_deposit_id_map = {x: y for y, x in self.deposit_id_map.items()}
            relate_name_count = {reverse_deposit_id_map[x]: self.deposit_id_count_map[x] for x in self.deposit_id_count_map}
            for key, value in relate_name_count.items():
                print(key, value, sep=" -> ")
            return relate_name_count

    def get_current_height(self):
        """
        使用"GetNodeStatus"接口获取当前块高度
        """
        method = "GetNodeStatus"
        func = self.get_test_obj(method, None)
        result = func.cli_api()
        if not self.check_result(result):  # 获取失败后，尝试重试一次
            print("Retry...".center(50, "*"))
            self.check_result(result)
        try:
            height = int(result["Height"])
            print(("Block Height [ %s ]" % height).center(100, "="))
            return height
        except Exception:
            print(result)
            sys.exit(1)

    @staticmethod
    def check_result(result):
        """
        检查接口返回的信息是否正确
        """
        if "message" in result:
            if "cannot be send tx to node currently" in result["message"]:
                print(result)
            else:
                return result
        else:
            return result

    def run(self):
        self.get_block_depositid()
        return self.get_block_info()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == "__main__":
    deposit_scale = GetDepositScale()
    deposit_scale.args = vars(deposit_scale.arg.parse_args())
    try:
        map_account_count = deposit_scale.run()
        print(map_account_count)
    except KeyboardInterrupt as e:
        print("Exit.")
        sys.exit(1)

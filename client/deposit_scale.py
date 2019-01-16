# -*- coding: utf-8 -*-
# @Time: 2019/1/15
# @File: deposit_scale

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from client.base import RPCTest
from tools.remote_exec import MySSH
import re
import json


class DepositScale(RPCTest):

    def __init__(self):
        super().__init__()
        self.arg.add_argument("-d", "--host", help="远程主机名或地址，用来获取DepositID")
        self.args = vars(self.get_args().parse_args())

    def get_block_depositid(self):
        deposit = GetDepositID(self.args["host"])
        self.deposit_id_map = deposit.run()
        self.deposit_id_count_map = dict.fromkeys(self.deposit_id_map.values(), 0)

    def change_height_body(self, height):
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
                print(key, ": ", value)

    def get_current_height(self):
        method = "GetNodeStatus"
        func = self.get_test_obj(method, None)
        result = func.cli_api()
        if not self.check_result(result):
            print("Retry...".center(50, "*"))
            self.check_result(result)
        try:
            height = int(result["Height"])
            print(("Block Height [ %s ]" % height).center(100, "="))
            return height
        except Exception:
            print(result)
            sys.exit(1)

    def check_result(self, result):
        if "message" in result:
            if "cannot be send tx to node currently" in result["message"]:
                print(result)
            else:
                return result
        else:
            return result

    def run(self):
        self.get_block_depositid()
        self.get_block_info()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class GetDepositID(MySSH):
    id_map = {
        "root": "root",
        "3006": "3006",
        "3007": "3007",
        # "3008": "3008",
        # "3009": "3009"
    }

    def __init__(self, hostname):
        self.id_re = re.compile(r"client_pb:\s(\d{19})\s?")
        super().__init__(hostname, username="root", keyfile=os.path.join(CONFIGDIR, "id_rsa_jump"), port=22)

    def get_deposit_id(self, deposit_name="root"):
        result = self.remote_exec("cd /root/work; ./cli convert -from %s -method str2depositid" % deposit_name)
        deposit_id = self.id_re.findall(result)
        if deposit_id:
            self.id_map[deposit_name] = deposit_id[0]

    def run(self):
        for name in self.id_map:
            self.get_deposit_id(name)
        return self.id_map


if __name__ == "__main__":
    deposit_scale = DepositScale()
    try:
        deposit_scale.run()
    # deposit_scale.get_block_depositid()
    except KeyboardInterrupt as e:
        print("Exit.")
        sys.exit(1)

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
        print(self.deposit_id_map)

    def change_height_body(self, height):
        for key in range(height + 1):
            body = {
                "key": str(key)
            }
            yield key, body

    def get_block_info(self):
        height = self.get_current_height()
        method = "GetBlockInfoByHeight"
        func = self.get_test_obj(method, None)
        bodys = self.change_height_body(height)
        for key, body in bodys:
            body = json.dumps(body).encode("utf-8")
            result = func.cli_api(body)
            if not self.check_result(result, "get_block_info"):
                self.check_result(result, "get_block_info")
            try:
                deposit_name = result["DepositID"]["Value"]
                print(str(key).center(10), end=' -->    ')
                print("[%s]" % deposit_name)
            except Exception:
                print(result)

    def get_current_height(self):
        method = "GetNodeStatus"
        func = self.get_test_obj(method, None)
        result = func.cli_api()
        if not self.check_result(result, "get_current_height"):
            self.check_result(result, "get_current_height")
        try:
            height = int(result["Height"])
            print("Block Height [ %s ]" % height)
            return height
        except Exception:
            print(result)
            sys.exit(1)

    def check_result(self, result, func_name):
        if "message" in result:
            if "cannot be send tx to node currently" in result["message"]:
                print(result)
                print("Retry...".center(50, "*"))
            else:
                return result
        else:
            return result

    def run(self):
        self.get_block_info()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class GetDepositID(MySSH):
    id_map = {
        "root": None,
        "3006": None,
        "3007": None,
        "3008": None,
        "3009": None
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

# -*- coding: utf-8 -*-
# @Time: 2019/1/15
# @File: GetDepositScale

"""
获取当前块高度，计算每个质押账户的出块数，接口包括：GetBlockInfoByHeight、GetNodeStatus，返回结果：
{'root': {'Count': 338, 'Scale': '34.49%'}, '3006': {'Count': 227, 'Scale': '23.16%'}}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from rpc_client.base import RPCTest
from rpc_client.GetDepositID import GetDepositID
from rpc_client.GetBlockInfoByHeight import GetBlockInfoByHeight
from rpc_client.GetDepositAccount import GetDepositAccount
from cmd_client.cmd_base import RunCmd
import json
from main.logger import Logger


class GetDepositScale(RPCTest):

    def __init__(self, logger):
        super().__init__(logger)
        self.arg.add_argument("-a", "--accounts", help="质押账号，多个账号用逗号分隔", required=True)
        self.logger = logger

    def get_block_depositid(self):
        """
        获取块信息中的质押ID
        :param dict_data: 命令行参数信息
        """
        deposit = GetDepositID(self.logger)
        deposit.args = self.args
        self.deposit_id_map = deposit.status()
        self.deposit_id_count_map = {x: 0 for x in self.deposit_id_map.values()}

    def get_deposit_from_pubkey(self, accounts):
        """
        获取账号的pubkey，然后将pubkey转换为DepositID
        """
        deposit_id_account_map = {}
        cmd = RunCmd(self.logger)
        cmd.args = {
            "host": self.args["host"],
            "port": 22,
            "user": "root",
            "key": os.path.join(CONFIGDIR, "id_rsa_jump"),
            "data-path": "/root/.pb_data",
            "method": "str2depositid",
            "type": "bls"
        }
        for account in accounts.strip().split(","):
            cmd.args["name"] = account
            if account == "root":
                cmd.args["nick"] = 3005
            else:
                cmd.args["nick"] = account
            pubkey = cmd.run("getwalletkey", self.logger)  # 获取公钥
            if not pubkey.startswith("0x"):
                print("Get pubkey faild: {} [{}]".format(pubkey, account))
                self.logger.error("Get pubkey faild: {} [{}]".format(pubkey, account))
                continue
            cmd.args["from"] = pubkey
            deposit_id = cmd.run("convert", self.logger)  # 获取质押ID
            deposit_id_account_map[account] = deposit_id
        else:
            deposit_id_count_map = {x: 0 for x in deposit_id_account_map.values()}
        return deposit_id_account_map, deposit_id_count_map

    def get_depositid_from_block(self, block_info):
        """
        从块信息中获取DepositID
        :return: 如果块信息中存在DepositID，则返回(DepositID, True)，否则返回(error_info, False)
        """
        if isinstance(block_info, dict):
            try:
                deposit_id = block_info["DepositID"]["Value"]
                return deposit_id, True
            except Exception as e:
                echo = "Faild get DepositID from block_info: {}".format(e)
                self.logger.error(echo)
                print(e)
                return block_info
        else:
            self.logger.error("Get block info failed: {}".format(block_info))
            return block_info, False

    def get_block_info(self):
        """
        首先根据get_current_height来获取当前块高度，然后循环每个块信息
        """
        self.deposit_id_account_map, self.deposit_id_count_map = \
            self.get_deposit_from_pubkey(self.args["accounts"])
        info_dict = {
            account_name: {
                "DepositID": self.deposit_id_account_map[account_name],
                "Amount": "",
                "Count": "",
                "Scale": ""
            } for account_name in self.deposit_id_account_map
        }  # 最终结果，{account: {DepositID: "", Amount: "", "Count": "", "Scale": ""}}
        fail_sign = 1
        height = self.get_current_height()
        block_obj = GetBlockInfoByHeight(self.logger)
        block_obj.args = self.args
        for i in range(height):  # 循环所有块
            if fail_sign > 10:
                sys.exit(1)  # 出现10次获取块信息错误，停止获取块信息
            block_obj.args["number"] = i
            block_info = block_obj.run()
            deposit_id, get_signal = self.get_depositid_from_block(block_info)  # 获取块信息中的DepositID
            print(i, "[ {} ]".format(deposit_id), sep=" --> ")
            if not get_signal:
                fail_sign += 1
                continue
            if deposit_id in self.deposit_id_count_map:
                self.deposit_id_count_map[deposit_id] += 1
        get_deposit_amount = GetDepositAccount(self.logger)
        get_deposit_amount.args = self.args
        get_deposit_amount.args["accounts"] = ",".join(self.deposit_id_count_map.keys())
        get_deposit_amount.args["field"] = "Amount"
        self.deposit_amount_map = get_deposit_amount.run()
        reverse_deposit_id_account_map = {x: y for y, x in self.deposit_id_account_map.items()}
        for deposit_id, account_name in reverse_deposit_id_account_map.items():
            info_dict[account_name]["Amount"] = self.deposit_amount_map[deposit_id]
            info_dict[account_name]["Count"] = self.deposit_id_count_map[deposit_id]
            info_dict[account_name]["Scale"] = "{:.2%}".format(self.deposit_id_count_map[deposit_id] / height)
        else:
            self.logger.info("[O] {}".format(info_dict))

        return info_dict

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
            self.logger.info(("Block Height [ %s ]" % height).center(100, "="))
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
    logger = Logger()
    deposit_scale = GetDepositScale(logger)
    deposit_scale.args = vars(deposit_scale.arg.parse_args())
    try:
        map_account_count = deposit_scale.run()
        print(map_account_count)
    except KeyboardInterrupt as e:
        print("Exit.")
        sys.exit(1)

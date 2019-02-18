# -*- coding: utf-8 -*-
# @Time: 2019/2/18
# @File: batch_create_account

"""
  批量创建账户，返回账户地址列表和账户信息列表
"""

import datetime
import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from cmd_client.cmd_base import RunCmd
from main.logger import Logger


class BatchCreateAccount(RunCmd):

    def __init__(self, logger, **kwargs):
        self.logger = logger
        self.data = kwargs["info"]
        super().__init__(self.logger)
        self.args = {"host": self.data["address"], "user": self.data["ssh_user"], "port": self.data["ssh_port"], "key": self.data["key"]}

    def create_account(self):
        accname = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.args["accname"] = accname
        self.args["nick"] = self.data["nick"]
        self.args["type"] = self.data["type"]
        self.args["noderpcaddr"] = self.data["address"]
        self.args["noderpcport"] = self.data["rpc_port"]
        # 创建wallet
        self.run("createwallet", self.logger)
        # 获取root地址
        self.args["accname"] = "root"
        root_address = self.run("getwalletinfo", self.logger)
        # 获取被创建账户的wallet地址
        self.args["accname"] = accname
        address = self.run("getwalletinfo", self.logger)
        self.args["address"] = address
        # 创建账户
        self.args["creatoraddr"] = root_address
        self.args["accname"] = accname
        self.run("createaccount", self.logger)
        # 转账200
        self.args["amount"] = self.data["amount"]
        self.args["from"] = root_address
        self.args["toaddr"] = address
        self.run("send", self.logger)
        # 获取账户信息
        accinfo = self.run("getaccount", self.logger)
        return accname, accinfo

    def batch_create(self):
        accname_list = []
        accinfo_list = []
        for n in range(self.data["number"]):
            account_name, account_info = self.create_account()
            accname_list.append(account_name)
            accinfo_list.append(account_info)
        return accname_list, accinfo_list


if __name__ == "__main__":
    logger = Logger()
    info = {
        "address": "10.15.101.77",
        "ssh_user": "root",
        "ssh_port": 22,
        "rpc_port": 40001,
        "key": os.path.join(CONFIGDIR, "id_rsa_jump"),
        "nick": 3005,  # 钱包名
        "type": "ecc",  # 账户类型
        "amount": 10000,  # 转账金额
        "number": 2  # 创建多少账户
    }
    create_obj = BatchCreateAccount(logger, info=info)
    accname_list, accinfo_list = create_obj.batch_create()
    for n in range(len(accname_list)):
        print(accname_list[n])
        print(accinfo_list[n])

# -*- coding: utf-8 -*-
# @Time: 2019/1/28
# @File: test_valid.py

import datetime
import time
import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from cmd_client.cmd_base import RunCmd
from rpc_client.GetDepositAccount import GetDepositAccount
from rpc_client.GetAccountByName import GetAccountByName


class DoTest(RunCmd):

    def __init__(self, host):
        super().__init__()
        self.args = {"host": host, "user": "root", "port": 22, "key": os.path.join(CONFIGDIR, "id_rsa_jump")}

    def cmd_run(self):
        accname = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.args["accname"] = accname
        self.args["nick"] = "3005"
        self.args["type"] = "ecc"
        self.args["noderpcaddr"] = "127.0.0.1"
        self.args["noderpcport"] = 40001
        # 创建wallet
        self.run("createwallet")
        # 获取root地址
        self.args["accname"] = "root"
        root_address = self.run("getwalletinfo")
        # 获取被创建账户的wallet地址
        self.args["accname"] = accname
        address = self.run("getwalletinfo")
        self.args["address"] = address
        # 创建账户
        self.args["creatoraddr"] = root_address
        self.args["accname"] = accname
        self.run("createaccount")
        # 转账12000
        self.args["amount"] = 12000
        self.args["from"] = root_address
        self.args["toaddr"] = address
        self.run("send")
        # 获取账户信息
        time.sleep(2)
        self.run("getaccount")

    def rpc_run(self):
        accounts = "root,3006"
        self.args["port"] = 60002
        # 获取质押信息
        print("[ GetDepositAccount ] [RPC]".center(80, "*"))
        self.args["accounts"] = accounts
        getdepositaccount = GetDepositAccount()
        getdepositaccount.args = self.args
        deposit_result = getdepositaccount.run()
        print(deposit_result)
        # 获取账户信息
        print("[ GetAccountByName ] [RPC]".center(80, "*"))
        self.args["name"] = accounts
        getaccountbyname = GetAccountByName()
        getaccountbyname.args = self.args
        get_account_result = getaccountbyname.run()
        print(get_account_result)

    def start(self):
        self.cmd_run()
        self.rpc_run()


if __name__ == "__main__":
    do_test = DoTest("10.15.101.77")
    do_test.start()

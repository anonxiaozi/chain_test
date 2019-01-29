# -*- coding: utf-8 -*-
# @Time: 2019/1/28
# @File: test_valid.py

import datetime
import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from cmd_client.cmd_base import RunCmd
from rpc_client.GetDepositAccount import GetDepositAccount
from rpc_client.GetAccountByAddr import GetAccountByAddr
from tools.bin_tools import EveryOne
from main.deploy_tools import DeployNode
from rpc_client.GetDepositScale import GetDepositScale
from tools.logger import Logger


class DoTest(RunCmd):

    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs["data"]
        self.args = {"host": self.kwargs["host"], "user": self.kwargs["user"], "port": self.kwargs["port"], "key": self.kwargs["key"]}

    def deploy(self):
        for action in ["stop", "clean", "init"]:
            args = {'sub': 'deploy', 'config': self.kwargs["config_file"], 'action': action}
            deploy = EveryOne(args)
            deploy.do_deploy()
            DeployNode.wait(2)

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
        # 转账200
        self.args["amount"] = 200
        self.args["from"] = root_address
        self.args["toaddr"] = address
        self.run("send")
        # 获取账户信息
        DeployNode.wait(3)
        self.run("getaccount")

    def rpc_run(self):
        self.args["port"] = 60002
        # 获取质押信息
        DeployNode.wait(5)
        print("[ GetDepositAccount ] [RPC]".center(80, "*"))
        self.args["accounts"] = self.kwargs["accounts"]
        getdepositaccount = GetDepositAccount()
        getdepositaccount.args = self.args
        getdepositaccount.args["field"] = None
        deposit_result = getdepositaccount.run()
        print(deposit_result)
        # 获取账户信息
        DeployNode.wait(5)
        for rpc_port in self.kwargs["rpc_ports"].split(","):
            self.args["port"] = int(rpc_port)
            print("[ GetAccountByAddr ] [RPC] <{}>".format(rpc_port).center(80, "*"))
            getaccountbyname = GetAccountByAddr()
            getaccountbyname.args = self.args
            getaccountbyname.args["addr"] = self.args["address"]
            get_account_result = getaccountbyname.run()
            print(get_account_result)

    def other_run(self):
        # 获取出块比例
        self.args["port"] = 60002
        get_scale = GetDepositScale()
        get_scale.args = self.args
        get_scale_result = get_scale.run()
        print(get_scale_result)

    def start(self):
        self.deploy()
        DeployNode.wait(5)
        self.cmd_run()
        self.rpc_run()
        DeployNode.wait(120)
        self.other_run()


if __name__ == "__main__":
    data = {
        "host": "10.15.101.77",
        "config_file": "config_ubuntu.ini",
        "user": "root",
        "port": 22,
        "key": os.path.join(CONFIGDIR, "id_rsa_jump"),
        "accounts": "root,3006,3007",
        "rpc_ports": "60002,60012,60022"
    }
    do_test = DoTest(data=data)
    do_test.start()

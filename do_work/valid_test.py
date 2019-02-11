# -*- coding: utf-8 -*-
# @Time: 2019/1/28
# @File: valid_test.py

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


class RunTest(RunCmd):

    def __init__(self, **kwargs):
        self.logger = kwargs["logger"]
        super().__init__(self.logger)
        self.kwargs = kwargs["data"]
        self.args = {"host": self.kwargs["host"], "user": self.kwargs["user"], "port": self.kwargs["port"], "key": self.kwargs["key"]}

    def deploy(self):
        for action in ["stop", "clean", "init"]:
            args = {'sub': 'deploy', 'config': self.kwargs["config_file"], 'action': action}
            deploy = EveryOne(args, self.logger)
            result = deploy.do_deploy()
            if result:
                print(result)
                sys.exit(1)
            DeployNode.wait(2)

    def cmd_run(self):
        accname = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.args["accname"] = accname
        self.args["nick"] = "3005"
        self.args["type"] = "ecc"
        self.args["noderpcaddr"] = "127.0.0.1"
        self.args["noderpcport"] = 40001
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
        self.args["amount"] = 200
        self.args["from"] = root_address
        self.args["toaddr"] = address
        self.run("send", self.logger)
        # 获取账户信息
        DeployNode.wait(3)
        self.run("getaccount", self.logger)

    def rpc_run(self):
        self.args["port"] = 60002
        # 获取质押信息
        DeployNode.wait(5)
        start_echo = "[ GetDepositAccount ] [RPC]".center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        self.args["accounts"] = self.kwargs["accounts"]
        getdepositaccount = GetDepositAccount(self.logger)
        getdepositaccount.args = self.args
        getdepositaccount.args["field"] = None
        deposit_result = getdepositaccount.run()
        print(deposit_result)
        self.logger.info(deposit_result)
        # 获取账户信息
        DeployNode.wait(5)
        for rpc_port in self.kwargs["rpc_ports"].split(","):
            self.args["port"] = int(rpc_port)
            start_echo = "[ GetAccountByAddr ] [RPC] <{}>".format(rpc_port).center(80, "*")
            print(start_echo)
            getaccountbyname = GetAccountByAddr(self.logger)
            getaccountbyname.args = self.args
            getaccountbyname.args["addr"] = self.args["address"]
            get_account_result = getaccountbyname.run()
            print(get_account_result)
            self.logger.info(get_account_result)

    def other_run(self):
        # 获取出块比例
        self.args["port"] = 60002
        get_scale = GetDepositScale(self.logger)
        get_scale.args = self.args
        get_scale_result = get_scale.run()
        print(get_scale_result)

    def start(self):
        self.deploy()
        DeployNode.wait(5)
        self.cmd_run()
        self.rpc_run()
        DeployNode.wait(500)
        self.other_run()


if __name__ == "__main__":
    data = {
        "host": "10.15.101.114",
        "config_file": "config.ini",
        "user": "root",
        "port": 22,
        "key": os.path.join(CONFIGDIR, "id_rsa_jump"),
        "accounts": "root,3006,3007",
        "rpc_ports": "60002,60012,60022"
    }  # accounts用来请求质押比例时所需的账户，rpc_ports用来验证多个节点数据相同时用到
    logfile_name = "test_{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M"))
    logger = Logger(logfile_name)
    logger.info("< Start test >".center(100, "*"))
    do_test = RunTest(data=data, logger=logger)
    try:
        do_test.start()
    except KeyboardInterrupt:
        sys.exit("Exit.")
    finally:
        logger.info("< End test >".center(100, "*"))

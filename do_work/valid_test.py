# -*- coding: utf-8 -*-
# @Time: 2019/1/28
# @File: valid_test.py

import datetime
import sys
import os
import random

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
from rpc_client.GetNodeStatus import GetNodeStatus
from main.deploy_tools import Config
from rpc_client.GetBlockInfoByHeight import GetBlockInfoByHeight


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

    def block_out(self):
        # 获取出块比例
        self.args["port"] = self.kwargs["genesis_port"]
        get_scale = GetDepositScale(self.logger)
        get_scale.args = self.args
        get_scale_result = get_scale.run()
        print(get_scale_result)

    def valid_node(self):
        # 停止节点
        self.args["port"] = self.kwargs["port"]
        self.args["id"] = self.kwargs["id"]
        start_echo = "stop noded [ {} ]".format(self.args["id"]).center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        self.run("stop_node", self.logger)
        DeployNode.wait(2)
        # 启动节点
        self.args["port"] = self.kwargs["port"]
        self.args["config_file"] = self.kwargs["config_file"]
        start_echo = "start noded [ {} ]".format(self.args["id"]).center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        self.run("start_node", self.logger)
        DeployNode.wait(15)
        # 获取节点信息
        start_echo = "[ GetNodeStatus <- {id} ] [RPC]".format(**self.kwargs).center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        getnodestatus_result = self.get_node_status(self.args["host"], self.kwargs["node_port"])
        print(getnodestatus_result)
        self.logger.info(getnodestatus_result)
        # 获取创世节点信息
        start_echo = "[ GetNodeStatus <- genesis ] [RPC]".center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        getnodestatus_result = self.get_node_status(self.kwargs["host"], self.kwargs["genesis_port"])
        print(getnodestatus_result)
        self.logger.info(getnodestatus_result)

    def compare_block(self):

        """
        在指定的节点中[compare_node]，随机对比10个block的信息是否相同
        """

        start_echo = "compare block info".center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        getnodestatus_result = self.get_node_status(self.kwargs["host"], self.kwargs["genesis_port"])
        height = int(getnodestatus_result["Height"])
        self.logger.info(getnodestatus_result)
        echo = "Current block heigh : [ {} ]".format(height).center(80, "*")
        print(echo)
        self.logger.info(echo)
        config = Config(self.kwargs["config_file"]).read_config()
        for i in range(10):
            data = []
            num = random.randint(0, height)
            for node in self.kwargs["compare_node"].split(","):
                getblockinfo = GetBlockInfoByHeight(self.logger)
                node_info = config[node]
                getblockinfo.args["host"] = node_info["address"]
                getblockinfo.args["port"] = int(node_info["rpc_port"])
                getblockinfo.args["number"] = num
                result = getblockinfo.run()
                data.append(result)
            else:
                for value in data:
                    if value != data[0]:
                        echo = "[ {} ] False".format(num)
                        self.logger.error(echo)
                        print(echo)
                        break
                else:
                    echo = "[ {} ] True".format(num)
                    self.logger.info(echo)
                    print(echo)

    def check_block(self):

        """
        检测每个块的信息是否正确：包含前一个块的Hash值，块高度递增，块的时间戳严格递增
        """

        start_echo = "check block info".center(80, "*")
        self.logger.info(start_echo)
        print(start_echo)
        hash_list = ["0x00000000000000000000000000000000000000000000000000000000000000000000000000000000"]
        nodestatus = self.get_node_status(self.kwargs["host"], self.kwargs["genesis_port"])
        height = int(nodestatus["Height"])
        for i in range(height + 1):
            getblockinfo = GetBlockInfoByHeight(self.logger)
            getblockinfo.args["host"] = self.kwargs["host"]
            getblockinfo.args["port"] = int(self.kwargs["genesis_port"])
            getblockinfo.args["number"] = i
            result = getblockinfo.run()
            pre_hash, current_hash, num, btime = result["PreBlockID"], result["ID"], result["Height"], result["BlockTime"]
            self.logger.debug("Height: {} PRE: {} CURR: {}".format(num, pre_hash, current_hash))
            if int(num) != i:  # 检查块高度是否正确
                echo = "block height error : {}".format(result)
                self.logger.error(echo)
                print(echo)
                break
            if pre_hash == hash_list[i]:  # 检查是否记录上一个块的HASH值
                hash_list.append(current_hash)
                echo = "[{} hash] -> True".format(i)
                self.logger.info(echo)
            else:
                echo = "[{} hash] -> False".format(i)
                self.logger.error(echo)
                print(echo)
                break
            if i > 1:
                time_diff, sign = self.compare_time(pre_block_time, btime)
                if not sign:
                    echo = "[{} time interval: {}] -> False".format(i, time_diff)
                    self.logger.error(echo)
                    print(echo)
            pre_block_time = btime
            sys.stdout.write("[{}]-".format(i))
            sys.stdout.flush()
        else:
            print("Now...")

    def get_node_status(self, host, port):
        getnodestatus = GetNodeStatus(self.logger)
        getnodestatus.args["host"] = host
        getnodestatus.args["port"] = port
        getnodestatus_result = getnodestatus.run()
        return getnodestatus_result

    def compare_time(self, pre_time, curr_time):
        """
        与前一个块的时间做对比，严格按照出块时间来计算
        """
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        pre_time = datetime.datetime.strptime(pre_time, time_format)
        curr_time = datetime.datetime.strptime(curr_time, time_format)
        time_diff = (curr_time - pre_time).seconds
        if time_diff != self.kwargs["time_interval"]:
            return time_diff, False
        else:
            return time_diff, True

    def start(self):
        self.deploy()
        DeployNode.wait(5)
        self.cmd_run()
        self.rpc_run()
        DeployNode.wait(300)
        self.block_out()
        self.valid_node()
        self.compare_block()
        self.check_block()


if __name__ == "__main__":
    # accounts用来请求质押比例时所需的账户，rpc_ports用来验证多个节点数据相同时用到，
    # id用来选择关闭指定的节点，node_port是noded的RPC端口，genesis_port是genesis noded的RPC端口,
    # time_interval出块时间间隔
    data = {
        "host": "10.15.101.114",
        "config_file": "config.ini",
        "user": "root",
        "port": 22,
        "key": os.path.join(CONFIGDIR, "id_rsa_jump"),
        "accounts": "root,3006,3007,3008",
        "rpc_ports": "60002,60012,60022",
        "id": "node02",
        "node_port": 60022,
        "genesis_port": 60002,
        "compare_node": "cli1,cli2,cli4",
        "time_interval": 2
    }
    logfile_name = "test_{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M"))
    logger = Logger(logfile_name, 30)
    logger.info("< Start test >".center(100, "*"))
    do_test = RunTest(data=data, logger=logger)
    try:
        do_test.start()
    except KeyboardInterrupt as e:
        logger.warning(e)
        sys.exit("Exit.")
    except Exception as e:
        print(e)
        logger.error(str(e))
    finally:
        logger.info("< End test >".center(100, "*"))

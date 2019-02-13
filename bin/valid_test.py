# -*- coding: utf-8 -*-
# @Time: 2019/1/28
# @File: valid_test.py

import datetime
import sys
import os
import random
import re

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from cmd_client.cmd_base import RunCmd
from rpc_client.GetDepositAccount import GetDepositAccount
from rpc_client.GetAccountByAddr import GetAccountByAddr
from main.bin_tools import EveryOne
from main.deploy_tools import DeployNode
from rpc_client.GetDepositScale import GetDepositScale
from main.logger import Logger
from rpc_client.GetNodeStatus import GetNodeStatus
from main.deploy_tools import Config
from rpc_client.GetBlockInfoByHeight import GetBlockInfoByHeight


class RunTest(RunCmd):

    def __init__(self, **kwargs):
        self.logger = kwargs["logger"]
        super().__init__(self.logger)
        self.kwargs = kwargs["data"]
        self.config = Config(self.kwargs["config_file"]).read_config()
        genesis_node = self.config["genesis"]
        self.args = {"host": genesis_node["address"], "user": genesis_node["ssh_user"], "port": genesis_node["ssh_port"], "key": self.kwargs["key"]}

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
        self.args["amount"] = self.kwargs["amount"]
        self.args["from"] = root_address
        self.args["toaddr"] = address
        self.run("send", self.logger)
        # 获取账户信息
        DeployNode.wait(3)
        result = self.run("getaccount", self.logger)
        balance = re.findall(r"Balance:(\d+?),", result)
        if balance:
            if balance[0] != self.kwargs["amount"]:
                echo = "Transfer failed, amount varies: {}".format(result)
                self.logger.error(echo)
                print(echo)
        else:
            echo = "Transfer failed, amount varies: {}".format(result)
            self.logger.error(echo)
            print(echo)

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
        cli_list = [x for x in self.config if x.startswith("cli")]
        for cli in cli_list:
            self.args["port"] = int(self.config[cli]["rpc_port"])
            self.args["host"] = self.config[cli]["address"]
            start_echo = "[ GetAccountByAddr ] [RPC] <{}>".format(self.config[cli]["rpc_port"]).center(80, "*")
            self.logger.info(start_echo)
            print(start_echo)
            getaccountbyaddr = GetAccountByAddr(self.logger)
            getaccountbyaddr.args = self.args
            getaccountbyaddr.args["addr"] = self.args["address"]
            getaccountbyaddr_result = getaccountbyaddr.run()
            self.logger.info(getaccountbyaddr_result)
            print(getaccountbyaddr_result)

    def block_out(self):
        # 获取出块比例
        self.args["port"] = int(self.config["genesis"]["cli_rpc_port"])
        get_scale = GetDepositScale(self.logger)
        get_scale.args = self.args
        get_scale_result = get_scale.run()
        print(get_scale_result)

    def valid_node(self):
        # 停止节点
        self.args["host"] = self.config[self.kwargs["id"]]["address"]
        self.args["port"] = self.config[self.kwargs["id"]]["ssh_port"]
        self.args["id"] = self.kwargs["id"]
        start_echo = "stop noded [ {} ]".format(self.args["id"]).center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        self.run("stop_node", self.logger)
        DeployNode.wait(10)
        # 启动节点
        start_cmd = self.config[self.kwargs["id"]]["start_cmd"]
        start_echo = "start noded [ {} ]".format(self.args["id"]).center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        self.run("start_node", self.logger, start_cmd=start_cmd)
        DeployNode.wait(8)
        # 获取节点信息
        start_echo = "[ GetNodeStatus <- {id} ] [RPC]".format(**self.kwargs).center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        getnodestatus_result = self.get_node_status(self.config[self.kwargs["id"]]["address"], int(self.config[self.kwargs["id"]]["cli_rpc_port"]))
        self.logger.info(getnodestatus_result)
        print(getnodestatus_result)
        # 获取创世节点信息
        start_echo = "[ GetNodeStatus <- genesis ] [RPC]".center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        getgenesisstatus_result = self.get_node_status(self.config["genesis"]["address"], int(self.config["genesis"]["cli_rpc_port"]))
        self.logger.info(getgenesisstatus_result)
        print(getgenesisstatus_result)
        if getnodestatus_result["Height"] != getgenesisstatus_result["Height"]:  # 检查块高度是否相等
            echo = "Height mismatch [{} : {}] [genesis : {}]".format(self.kwargs["id"], getnodestatus_result["Height"], getgenesisstatus_result["Height"])
            self.logger.error(echo)
            print(echo)

    def compare_block(self):

        """
        随机对比20个block的信息在所有节点中是否相同
        """

        start_echo = "compare block info".center(80, "*")
        print(start_echo)
        self.logger.info(start_echo)
        getnodestatus_result = self.get_node_status(self.config["genesis"]["address"], int(self.config["genesis"]["cli_rpc_port"]))
        height = int(getnodestatus_result["Height"])
        self.logger.info(getnodestatus_result)
        echo = "Current block heigh : [ {} ]".format(height).center(80, "*")
        print(echo)
        self.logger.info(echo)
        node_list = ["genesis"]
        for key in self.config:
            if key.startswith("node"):
                node_list.append(key)
        for i in range(20):
            data = []
            num = random.randint(0, height)
            for node in node_list:
                getblockinfo = GetBlockInfoByHeight(self.logger)
                node_info = self.config[node]
                getblockinfo.args["host"] = node_info["address"]
                getblockinfo.args["port"] = int(node_info["cli_rpc_port"])
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
        检测每个块的信息是否正确：包含前一个块的Hash值，块高度递增，块的时间严格递增
        """

        start_echo = "check block info".center(80, "*")
        self.logger.info(start_echo)
        print(start_echo)
        hash_list = ["0x00000000000000000000000000000000000000000000000000000000000000000000000000000000"]
        nodestatus = self.get_node_status(self.config["genesis"]["address"], int(self.config["genesis"]["cli_rpc_port"]))
        height = int(nodestatus["Height"])
        for i in range(height + 1):
            getblockinfo = GetBlockInfoByHeight(self.logger)
            getblockinfo.args["host"] = self.config["genesis"]["address"]
            getblockinfo.args["port"] = int(self.config["genesis"]["cli_rpc_port"])
            getblockinfo.args["number"] = i
            result = getblockinfo.run()
            pre_hash, current_hash, num, btime = result["PreBlockID"], result["ID"], result["Height"], result["BlockTime"]
            self.logger.debug("Height: {} PRE: {} CURR: {}".format(num, pre_hash, current_hash))
            if int(num) != i:  # 检查块高度是否正确
                echo = "block height error : {}".format(result)
                self.logger.error(echo)
                print(echo)
                break
            if current_hash in hash_list:  # 检查hash值是否重复
                echo = "[{} Repeat_hash <{}> {}] -> False".format(i, hash_list.index(current_hash), current_hash)
                print(echo)
                self.logger.error(echo)
            else:
                echo = "[{} Repeat_hash] -> True".format(i)
                self.logger.info(echo)
            if pre_hash == hash_list[i]:  # 检查是否记录上一个块的HASH值
                echo = "[{} Pre_hash] -> True".format(i)
                self.logger.info(echo)
            else:
                echo = "[{} Pre_hash Error: idle [{}] real [{}]] -> False".format(i, hash_list[i], pre_hash)
                self.logger.error(echo)
                print(echo)
                break
            if i > 1:  # 检查块时间是否按严格按照出块时间递增
                time_diff, sign = self.compare_time(pre_block_time, btime)
                if not sign:
                    echo = "[{} time interval: {}] -> False".format(i, time_diff)
                    self.logger.error(echo)
                    print(echo)
            pre_block_time = btime
            hash_list.append(current_hash)
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
    data = {
        "config_file": "config.ini",  # 配置文件名，路径在 ../conf/
        "key": os.path.join(CONFIGDIR, "id_rsa_jump"),  # ssh远程的登陆的key
        "accounts": "root,3006,3007,3008",  # 用来计算出块比例
        "id": "node02",  # 用来选择关闭、启动的节点
        "time_interval": 2,  # 出块时间间隔，单位s
        "amount": "200"  # 转账金额
    }
    logfile_name = "test_{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M"))
    logger = Logger(logfile_name, 30)  # 30 代表 error
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

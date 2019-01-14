# -*- coding: utf-8 -*-
# @Time: 2018/12/28
# @File: bin_tools

from main.deploy_tools import Config, check_file_exists, check_action_result, DeployNode, DeployCli, Deposit
from main.test_api import RunApi, ApiTestData
from tools.remote_exec import RunCmd
import os
import sys
import json

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)


class EveryOne(object):
    """
    启动接口
    """

    def __init__(self, args):
        self.args = args

    def do_generate_config(self):
        """
        生成配置文件
        """
        config = Config(self.args["filename"])
        config.generate_config()
        return 0

    def do_testapi(self):
        """
        测试RPC接口
        """
        api = RunApi(self.args["host"], self.args["port"], self.args["method"], self.args["sign"])
        result = api.cli_api()
        if isinstance(result, dict):  # 有值
            print(json.dumps(result, indent=2))
            return 0
        else:
            print(result)
            return 1

    def do_monitapi(self):
        """
        定时返回RPC接口信息
        """
        api = RunApi(self.args["host"], self.args["port"], self.args["method"], self.args["sign"])
        api.monit_result(self.args["interval"], self.args["total"])
        return

    def do_list(self):
        """
        打印RPC接口或配置文件内容
        """
        if self.args["listobj"] == "api":
            data = [x for x in ApiTestData().rpc_data.keys() if x != "header"]
            print(data)
            return 0
        elif self.args["listobj"] == "config":
            configobj = Config(self.args["config"])
            err = configobj.list_config()
            if err:
                print("Error: %s" % err)
            return 1 if err else 0

    def do_cmd(self):
        """
        单独执行cli或noded命令
        """
        remote_exec = RunCmd(self.args["attach"], self.args["host"])
        exec_result = remote_exec.run_cmd()
        print(exec_result)
        return 0

    def do_deploy(self):
        """
        操作noded和cli，重置(reset)、启动(start)、关闭(stop)、清除数据(clean)
        依据配置文件内容，顺序执行，每执行完一个都需要对结果进行检查
        """
        action = self.args["action"]
        node_list, cli_list = [], []
        config = self.do_read_config()
        node_list.extend([x for x in config.keys() if x.startswith("node")])
        if "genesis" in config:
            genesis = DeployNode(config["genesis"], config["genesis"])
            genesis_result = getattr(genesis, action, DeployNode.echo)()
            check_action_result(genesis_result, config["genesis"], action)
            if action in ["reset", "start", "init"]:
                DeployNode.wait(2)
        for node in node_list:
            noded_obj = DeployNode(config["genesis"], config[node])
            noded_result = getattr(noded_obj, action, DeployNode.echo)()
            check_action_result(noded_result, config[node], action)
        if action == "init":
            DeployNode.wait(3)
            for node in node_list:
                print(("Start deposit... [%s]" % node).center(50, '*'))
                if config[node].getboolean("deposit"):
                    deposit = Deposit(config["genesis"], config[node])
                    deposit.send()
                    deposit_id = deposit.deposit()
                    print("Deposit id [%s]: %s" % (config[node]["id"], deposit_id))
        cli_list.extend([x for x in config.keys() if x.startswith("cli")])
        for cli in cli_list:
            client = DeployCli(config[cli])
            client_result = getattr(client, action, DeployNode.echo)()
            check_action_result(client_result, config[cli], action)
        return 0

    def do_read_config(self):
        """
        读取配置
        """
        check_file_exists(os.path.join(CONFIGDIR, self.args["config"]))
        configobj = Config(self.args["config"])
        config = configobj.read_config()
        return config

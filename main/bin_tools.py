# -*- coding: utf-8 -*-
# @Time: 2018/12/28
# @File: bin_tools

from main.deploy_tools import Config, check_file_exists, check_action_result, DeployNode, DeployCli, Deposit
from main.test_api import RunApi, ApiTestData
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

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

    def do_generate_config(self):
        """
        生成配置文件
        """
        self.logger.info("generate config file [ {} ]".format(self.args["filename"]))
        config = Config(self.args["filename"])
        config.generate_config()
        return 0

    def do_testapi(self):
        """
        测试RPC接口
        """
        api = RunApi(self.args["host"], self.args["port"], self.args["method"], self.args["sign"], self.logger)
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
        api = RunApi(self.args["host"], self.args["port"], self.args["method"], self.args["sign"], self.logger)
        self.logger.info("Start monit result, total time is {total} seconds, once every {interval} seconds".format(**self.args))
        api.monit_result(self.args["interval"], self.args["total"])
        return

    def do_list(self):
        """
        打印RPC接口或配置文件内容
        """
        if self.args["listobj"] == "api":
            self.logger.info("[I] list api")
            data = [x for x in ApiTestData().rpc_data.keys() if x != "header"]
            print(data)
            self.logger.info("[O] {}".format(data))
            return 0
        elif self.args["listobj"] == "config":
            self.logger.info("[I] print config")
            configobj = Config(self.args["config"])
            data = configobj.list_config()
            if not data:  # 读取文件失败
                self.logger.error("This file was not found [ {} ]".format(self.args["config"]))
                return 1
            for line in data:
                print(line)
            return 0

    def do_deploy(self):
        """
        操作noded和cli，重置(reset)、启动(start)、关闭(stop)、清除数据(clean)
        依据配置文件内容，顺序执行，每执行完一个都需要对结果进行检查
        """
        action = self.args["action"]
        node_list, cli_list = [], []
        config = self.do_read_config()
        if not config:
            data = "read config file [{}] failed.".format(self.args["config"])
            self.logger.error(data)
            return data
        else:
            node_list.extend([x for x in config.keys() if x.startswith("node")])
            cli_list.extend([x for x in config.keys() if x.startswith("cli")])
            if action == "stop":  # stop，先stop cli，之后stop noded
                for cli in cli_list:
                    client = DeployCli(config[cli], self.logger)
                    client_result = getattr(client, action, DeployNode.echo)()
                    check_action_result(client_result, config[cli], action, self.logger)
                else:
                    if "genesis" in config:
                        node_list.insert(0, "genesis")
                        for node in node_list:
                            noded_obj = DeployNode(config[node], self.logger)
                            noded_result = getattr(noded_obj, action, DeployNode.echo)()
                            check_action_result(noded_result, config[node], action, self.logger)
            else:  # 除了stop动作之外，都是先操作noded，然后是cli
                if "genesis" in config:
                    genesis = DeployNode(config["genesis"], self.logger)
                    genesis_result = getattr(genesis, action, DeployNode.echo)()
                    check_action_result(genesis_result, config["genesis"], action, self.logger)
                    if action in ["reset", "start", "init"]:
                        DeployNode.wait(5)
                for node in node_list:
                    noded_obj = DeployNode(config[node], self.logger)
                    noded_result = getattr(noded_obj, action, DeployNode.echo)()
                    check_action_result(noded_result, config[node], action, self.logger)
                if action == "init":
                    DeployNode.wait(6)
                    for node in node_list:
                        if config[node].getboolean("deposit"):
                            print(("Start deposit... [%s]" % node).center(50, '*'))
                            deposit = Deposit(config["genesis"], config[node], self.logger)
                            deposit.send()
                            deposit_id = deposit.deposit()
                            print("Deposit id [%s]: %s" % (config[node]["id"], deposit_id))
                            DeployNode.wait(3)
                for cli in cli_list:
                    client = DeployCli(config[cli], self.logger)
                    client_result = getattr(client, action, DeployNode.echo)()
                    check_action_result(client_result, config[cli], action, self.logger)
            return 0

    def do_read_config(self):
        """
        读取配置
        """
        filename = os.path.join(CONFIGDIR, self.args["config"])
        self.logger.info("Check file: {}".format(filename))
        check_result = check_file_exists(filename)
        if check_result != filename:
            self.logger.error(check_result)
            return
        configobj = Config(self.args["config"])
        config = configobj.read_config()
        return config

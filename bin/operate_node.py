# -*- coding: utf-8 -*-
# @Time: 2019/2/14
# @File: operate_node

import sys
import os
import datetime
import random

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.deploy_tools import DeployNode, DeployCli, Config, check_action_result
from main.logger import Logger
from rpc_client.GetNodeStatus import GetNodeStatus


class OperateNode(object):

    def __init__(self, config_file="config.ini"):
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        self.logger = Logger("action_{}.log".format(now))
        self.config = Config(config_file).read_config()
        self.time_wait = 10

    def operate_node(self, action):
        node_conf = self.config[self.node]
        echo = "{} {} [{}:{}]".format(
            action, self.node, self.config[self.node]["address"],
            self.config[self.node["cli_rpc_port"]]).center(80, "*")
        self.logger.info(echo)
        print(echo)
        action_obj = DeployNode(node_conf, self.logger)
        action_result = getattr(action_obj, action, DeployNode.echo)()
        return check_action_result(action_result, node_conf, action, self.logger)

    # def operate_cli(self, action):
    #     cli_conf = self.config[self.cli]
    #     echo = "{} {} [{}:{}]".format(
    #         action, self.cli, self.config[self.cli]["address"],
    #         self.config[self.cli["rpc_port"]]).center(80, "*")
    #     self.logger.info(echo)
    #     print(echo)
    #     cli_obj = DeployCli(cli_conf, self.logger)
    #     cli_result = getattr(cli_obj, action, DeployNode.echo)()
    #     return check_action_result(cli_result, cli_conf, action, self.logger)

    def action(self):
        self.operate_node("stop")
        DeployNode.wait(self.time_wait)
        self.operate_node("start")
        DeployNode.wait(self.time_wait)
        self.compare_height()

    def get_block_height(self, node):
        args = {
            "host": self.config[node]["address"],
            "port": self.config[node]["cli_rpc_port"]
        }
        get_status = GetNodeStatus(self.logger)
        get_status.args = args
        return get_status.run()

    def compare_height(self):
        node_status = self.get_block_height(self.node)
        genesis_status = self.get_block_height("genesis")
        if all([node_status, genesis_status]):
            if "Height" in node_status and "Height" in genesis_status:
                height_diff = abs(int(genesis_status["Height"]) - int(node_status["Height"]))
                echo = "block height is different: genesis:[{}] {}: [{}] diff: [{}]".format(
                    genesis_status["Height"], self.node, node_status["Height"], height_diff)
                if height_diff:
                    self.logger.error(echo)
                else:
                    self.logger.info(echo)
                print(echo)
                return echo
        echo = "get block height faild. genesis: [{}], {}: [{}]".format(
            self.config["genesis"]["address"], self.config["genesis"]["cli_rpc_port"],
            self.config[self.node]["address"], self.config[self.node]["cli_rpc_port"])
        self.logger.error(echo)
        print(echo)
        return echo

    def run(self):
        node_list = [x for x in self.config.keys() if x.startswith("node")]
        for i in range(10):  # 循环执行10次关停再启动的操作
            self.node = random.sample(node_list, 1)[0]
            self.action()
            DeployNode.wait(self.time_wait)


if __name__ == "__main__":
    operate = OperateNode()
    operate.run()

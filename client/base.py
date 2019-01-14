# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: base.py

import argparse
import sys
import os
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.test_api import RunApi
from main.deploy_tools import DeployNode, DeployCli, Config, check_action_result


class RPCTest(object):
    """
    RPC测试基类，继承时只需编写status方法即可
    """

    def __init__(self):
        self.start_method = ""
        self.start_sign = ""
        self.stop_method = ""
        self.stop_sign = ""
        self.status_method = ""
        self.status_sign = ""
        self.arg = self.get_args()
        self.args = None

    @staticmethod
    def get_args():
        default_config_file = os.path.join(CONFIGDIR, "config.ini")
        arg = argparse.ArgumentParser(prog="测试")
        arg.add_argument("host", type=str, help="服务器地址")
        arg.add_argument("port", type=int, help="服务器端口")
        arg.add_argument("-c", "--config", type=str,
            help="config file name, the file directory is %s , Default: %s" % (
            CONFIGDIR, default_config_file), default=default_config_file, required=True)
        return arg

    def deploy(self, action):
        node_list, cli_list = ["genesis"], []
        config = Config(self.args["config"]).read_config()
        node_list.extend([x for x in config.keys() if x.startswith("node")])
        cli_list.extend([x for x in config.keys() if x.startswith("cli")])
        for node in node_list:
            noded = DeployNode(config["genesis"], config[node])
            noded_result = getattr(noded, action, DeployNode.echo)()
            check_action_result(noded_result, config[node], action)
        for cli in cli_list:
            client = DeployCli(config[cli])
            client_result = getattr(client, action, DeployNode.echo)()
            check_action_result(client_result, config[cli], action)

    def check_service(self):
        """
        检查noded和cli是否正常运行(status)，否则对noded和cli执行初始化(reset)操作
        """
        try:
            self.deploy("status")
        except SystemExit:
            self.deploy("reset")

    def get_test_obj(self, method, sign):
        func = RunApi(self.args["host"], self.args["port"], method, sign)
        return func

    def start(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        start_result = func.cli_api()
        self.check(self.start_method, start_result)

    def status(self):
        """
        每个继承的RPC测试，都需要重写status方法
        """
        pass

    def check(self, method, result):
        if result:
            print("%s start failed: %s" % (method, result))
            sys.exit()
        else:
            print("%s started..." % method)

    def stop(self):
        func = self.get_test_obj(self.stop_method, self.stop_sign)
        stop_result = func.cli_api()
        self.check(self.stop_method, stop_result)

    def run(self):
        self.check_service()
        self.stop()
        self.start()
        self.status()
        self.stop()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

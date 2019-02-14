# -*- coding: utf-8 -*-
# @Time: 2018/12/29
# @File: base.py

"""
RPC接口测试的基类
"""

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

    def __init__(self, logger):
        """
        如果测试会自动结束，则除了重写status方法外，也要重写run方法
        """
        self.start_method = ""  # 执行测试的接口名
        self.start_sign = ""  # 如果同一接口包含多种body体，需要指定
        self.stop_method = ""  # 停止测试的接口名
        self.stop_sign = ""  # 同 self.start_sign
        self.status_method = ""  # 获取状态的接口名
        self.status_sign = ""  # 同 self.start_sign
        self.arg = self.get_args()
        self.args = {}
        self.logger = logger

    @staticmethod
    def get_args():
        arg = argparse.ArgumentParser(prog="RPC测试")
        arg.add_argument("host", type=str, help="服务器地址")
        arg.add_argument("port", type=int, help="服务器端口")
        return arg

    def deploy(self, action):
        node_list, cli_list = ["genesis"], []
        config = Config(self.args["config"]).read_config()
        self.logger.info("load config [ {} ]".format(self.args["config"]))
        node_list.extend([x for x in config.keys() if x.startswith("node")])
        cli_list.extend([x for x in config.keys() if x.startswith("cli")])
        for node in node_list:
            noded = DeployNode(config[node], self.logger)
            noded_result = getattr(noded, action, DeployNode.echo)()
            check_action_result(noded_result, config[node], action, self.logger)
        for cli in cli_list:
            client = DeployCli(config[cli], self.logger)
            client_result = getattr(client, action, DeployNode.echo)()
            check_action_result(client_result, config[cli], action, self.logger)

    def check_service(self):
        """
        检查noded和cli是否正常运行(status)，否则对noded和cli执行初始化(reset)操作
        """
        try:
            self.deploy("status")
        except SystemExit:
            self.deploy("stop")
            self.deploy("clean")
            self.deploy("init")

    def get_test_obj(self, method, sign):
        func = RunApi(self.args["host"], self.args["port"], method, sign, self.logger)
        return func

    def start(self):
        func = self.get_test_obj(self.start_method, self.start_sign)
        start_result = func.cli_api()
        return start_result

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
        # self.check_service()  # 用来检测配置文件中指定的服务是否启动，如果没有启动，则会尝试初始化环境
        self.stop()
        self.start()
        return self.status()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

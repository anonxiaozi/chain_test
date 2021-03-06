# -*- coding: utf-8 -*-
# @Time: 2019/1/24
# @File: cmd_base.py

import sys
import os
import argparse

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.remote_exec import MySSH
from main.logger import Logger


class RunCmd(object):

    def __init__(self, logger):
        self.args = None
        self.check = True
        self.logger = logger

    @staticmethod
    def get_args():
        arg = argparse.ArgumentParser(prog="CMD测试")
        arg.add_argument("-d", "--host", type=str, help="服务器地址,默认为: %(default)s", default="10.15.101.114")
        arg.add_argument("-p", "--port", type=int, help="服务器端口,默认为: %(default)s", default=22)
        arg.add_argument("-u", "--user", help="SSH登陆用户名，默认为: %(default)s", default="root")
        arg.add_argument("-k", "--key", type=str, help="SSH密钥存放位置，默认为:%(default)s", default=os.path.join(CONFIGDIR, "id_rsa_jump"), required=False)
        arg.add_argument("--data-path", type=str, help="数据目录路径，默认为：%(default)s", default="/root/.pb_data", required=False)
        return arg

    def get_ssh(self):
        self.ssh = MySSH(self.args["host"], self.args["user"], self.args["key"], self.args["port"], self.logger)
        self.ssh.login_auth()

    def createwallet_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--accname", help="钱包名", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--type", choices=["ecc", "bls"], help="钱包类型 [ecc, bls],默认为: %(default)s", default="ecc")

    def createwallet(self):
        self.get_ssh()
        createwallet_cmd = "cli createwallet -dev 1 -accname {accname} -nick {nick} -type {type} | " \
                           "grep INFO | tail -n 1 | awk -F'client_{nick}: ' '{{print $2}}'".format(**self.args)
        return self.ssh.remote_exec(createwallet_cmd, self.check)

    def createaccount_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--address", help="钱包地址", required=True)
        self.arg.add_argument("--creatoraddr", help="创建者地址", required=True)
        self.arg.add_argument("--accname", help="新的账户名", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--noderpcaddr", help="节点地址，默认为: %(default)s", default="127.0.0.1")
        self.arg.add_argument("--noderpcport", type=int, help="节点端口，默认为: %(default)s", default=40001)

    def createaccount(self):
        self.get_ssh()
        createaccount_cmd = "cli createaccount -address {address} -creatoraddr {creatoraddr} -dev 1 -name {accname} -nick {nick} -noderpcaddr {noderpcaddr} " \
                            "-noderpcport {noderpcport}".format(**self.args)
        return self.ssh.remote_exec(createaccount_cmd, self.check)

    def listaccounts_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")

    def listaccounts(self):
        self.get_ssh()
        listaccounts_cmd = "cli listaccounts -nick {nick}".format(**self.args)
        return self.ssh.remote_exec(listaccounts_cmd, self.check)

    def getwalletkey_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--name", help="钱包名称", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--type", choices=["ecc", "bls"], help="钱包类型：[ecc, bls]", required=True)

    def getwalletkey(self):
        self.get_ssh()
        getwalletkey_cmd = "cli getwalletkey -dev 1 -name {name} -nick {nick} -type {type} | grep INFO | tail -n 1 | awk -F'{nick}: ' '{{print $2}}'".format(**self.args)
        return self.ssh.remote_exec(getwalletkey_cmd, self.check)

    def convert_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--from", help="需要转换的内容", required=True)
        self.arg.add_argument("--method", choices=["pub2addr", "str2depositid"], help="转换使用的方法[pub2addr, str2depositid]，默认是: %(default)s", default="pub2addr")
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")

    def convert(self):
        self.get_ssh()
        convert_cmd = "cli convert -from {from} -method {method} -nick {nick} | grep INFO | tail -n 1 | awk -F'to depositid: ' '{{print $2}}'".format(**self.args)
        return self.ssh.remote_exec(convert_cmd, self.check).strip("{}")

    def send_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--amount", help="交易金额", type=int, required=True)
        self.arg.add_argument("--from", help="发送账户的地址", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--noderpcaddr", help="节点地址，默认为: %(default)s", default="127.0.0.1")
        self.arg.add_argument("--noderpcport", type=int, help="节点端口，默认为: %(default)s", default=40001)
        self.arg.add_argument("--toaddr", help="接收账户的地址", required=True)

    def send(self):
        self.get_ssh()
        send_cmd = "cli send -dev 1 -amount {amount} -from {from} -nick {nick} -toaddr {toaddr} " \
                   "-noderpcaddr {noderpcaddr} -noderpcport {noderpcport}".format(**self.args)
        return self.ssh.remote_exec(send_cmd, self.check)

    def deposit_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--amount", help="质押金额", type=int, required=True)
        self.arg.add_argument("--blsname", help="bls钱包名", required=True)
        self.arg.add_argument("--deposit", help="质押ID", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--noderpcaddr", help="节点地址，默认为: %(default)s", default="127.0.0.1")
        self.arg.add_argument("--noderpcport", type=int, help="节点端口，默认为: %(default)s", default=40001)
        self.arg.add_argument("--source", help="质押账户的地址", required=True)

    def deposit(self):
        self.get_ssh()
        deposit_cmd = "cli deposit -dev 1 -amount {amount} -blsname {blsname} -deposit {deposit} -nick {nick} -source {source} " \
                      "-noderpcaddr {noderpcaddr} -noderpcport {noderpcport}".format(**self.args)
        return self.ssh.remote_exec(deposit_cmd, self.check)

    def getaccount_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--addr", help="账户地址，不与 --name 同时使用")
        self.arg.add_argument("--accname", help="账户名称，不与 --addr 同时使用")
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--noderpcaddr", help="节点地址，默认为: %(default)s", default="127.0.0.1")
        self.arg.add_argument("--noderpcport", type=int, help="节点端口，默认为: %(default)s", default=40001)

    def getaccount(self):
        if "addr" in self.args:
            getaccount_cmd = "cli getaccount -addr {addr} -nick {nick} -noderpcaddr {noderpcaddr} -noderpcport {noderpcport} | " \
                             "grep '&AccountBriefInfo' | awk -F'&AccountBriefInfo' '{{print $2}}'".format(**self.args)
        elif "accname" in self.args:
            getaccount_cmd = "cli getaccount -name {accname} -nick {nick} -noderpcaddr {noderpcaddr} -noderpcport {noderpcport} | " \
                             "grep '&AccountBriefInfo' | awk -F'&AccountBriefInfo' '{{print $2}}'".format(**self.args)
        else:
            return "Invalid command."
        self.get_ssh()
        return self.ssh.remote_exec(getaccount_cmd, self.check)

    def getwalletinfo_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--accname", help="钱包名", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")

    def getwalletinfo(self):
        self.get_ssh()
        getwalletinfo_cmd = "cli getwalletinfo -accname {accname} -nick {nick} | grep INFO | awk -F'client_{nick}: address : ' '{{print $2}}'".format(**self.args)
        return self.ssh.remote_exec(getwalletinfo_cmd, self.check)

    def stop_node_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--id", help="标识配置文件中的节点ID", required=True)

    def stop_node(self):
        self.get_ssh()
        stop_node_cmd = "kill -9 `pgrep -a noded$ | grep '\-nick {id}' | awk '{{print $1}}'` &> /dev/null".format(**self.args)
        print("Bash: {}".format(stop_node_cmd))
        return self.ssh.remote_exec(stop_node_cmd, False)

    def start_node_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--id", help="标配置文件中的节点ID", required=True)

    def start_node(self, **kwargs):
        self.get_ssh()
        start_cmd = kwargs["start_cmd"]
        print("Bash: {}".format(start_cmd))
        return self.ssh.remote_exec(start_cmd, False)

    def echo(self):
        return "Invalid method"

    def run(self, method, logger, **kwargs):
        action_echo = ("[ {} ] [CMD]".format(method)).center(80, "*")
        print(action_echo)
        logger.info(action_echo)
        getattr(self, "{}_args".format(method), self.echo)()
        result = getattr(self, method, self.echo)(**kwargs)
        print(result)
        return result

    def __del__(self):
        try:
            self.ssh.__del__()
        except Exception:
            pass


if __name__ == "__main__":
    logger = Logger()
    method = "getwalletkey"
    run = RunCmd(logger)
    getattr(run, "%s_args" % method)()
    run.args = vars(run.arg.parse_args())
    result = getattr(run, method)()
    print(result)

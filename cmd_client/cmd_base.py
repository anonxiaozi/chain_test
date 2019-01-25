# -*- coding: utf-8 -*-
# @Time: 2019/1/24
# @File: cmd_base.py

import sys
import os
import argparse

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from tools.remote_exec import MySSH


class RunCmd(object):

    def __init__(self):
        self.args = None
        self.check = True

    @staticmethod
    def get_args():
        arg = argparse.ArgumentParser(prog="CMD测试")
        arg.add_argument("-d", "--host", type=str, help="服务器地址,默认为: %(default)s", default="10.15.101.77")
        arg.add_argument("-p", "--port", type=int, help="服务器端口,默认为: %(default)s", default=22)
        arg.add_argument("-u", "--user", help="SSH登陆用户名，默认为: %(default)s", default="root")
        arg.add_argument("-k", "--key", type=str, help="SSH密钥存放位置，默认为:%(default)s", default=os.path.join(CONFIGDIR, "id_rsa_jump"), required=False)
        return arg

    def get_ssh(self):
        self.ssh = MySSH(self.args["host"], self.args["user"], self.args["key"], self.args["port"])
        self.ssh.login_auth()

    def createwallet_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--accname", help="钱包名", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--type", choices=["ecc", "bls"], help="钱包类型 [ecc, bls],默认为: %(default)s", default="ecc")

    def createwallet(self):
        self.get_ssh()
        createwallet_cmd = "cli createwallet -dev 1 -accname {accname} -nick {nick} -type {type}".format(**self.args)
        return self.ssh.remote_exec(createwallet_cmd, self.check)

    def createaccount_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--accname", help="钱包名", required=True)
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")

    def createaccount(self):
        self.get_ssh()
        createaccount_cmd = "cli getwalletinfo -accname {accname} -nick {nick} | awk -F'address : ' '{{print $2}}'".format(**self.args)
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

    def getwalletkey(self):
        self.get_ssh()
        getwalletkey_cmd = "cli getwalletkey -dev 1 -name {name} -nick {nick} | grep INFO | tail -n 1 | awk -F'{nick}: ' '{{print $2}}'".format(**self.args)
        return self.ssh.remote_exec(getwalletkey_cmd, self.check)

    def convert_args(self):
        self.arg = self.get_args()
        self.arg.add_argument("--from", help="需要转换的内容", required=True)
        self.arg.add_argument("--method", choices=["pub2addr", "str2depositid"], help="转换使用的方法[pub2addr, str2depositid]，默认是: %(default)s", default="pub2addr")
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")

    def convert(self):
        self.get_ssh()
        convert_cmd = "cli convert -from {from} -method {method} -nick {nick} | grep INFO | tail -n 1 | awk -F'client_{nick}: ' '{{print $2}}'".format(**self.args)
        return self.ssh.remote_exec(convert_cmd, self.check)

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
        self.arg.add_argument("--name", help="账户名称，不与 --addr 同时使用")
        self.arg.add_argument("--nick", help="标识钱包id，默认为: %(default)s", default="pb")
        self.arg.add_argument("--noderpcaddr", help="节点地址，默认为: %(default)s", default="127.0.0.1")
        self.arg.add_argument("--noderpcport", type=int, help="节点端口，默认为: %(default)s", default=40001)

    def getaccount(self):
        if self.args["addr"]:
            getaccount_cmd = "cli getaccount -addr {addr} -nick {nick} -noderpcaddr {noderpcaddr} -noderpcport {noderpcport} | " \
                             "grep '&AccountBriefInfo' | awk -F'&AccountBriefInfo' '{{print $2}}'".format(**self.args)
        elif self.args["name"]:
            getaccount_cmd = "cli getaccount -name {name} -nick {nick} -noderpcaddr {noderpcaddr} -noderpcport {noderpcport} | " \
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

    def __del__(self):
        try:
            self.ssh.close()
        except Exception:
            pass


if __name__ == "__main__":
    method = "getwalletinfo"
    run = RunCmd()
    getattr(run, "%s_args" % method)()
    run.args = vars(run.arg.parse_args())
    result = getattr(run, method)()
    print(result)

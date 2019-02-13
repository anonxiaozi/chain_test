# -*- coding: utf-8 -*-
# @Time: 2019/1/17
# @File: GetDepositID

"""
通过质押账号获取对应的质押ID，输出结果为：
{'root': '6051053228330400958', '3005': '1423632669172846374', '3006': '9384355224946534474'}
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.remote_exec import MySSH
import re
import argparse
from main.logger import Logger


class GetDepositID(object):

    def __init__(self, logger):
        self.id_re = re.compile(r"client_pb:\s(\d{18,25})\s?")
        self.arg = argparse.ArgumentParser(prog="Get Deposit ID")
        self.arg.add_argument("host", type=str, help="服务器地址")
        self.arg.add_argument("port", type=int, help="服务器端口")
        self.arg.add_argument("-a", "--accounts", help="质押账号，多个账号用逗号分隔", required=True)
        self.args = {}
        self.logger = logger

    def status(self):
        ssh = MySSH(self.args["host"], username="root", keyfile=os.path.join(CONFIGDIR, "id_rsa_jump"), port=22, logger=self.logger)
        accounts = self.args["accounts"].split(",")
        if not accounts:
            return
        id_map = {x: None for x in accounts}
        for account in accounts:
            result = ssh.remote_exec("cd /root/work; ./cli convert -from %s -method str2depositid" % account)
            deposit_id = self.id_re.findall(result)
            if deposit_id:
                id_map[account] = deposit_id[0]
        return id_map

    def run(self):
        return self.status()


if __name__ == "__main__":
    logger = Logger()
    do = GetDepositID(logger)
    do.args = vars(do.arg.parse_args())
    id_map = do.run()
    print(id_map)

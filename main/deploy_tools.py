# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: deploy_tools

import mysql.connector
from mysql.connector import errorcode
import time
import sys
import re
import os
import random
import configparser
from tools.remote_exec import MySSH
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")


class DeployNode(MySSH):

    """
    操作noded，需要提供noded的配置信息(node_info)
    reset: 重置节点，stop -> clean -> init -> start
    stop: 停止节点
    clean: 清除node数据，包括：清除db、备份日志后清空日志、删除钱包
    start: 启动节点
    """

    stop_cmd = 'kill -9 $(pgrep noded$)'
    get_faild_info = "cd /root/work/logs; data=`ls -lt | grep node_%s | head -1 | awk '{print $NF}'`; if [ ! -z $data ]; then grep -i -E 'panic|warn' $data; else echo Nothing; fi"

    def __init__(self, node_info):
        super().__init__(node_info["address"], node_info["ssh_user"], node_info["ssh_key"], node_info.getint("ssh_port"))
        self.node_info = node_info

    def reset(self):
        """
        重置节点，首先stop，然后clean，之后init，最后start
        """
        self.stop()
        self.clean()
        self.init()

    def init(self):
        """
        初始化节点
        """
        mongo_status = self.check_mongo()
        if mongo_status:
            mongo_start = self.start_mongo()
            if mongo_start:
                return mongo_start
        result = self.remote_exec(self.node_info["init_cmd"])
        if result.startswith("[CheckWarning]"):
            return result
        elif result.split("\n")[-1] != "0":
            return result  # 初始化失败
        else:
            start_status = self.start()
            return start_status if start_status else None

    def clean(self):
        """
        清除noded数据
        """
        clean_cmd = "cd /root/work; ./noded clear -id %s" % self.node_info["id"] + "; tar zcf log_$(date +%Y%m%d%H%M).tgz logs; rm -f logs/*.log"
        self.remote_exec(clean_cmd)
        if self.node_info.getboolean("del_wallet"):
            del_wallet_cmd = "cd /root/work; rm -f wallet_%s.dat" % self.node_info["id"]
            self.remote_exec(del_wallet_cmd)

    def stop(self):
        """
        停止noded进程
        """
        self.remote_exec(self.stop_cmd + '&> /dev/null')

    def start(self):
        """
        启动节点
        :return: 执行失败，返回错误信息，否则返回空
        """
        result = self.remote_exec(self.node_info["start_cmd"])
        if result.startswith("[CheckWarning]"):
            return result
        start_status = self.status()
        if start_status:
            return start_status
        else:
            print("start noded [%s] successfully." % self.node_info["address"])

    def status(self):
        result = self.remote_exec("pgrep -a noded$ | grep %s &> /dev/null ; echo $?" % self.node_info["id"])
        if result != "0":
            faild_info = self.remote_exec(self.get_faild_info % self.node_info["id"])
            return faild_info.split("\n")  # 启动失败，返回日志中panic信息，列表类型

    @staticmethod
    def wait(n):
        for i in range(1, n + 1).__reversed__():
            time.sleep(1)
            sys.stdout.write(str(i).center(20, "*") + "\r")
            sys.stdout.flush()

    def check_mongo(self):
        """
        检查mongod是否启动
        """
        result = self.remote_exec("pgrep mongod &> /dev/null; echo $?")
        if result != "0":
            return "Mongod service did not start [%s]." % self.node_info["address"]

    def start_mongo(self):
        """
        启动mongod，使用默认的dbpath：/data/db
        """
        result = self.remote_exec("mkdir -p /opt/mongo_data; touch /opt/mongo.log ; mongod --dbpath /data/db --bind_ip_all --syslog --noauth --fork &> /dev/null")
        if result != "0":
            return "Mongod service start failed [%s]." % self.node_info["address"]

    @staticmethod
    def echo():
        return "Hello."


class GetP2pid(object):

    def __init__(self, genesis_info, node_info):
        self.genesis_info = genesis_info
        self.node_info = node_info

    @staticmethod
    def get_ssh_obj(node_info):
        ssh = MySSH(node_info["address"], node_info["ssh_user"], node_info["ssh_key"], node_info.getint("ssh_port"))
        return ssh

    def get_pubkey(self, account, node_info):
        ssh = self.get_ssh_obj(node_info)
        get_pubkey_cmd = "cd /root/work; ./cli getwalletkey -id %s -name %s -password 123456 | grep ': 0x' | awk '{print $NF}'" % (self.node_info["id"], account)
        result = ssh.remote_exec(get_pubkey_cmd)
        if result:
            return result
        else:
            print("Get p2paddr failed. [%s]" % get_pubkey_cmd)
            sys.exit(1)

    def get_addr(self, account, node_info):
        get_addr_cmd = "cd /root/work; ./cli getwalletinfo -accname %s -id %s | awk -F'address : ' '{print $NF}'" % (account, node_info["id"])
        if get_addr_cmd.startswith("0x"):
            return get_addr_cmd
        else:
            print("Get addr failed. [%s]" % get_addr_cmd)
            sys.exit(1)

    def send(self, account):
        root_addr = self.get_addr("root", self.genesis_info)
        to_addr = self.get_addr(account, self.node_info)
        send_cmd = "./cli send -amount 20000 -from %s -id %s -password 123456 -toaddr %s ; echo $?" % (root_addr, self.genesis_info["id"], to_addr)  # 由于send操作直接在genesis node上做，所以不需要指定noderpcaddr和noderpcport
        ssh = self.get_ssh_obj(self.genesis_info)
        result = ssh.remote_exec(send_cmd)
        if result.split("\n")[-1] != "0":
            print("send failed. [ %s ]" % send_cmd)
            sys.exit(1)

    def deposit(self, amount=10000):
        random_id = random.random()
        source_addr = self.get_addr(self.node_info["id"], self.node_info)
        deposit_cmd = "cd /root/work; ./cli deposit -amount %s -blsname %s -deposit %s -id %s -source %s; echo $?" % (amount, self.node_info["id"], random_id, self.node_info["id"], source_addr)
        ssh = self.get_ssh_obj(self.node_info)
        result = ssh.remote_exec(deposit_cmd)


class DeployCli(MySSH):
    """
    操作 CLI
        start：启动cli
        stop： 停止cli
    """
    match_id = re.compile(r'-id\s+?(\d+?)\s')
    get_faild_info = "cd /root/work; grep -i -E 'panic|warn' cli_%s.log"

    def __init__(self, cli_info):
        super().__init__(cli_info["address"], cli_info["ssh_user"], cli_info["ssh_key"], cli_info.getint("ssh_port"))
        self.cli_info = cli_info

    def stop(self):
        self.remote_exec('kill -9 $(pgrep ^cli$)')

    def status(self):
        result = self.remote_exec('pgrep -a ^cli$')
        start_id = self.match_id.findall(result)
        if start_id and self.cli_info["id"] in start_id:
            return
        else:
            data = self.remote_exec(self.get_faild_info % self.cli_info["id"])
            return data.split("\n")     # 返回错误信息

    def reset(self):
        self.stop()
        time.sleep(2)
        self.start()

    def init(self):
        self.start()

    def start(self):
        result = self.remote_exec(self.cli_info["start_cmd"])
        if result.startswith("[CheckWarning]"):
            return result
        return self.status()


class OperateMysql(object):
    """
    操作Mysql
    """

    def __init__(self, username, password, host, db, raise_on_warnings=True):
        self.config = {
            "user": username,
            "password": password,
            "host": host,
            "database": db,
            "raise_on_warnings": raise_on_warnings
        }

    def connect(self):
        """
        连接mysql
        """
        self.cnx = mysql.connector.connect(**self.config)
        self.cursor = self.cnx.cursor()

    def exec(self):
        """
        执行sql语句
        :return: sql语句执行失败，返回错误信息，否则返回空
        """
        try:
            self.cursor.executemany("TRUNCATE TABLE %s;", ["account", "block", "transaction", "transfer"])
            self.cursor.execute('update %s set value=-1 where keyname="PeerBlockHeight";', ["blockchain_info"])
        except Exception as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                return "Something is wrong with your user name or password [%s]" % str(err)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                return "Database does not exist [%s]" % str(err)
            else:
                return str(err)
        else:
            self.cnx.close()

    def run(self):
        self.connect()
        return self.exec()


class Config(object):
    """
    配置，默认配置文件为 conf/config.ini
    read_config: 从配置文件中读取配置，返回 class config
    generate_config: 生成默认的配置文件
    list_config: 打印配置文件内容
    """

    def __init__(self, filename="config.ini"):
        self.filename = os.path.join(CONFIGDIR, filename)
        self.config = configparser.ConfigParser()

    def read_config(self):
        with open(self.filename, "r") as f:
            self.config.read_file(f)
        return self.config

    def list_config(self):
        if not os.path.exists(self.filename):
            return "This file was not found [ %s ]" % self.filename
        with open(self.filename, "r") as f:
            for line in f.readlines():
                print(line, end="")
            return

    def generate_config(self):
        # self.config["global"] = {
        #     "leader": "127.0.0.1:3000"
        # }
        self.config["genesis"] = {
            "address": "127.0.0.1",
            "ssh_user": "root",
            "ssh_port": "22",
            "ssh_key": os.path.join(CONFIGDIR, "id_rsa_jump"),
            "id": 3005,
            "del_wallet": False,
            "create_wallet": 0,
            "init_cmd": "cd /root/work; ./noded init -account root -role miner -id 3005 -genesis 1 -createwallet 0 -dev 1 ; echo $?",
            "start_cmd": "cd /root/work; nohup ./noded run -account root -id 3005 -role miner -ip 10.15.101.114 --port 3005 -rpc 1 -rpcaddr 0.0.0.0 -rpcport 40001 -dev 1 \
                            -p2paddr 10.15.101.114:3005 -p2pid xxxxxxxx &> /dev/null &"
        }
        for i in range(1, 3):
            self.config["node0%d" % i] = {
                "address": "127.0.0.1",
                "ssh_user": "root",
                "ssh_port": "22",
                "ssh_key": os.path.join(CONFIGDIR, "id_rsa_jump"),
                "id": "300%d" % i,
                "del_wallet": False,
                "create_wallet": 0,
                "init_cmd": "noded init...",
                "start_cmd": "noded run..."
            }
        for i in range(1, 3):
            self.config["cli%d" % i] = {
                "address": "127.0.0.1",
                "ssh_user": "root",
                "ssh_port": "22",
                "ssh_key": os.path.join(CONFIGDIR, "id_rsa_jump"),
                "id": "300%d" % i,
                "del_wallet": False,
                "start_cmd": "cli service..."
            }
        self.write()

    def write(self):
        with open(os.path.join(CONFIGDIR, self.filename), "w") as f:
            self.config.write(f, space_around_delimiters=True)


def check_file_exists(*filename):
    """
    检查给定的文件是否存在
    :param filename: 文件名，tuple类型
    :return: 如果有文件不存在，则追加到列表中并返回
    """
    not_exists_list = []
    for f in filename:
        if not os.path.exists(f):
            not_exists_list.append(f)
    else:
        if not_exists_list:
            print("File not found: %s" % not_exists_list)
            sys.exit()


def check_action_result(result, config, action):
    if result and result != "Hello.":
        print("%s %s [%s] faild. Error:" % (action, config.name, config["address"]))
        for err in result:
            print(err)
            sys.exit(1)
    else:
        print("%s %s [%s] successfully." % (action, config.name, config["address"]))
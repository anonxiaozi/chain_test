# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: deploy_tools

import mysql.connector
from mysql.connector import errorcode
import time
import sys
import re
import os
import configparser
from main.remote_exec import MySSH

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")


class DeployNode(MySSH):
    """
    操作noded，需要提供noded的配置信息(node_info)
    stop: 停止节点
    clean: 清除node数据，包括：清除db、备份日志后清空日志、删除钱包
    start: 启动节点
    """

    stop_cmd = 'kill -9 $(pgrep noded$) &> /dev/null'
    get_faild_info = "cd {data_path}/logs; data=`ls -lt | grep node_%s | head -1 | awk '{print $NF}'`; if [ ! -z $data ]; then grep -i -E 'panic|warn' $data; else echo Nothing; fi"

    def __init__(self, node_info, logger):
        self.logger = logger
        super().__init__(node_info["address"], node_info["ssh_user"], node_info["ssh_key"], node_info.getint("ssh_port"), self.logger)
        self.node_info = node_info

    def init(self):
        """
        初始化节点
        """
        self.check_mongo()
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
        clean_cmd = "cd /root/work; ./noded clear -nick {id} -datapath {data_path}; rm -f {data_path}/logs/*".format(**self.node_info)
        self.remote_exec(clean_cmd)
        if self.node_info.getboolean("del_wallet"):
            del_wallet_cmd = "cd /root/work; rm -f {data_path}/wallet_{id}.dat".format(**self.node_info)
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
        self.check_mongo()
        result = self.remote_exec(self.node_info["start_cmd"])
        if result.startswith("[CheckWarning]"):
            return result
        start_status = self.status()
        if start_status:
            return start_status
        else:
            data = "start noded [{address}] successfully.".format(**self.node_info)
            self.logger.info(data)
            print(data)

    def status(self):
        result = self.remote_exec("pgrep -a noded$ | grep {id} &> /dev/null ; echo $?".format(**self.node_info))
        if result != "0":
            faild_info = self.remote_exec(self.get_faild_info.format(**self.node_info))
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
        check_mongo_cmd = "pgrep mongod &> /dev/null; echo $?"
        result = self.remote_exec(check_mongo_cmd)
        if result != "0":
            result = "Mongod service did not start [%s]." % self.node_info["address"]
            self.logger.warning(result)
            print(result)
            self.start_mongo()

    def start_mongo(self):
        """
        启动mongod，使用默认的dbpath：/data/db
        """
        print("Start mongodb...")
        self.logger.info("Start mongodb...")
        start_mongo_cmd = "mkdir -p /opt/mongo_data; touch /opt/mongo.log ; mongod --dbpath /data/db --bind_ip_all --syslog --noauth --fork &> /dev/null"
        result = self.remote_exec(start_mongo_cmd)
        if result != "0":
            data = "Mongod service start failed [%s]." % self.node_info["address"]
            self.logger.error(data)
            return data

    @staticmethod
    def echo():
        return "Hello."


class Deposit(object):

    def __init__(self, genesis_info, node_info, logger):
        self.genesis_info = genesis_info
        self.node_info = node_info
        self.logger = logger

    def get_ssh_obj(self, node_info):
        ssh = MySSH(node_info["address"], node_info["ssh_user"], node_info["ssh_key"], node_info.getint("ssh_port"), self.logger)
        return ssh

    def get_pubkey(self, account, node_info):
        """
        启动节点时，p2pid 选项使用
        """
        if not account:
            account = "root"
        ssh = self.get_ssh_obj(node_info)
        get_pubkey_cmd = "cd /root/work; ./cli getwalletkey -nick {} -name {} -password 123456 -datapath {} | grep ': 0x' | awk '{{print $NF}}'".format(
            self.node_info["id"], account, self.node_info["data_path"])
        result = ssh.remote_exec(get_pubkey_cmd)
        if result:
            return result
        else:
            data = "Get p2paddr failed. [%s]" % get_pubkey_cmd
            self.logger.error("{} Exit...".format(data))
            print(data)
            sys.exit(1)

    def get_addr(self, account, node_info):
        get_addr_cmd = "cd /root/work; ./cli getwalletinfo -accname {} -nick {} -datapath {} | awk -F'address : ' '{{print $NF}}'".format(
            account, node_info["id"], node_info["data_path"])
        ssh = self.get_ssh_obj(node_info)
        result = ssh.remote_exec(get_addr_cmd)
        if result.startswith("0x"):
            return result
        else:
            data = "Get addr failed. [%s] %s" % (get_addr_cmd, result)
            self.logger.error("{} Exit...".format(data))
            print(data)
            sys.exit(1)

    def send(self, account=None, amount=20000):
        if not account:
            account = self.node_info["id"]
        root_addr = self.get_addr("root", self.genesis_info)  # root address
        to_addr = self.get_addr(account, self.node_info)  # deposit account address
        send_cmd = "cd /root/work; ./cli send -amount {} -from {} -nick {} -toaddr {} -dev 1 -datapath {}; echo $?".format(
            amount, root_addr, self.genesis_info["id"], to_addr, self.node_info["data_path"])  # 由于send操作直接在genesis node上做，所以不需要指定noderpcaddr和noderpcport
        ssh = self.get_ssh_obj(self.genesis_info)
        result = ssh.remote_exec(send_cmd)
        if result.split("\n")[-1] != "0":
            data = "send failed. [ %s ]" % send_cmd
            self.logger.error("{} Exit...".format(data))
            print(data)
            sys.exit(1)

    def deposit(self):
        deposit_name = self.node_info["id"]
        source_addr = self.get_addr(self.node_info["id"], self.node_info)
        amount = self.node_info["deposit_amount"]
        if int(amount) == 0:
            print("Don't deposit [{}]".format(deposit_name))
            return deposit_name
        deposit_cmd = "cd /root/work; ./cli deposit -amount {} -blsname {} -nick {} -source {} -dev 1 -datapath {}".format(
            amount, self.node_info["id"], self.node_info["id"], source_addr, self.node_info["data_path"])
        ssh = self.get_ssh_obj(self.node_info)
        result = ssh.remote_exec(deposit_cmd)
        print("Deposit result [{}]:".format(deposit_name))
        for item in result.split("\n"):
            print(item)
        return deposit_name


class DeployCli(MySSH):
    """
    操作 CLI
        start：启动cli
        stop： 停止cli
    """
    match_id = re.compile(r'-nick\s+?(\d+?)\s')
    get_faild_info = "cd {data_path}; grep -i -E 'panic|warn' cli_{id}.log"

    def __init__(self, cli_info, logger):
        super().__init__(cli_info["address"], cli_info["ssh_user"], cli_info["ssh_key"], cli_info.getint("ssh_port"), logger)
        self.cli_info = cli_info
        self.logger = logger

    def stop(self):
        self.remote_exec('kill -9 $(pgrep pbcli$) &> /dev/null')

    def status(self):
        result = self.remote_exec('pgrep -a ^pbcli$')
        start_id = self.match_id.findall(result)
        if start_id and self.cli_info["id"] in start_id:
            return
        else:
            data = self.remote_exec(self.get_faild_info.format(**self.cli_info))
            self.logger.error(data)
            return data.split("\n")  # 返回错误信息

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
            return
        with open(self.filename, "r") as f:
            return f.readlines()

    def generate_config(self):
        self.config["genesis"] = {
            "address": "127.0.0.1",
            "ssh_user": "root",
            "ssh_port": "22",
            "ssh_key": os.path.join(CONFIGDIR, "id_rsa_jump"),
            "id": 3005,
            "del_wallet": False,
            "create_wallet": 0,
            "deposit": False,
            "data_path": "~/.pb_data",
            "init_cmd": "cd /root/work; ./noded init -account root -role miner -nick 3005 -genesis 1 -createwallet 0 -dev 1; echo $?",
            "start_cmd": "cd /root/work; nohup ./noded run -account root -nick 3005 -role miner -addr 10.15.101.114:3005 -rpc 1 \
                             -rpcaddr 0.0.0.0:40001 -dev 1 &> /dev/null &"
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
                "deposit": True,
                "deposit_amount": 10000,
                "cli_rpc_port": 60002,
                "data_path": "~/.pb_data",
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
                "rpc_port": 60002,
                "data_path": "~/.pb_data",
                "start_cmd": "cli service..."
            }
        self.write()

    def write(self):
        with open(os.path.join(CONFIGDIR, self.filename), "w") as f:
            self.config.write(f, space_around_delimiters=True)


def check_file_exists(filename):
    """
    检查给定的文件是否存在
    :param filename: 文件名，tuple类型
    :return: 如果有文件不存在，则追加到列表中并返回
    """
    if not os.path.exists(filename):
        return "File not found: {}".format(filename)
    else:
        return filename


def check_action_result(result, config, action, logger):
    try:
        if result and result != "Hello.":
            data = "%s %s [%s] faild. Error:" % (action, config.name, config["address"])
            logger.error(data)
            if isinstance(result, str):
                print(result)
                logger.error(result)
                return result
            for err in result:
                print(err)
            else:
                logger.error(result)
                return result
        else:
            data = "%s %s [%s] successfully." % (action, config.name, config["address"])
            logger.info(data)
            print(data)
            return data
    except Exception as e:
        logger.error(e)
        print(e)
        return e

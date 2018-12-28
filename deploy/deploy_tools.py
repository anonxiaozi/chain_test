# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: deploy_tools

import paramiko
import mysql.connector
from mysql.connector import errorcode
import time
import sys
import re
import os
import configparser

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")


class MySSH(object):
    """
    通过SSH连接服务器
    login_auth: 登陆
    remote_exec: 执行命令，返回执行结果
    """

    def __init__(self, hostname, username, keyfile, port):
        self.hostname = hostname
        self.username = username
        self.keyfile = keyfile
        self.port = port

    def login_auth(self):
        private_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.hostname, port=self.port, username=self.username, pkey=private_key)

    def remote_exec(self, cmd):
        """
        执行命令
        :param cmd: 传入命令
        :return: 返回执行的结果，使用"utf8"解码
        """
        self.login_auth()
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=60)
        error = stderr.read()
        if error:
            result = error
        else:
            result = stdout.read()
        return result.decode("utf-8").strip()


class DeployNode(MySSH):

    """
    操作noded，需要提供noded的配置信息(node_info)
    reset: 重置节点，stop -> clean -> init -> start
    stop: 停止节点
    clean: 清除node数据，包括：清除db、备份日志后清空日志、删除钱包
    start: 启动节点
    """

    stop_cmd = 'kill -9 $(pgrep noded$)'
    get_faild_info = "cd /root/work/logs; grep -i -E 'panic|warn' `ls -lt | grep node_%s | head -1 | awk '{print $NF}'`"

    def __init__(self, node_info):
        super().__init__(node_info["address"], node_info["ssh_user"], node_info["ssh_key"], node_info.getint("ssh_port"))
        self.node_info = node_info

    def reset(self):
        """
        重置节点，首先stop，之后clean
        return: 初始化失败，返回输出信息，否则执行start
        """
        self.stop()
        self.clean()
        result = self.remote_exec(self.node_info["init_cmd"])
        if result.split("\n")[-1] != "0":
            return result  # 初始化失败
        else:
            start_status = self.start()
            return start_status if start_status else None

    def clean(self):
        """
        清除noded数据
        """
        clean_cmd = "cd /root/work; ./noded clear -id %s" % self.node_info["id"] + "; tar zcf log_$(date +%Y%m%d%H%M).tgz logs; rm -f logs/*.log; " + "rm -f wallet_%s.dat" % self.node_info["id"]
        self.remote_exec(clean_cmd)

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
        self.remote_exec(self.node_info["start_cmd"])
        start_status = self.check_started()
        if start_status != '0':
            return start_status

    def check_started(self):
        result = self.remote_exec('pgrep noded$ &> /dev/null ; echo $?')
        if result != "0":
            faild_info = self.remote_exec(self.get_faild_info % self.node_info["id"])
            return faild_info.split("\n")  # 启动失败，返回日志中panic信息，列表类型
        else:
            return result

    @staticmethod
    def wait(n):
        for i in range(1, n + 1).__reversed__():
            time.sleep(1)
            sys.stdout.write(str(i).center(20, "*") + '\r')
            sys.stdout.flush()

    @staticmethod
    def echo():
        return "Hello."


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

    def check_start(self):
        result = self.remote_exec('pgrep -a ^cli$')
        start_id = self.match_id.findall(result)
        if start_id and self.cli_info["id"] in start_id:
            return
        else:
            data = self.remote_exec(self.get_faild_info % self.cli_info["id"])
            return data.split("\n")     # 返回错误信息

    def reset(self):
        self.stop()
        self.start()

    def start(self):
        self.remote_exec(self.cli_info["start_cmd"])
        return self.check_start()


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

    filename = os.path.join(os.path.join(BASEDIR, "conf"), "config.ini")

    def __init__(self, filename):
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
        self.config["global"] = {
            "leader": "127.0.0.1:3000"
        }
        self.config["genesis"] = {
            "address": "127.0.0.1",
            "ssh_user": "root",
            "ssh_port": "22",
            "ssh_key": os.path.join(CONFIGDIR, "id_rsa_jump"),
            "id": 3005,
            "init_cmd": "noded init...",
            "start_cmd": "noded run..."
        }
        for i in range(1, 3):
            self.config["node0%d" % i] = {
                "address": "127.0.0.1",
                "ssh_user": "root",
                "ssh_port": "22",
                "ssh_key": os.path.join(CONFIGDIR, "id_rsa_jump"),
                "id": "300%d" % i,
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
        print("%s [%s] faild. Error:" % (action, config["address"]))
        for err in result:
            print(err)
            sys.exit(1)
    else:
        print("%s %s [%s] successfully." % (action, config.name, config["address"]))

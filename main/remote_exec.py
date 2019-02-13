# -*- coding: utf-8 -*-
# @Time: 2018/12/28
# @File: exec_cmd

import paramiko


class MySSH(object):
    """
    通过SSH连接服务器
    login_auth: 登陆
    check_cmd: 检查命令的安全性
    remote_exec: 执行命令，返回执行结果
    """

    def __init__(self, hostname, username, keyfile, port, logger):
        self.hostname = hostname
        self.username = username
        self.keyfile = keyfile
        self.port = port
        self.logger = logger

    def login_auth(self):
        self.logger.info("ssh login: {}@{}:{} [{}]".format(self.username, self.hostname, self.port, self.keyfile))
        private_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.hostname, port=self.port, username=self.username, pkey=private_key)

    def check_cmd(self, cmd):
        """
        检查指令是否安全，开头不是cli和noded的指令都不允许执行，也不允许使用";"或"&&"来拼接指令
        :return: 如果指令有问题，则返回警告信息：[BlokeError]标志
        """
        self.logger.info("Check CMD ...")
        cmd_prefix = "cd /root/work; ./"
        if cmd.split()[0] not in ["cli", "noded"]:  # 不是cli或noded命令
            data = "[CheckWarning] Illegal instruction: [ %s ]" % cmd, cmd
            self.logger.error(data)
            return data
        elif ";" in cmd or "&&" in cmd:  # 不允许拼接多条命令
            data = "[CheckWarning] Multiple instructions are not allowed: [ %s ]" % cmd, cmd
            self.logger.error(data)
            return data
        else:
            data = cmd_prefix + cmd
            self.logger.info(data)
            return data

    def remote_exec(self, cmd, check=False):
        """
        执行命令
        :param cmd: 传入命令
        :return: 返回执行的结果，使用"utf8"解码
        """
        if check:
            check_result = self.check_cmd(cmd)
            if isinstance(check_result, tuple):
                return check_result[0]
            else:
                cmd = check_result
        self.login_auth()
        self.logger.info("[I] {}".format(cmd))
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=30)
        error = stderr.read()
        if error:
            result = error
            self.logger.warning("[O] {}".format(result))
        else:
            result = stdout.read()
            self.logger.info("[O] {}".format(result))
        return result.decode("utf-8").strip()

    def __del__(self):
        try:
            self.ssh.close()
        except Exception:
            pass

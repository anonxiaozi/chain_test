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

    @staticmethod
    def check_cmd(cmd):
        """
        检查指令是否安全，开头不是cli和noded的指令都不允许执行，也不允许使用";"或"&&"来拼接指令
        :return: 如果指令有问题，则返回警告信息：[BlokeError]标志
        """
        cmd_prefix = "cd /root/work; ./"
        if cmd.split()[0] not in ["cli", "noded"]:  # 不是cli或noded命令
            return "[CheckWarning] Illegal instruction: [ %s ]" % cmd, cmd
        elif ";" in cmd or "&&" in cmd:  # 不允许拼接多条命令
            return "[CheckWarning] Multiple instructions are not allowed: [ %s ]" % cmd, cmd
        else:
            return cmd_prefix + cmd

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
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=60)
        error = stderr.read()
        if error:
            result = error
        else:
            result = stdout.read()
        return result.decode("utf-8").strip()


class RunCmd(MySSH):

    def __init__(self, cmd, host_info=None):
        # super().__init__(host_info["address"], host_info["ssh_user"], host_info["ssh_key"], host_info.getint("ssh_port"))
        super().__init__("10.15.101.254", "root", "..\\conf\\id_rsa_jump", 22)
        self.cmd = cmd

    def run_cmd(self):
        result = self.remote_exec(self.cmd, check=True)
        return result

    def __del__(self):
        try:
            self.ssh.close()
        except Exception:
            print()

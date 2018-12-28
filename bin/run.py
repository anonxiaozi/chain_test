# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: run

import argparse
import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from deploy.deploy_tools import Config, check_file_exists, check_action_result, DeployNode, DeployCli
from deploy.test_api import RunApi, ApiTestData
from deploy.remote_exec import RunCmd


def get_args():
    """
    命令行参数
    """
    default_config_file = os.path.join(os.path.join(BASEDIR, "conf"), "config.ini")
    arg = argparse.ArgumentParser(prog="Deploy node")

    subarg = arg.add_subparsers(help="Subcommand", dest="sub")

    # run cmd
    cmd = subarg.add_parser("cmd", help="Remote execution of commands")
    cmd.add_argument("host", type=str, help="Node name")
    cmd.add_argument("-c", "--config", type=str, help="config file name, the file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)
    cmd.add_argument("-a", "--attach", type=str, help="The command to execute", required=True)

    # deployment
    deploy = subarg.add_parser("deploy", help="Deployment environment")
    deploy.add_argument("-c", "--config", type=str, help="config file name, the file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)
    deploy.add_argument("action", choices=["start", "stop", "clean", "reset"], help="action")

    # generate_config
    generate_config = subarg.add_parser("generate_config", help="Generate configuration file")
    generate_config.add_argument("-f", "--filename", type=str, help="config file name, he file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)

    # api_test
    api_test = subarg.add_parser("testapi", help="test api")
    api_test.add_argument("host", type=str, help="server addr")
    api_test.add_argument("port", type=int, help="server port")
    api_test.add_argument("method", type=str, help="api name")

    # monit api
    monit_api = subarg.add_parser("monitapi", help="monit api result")
    monit_api.add_argument("host", type=str, help="server addr")
    monit_api.add_argument("port", type=int, help="server port")
    monit_api.add_argument("method", type=str, help="api name")
    monit_api.add_argument("-i", "--interval", type=int, help="monitoring interval", required=True)
    monit_api.add_argument("-n", "--total", type=int, help="Total number of monitoring, default: %(default)s, means unlimited", default=0)

    # list: api/config
    list_func = subarg.add_parser("list", help="list valid api")
    list_func.add_argument("listobj", type=str, choices=["api", "config"])
    list_func.add_argument("-c", "--config", type=str, help="config file name, the file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)

    return arg


if __name__ == '__main__':
    args_obj = get_args()
    args = vars(args_obj.parse_args())
    operate = args["sub"]
    if not operate:
        args_obj.print_help()  # 打印help信息
        sys.exit(0)

    try:
        if operate == "generate_config":  # 生成配置文件
            try:
                config = Config(args["filename"])
                config.generate_config()
            except Exception as e:
                print("Error: %s" % e)
            finally:
                sys.exit()
        elif operate == "testapi":  # 测试接口
            api = RunApi(args["host"], args["port"], args["method"])
            result = api.cli_api()
            if isinstance(result, dict):    # 有值
                for key, value in result.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            print(subkey, subvalue, sep=": ", end="")
                    else:
                        print(key, value, sep=" : ", end="")
                else:
                    exit()
            else:
                print(result)
                sys.exit(1)
        elif operate == "monitapi":     # 监控接口返回值
            api = RunApi(args["host"], args["port"], args["method"])
            api.monit_result(args["interval"], args["total"])
        elif operate == "list":
            if args["listobj"] == "api":    # 列出支持的接口名
                data = [x for x in ApiTestData().url_index]
                print(data)
                sys.exit()
            elif args["listobj"] == "config":   # 打印配置信息
                configobj = Config(args["config"])
                err = configobj.list_config()
                if err: print("Error: %s" % err)
                sys.exit(1 if err else 0)
        # 读取配置
        check_file_exists(os.path.join(CONFIGDIR, args["config"]))  # 检测文件是否存在
        configobj = Config(args["config"])
        config = configobj.read_config()
        if operate == "cmd":  # 远程执行命令
            remote_exec = RunCmd(args["attach"], config[args["host"]])
            exec_result = remote_exec.run_cmd()
            print(exec_result)
            sys.exit()
        # ======================================操作noded与cli======================================
        action = args["action"]     # 要执行的动作
        if operate == "deploy":
            node_list = []
            for node_key in config.keys():
                if node_key.startswith("node"):
                    node_list.append(node_key)
            # genesis
            genesis = DeployNode(config["genesis"])
            genesis_result = getattr(genesis, action, DeployNode.echo)()
            check_action_result(genesis_result, config["genesis"], action)
            if action in ["reset", "start"]: DeployNode.wait(2)
            # noded
            for node in node_list:
                noded_result = DeployNode(config[node])
                check_action_result(noded_result, config[node], action)
            # cli
            cli_list = []
            for cli_key in config.keys():
                if cli_key.startswith("cli"):
                    cli_list.append(cli_key)
            for cli in cli_list:
                client = DeployCli(config[cli])
                client_result = getattr(client, action, DeployNode.echo)()
                check_action_result(client_result, config[cli], action)
    except KeyboardInterrupt:
        print("Exit.")
    except KeyError as e:
        print("KeyError: %s" % e)
    except AttributeError as e:
        print("AttributeError: %s" % e)
    finally:
        sys.exit()

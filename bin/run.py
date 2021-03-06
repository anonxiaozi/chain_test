# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: run

import argparse
import sys
import os
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from main.bin_tools import EveryOne
from main.logger import Logger
import datetime


def get_args():
    """
    命令行参数
    """
    default_config_file = os.path.join(os.path.join(BASEDIR, "conf"), "config.ini")
    arg = argparse.ArgumentParser(prog="Deploy node")

    subarg = arg.add_subparsers(help="Subcommand", dest="sub")

    # deployment
    deploy = subarg.add_parser("deploy", help="Deployment environment")
    deploy.add_argument("-c", "--config", type=str, help="config file name, the file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)
    deploy.add_argument("action", choices=["start", "stop", "clean", "status", "init"], help="action")

    # generate_config
    generate_config = subarg.add_parser("generate_config", help="Generate configuration file")
    generate_config.add_argument("-f", "--filename", type=str, help="config file name, he file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)

    # api_test
    api_test = subarg.add_parser("testapi", help="test api")
    api_test.add_argument("host", type=str, help="server addr")
    api_test.add_argument("port", type=int, help="server port")
    api_test.add_argument("method", type=str, help="api name")
    api_test.add_argument("--sign", type=str, help="api function, default: %(default)s", default=None)

    # monit api
    monit_api = subarg.add_parser("monitapi", help="monit api result")
    monit_api.add_argument("host", type=str, help="server addr")
    monit_api.add_argument("port", type=int, help="server port")
    monit_api.add_argument("method", type=str, help="api name")
    monit_api.add_argument("--sign", type=str, help="api function, default: %(default)s", default=None)
    monit_api.add_argument("-i", "--interval", type=int, help="monitoring interval", required=True)
    monit_api.add_argument("-n", "--total", type=int, help="Total number of monitoring, default: %(default)s, means unlimited", default=0)

    # list: api/config
    list_func = subarg.add_parser("list", help="list valid api")
    list_func.add_argument("listobj", type=str, choices=["api", "config"])
    list_func.add_argument("-c", "--config", type=str, help="config file name, the file directory is %s , Default: %s" % (CONFIGDIR, default_config_file), default=default_config_file)

    return arg


if __name__ == '__main__':
    log_name = "{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d"))
    logger = Logger(log_name)
    args_obj = get_args()
    args = vars(args_obj.parse_args())
    operate = args["sub"]
    if not operate:
        args_obj.print_help()  # 打印help信息
        sys.exit(0)
    try:
        run = EveryOne(args, logger)
        getattr(run, "do_{}".format(args["sub"]))()
    except KeyboardInterrupt:
        print("\nExit.")
    except KeyError as e:
        logger.error("KeyError: {}".format(e))
        print("KeyError: {}".format(e))
    except AttributeError as e:
        logger.error("AttributeError: {}".format(e))
        print("AttributeError: {}".format(e))
    except Exception as e:
        logger.error("Error: {}".format(e))
        print("Error: %s" % e)
    finally:
        logger.warning("Exit.")

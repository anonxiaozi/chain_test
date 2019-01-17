# -*- coding: utf-8 -*-
# @Time: 2019/1/14
# @File: allinone.py

"""
all in one
"""

import sys
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
import importlib


def import_module(module_name, module_args, sub_module_name, package_path="client"):
    spec = importlib.import_module(module_name, package_path)
    func = getattr(spec, sub_module_name)()
    result = func.status(module_args)
    return result


if __name__ == "__main__":
    module_dict = {
        'GetDepositID': {
            "host": "10.15.101.67",
            "port": 60002,
            "accounts": "root,3005,3006",
        }
    }
    name = "GetDepositID"
    get_deposit_id = import_module(name, module_dict[name], name)
    print(get_deposit_id)

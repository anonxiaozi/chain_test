# -*- coding: utf-8 -*-
# @Time: 2019/1/14
# @File: allinone.py

"""
all in one
"""

import importlib
import json
import datetime


def run_module(module_dict, package_path="client"):
    result_dict = {}
    args = module_dict["global"].copy()
    modules = module_dict["modules"]
    for module in modules:
        args.update(modules[module])
        print("%s..." % modules[module]["desc"])
        spec = importlib.import_module(module, package_path)
        func = getattr(spec, module)()
        func.args = args
        result = func.run()
        result_dict[module] = result
    return result_dict


if __name__ == "__main__":
    module_dict = {
        "global": {
            "host": "10.15.101.67",
            "port": 60002
        },
        "modules": {
            "GetDepositID": {
                "accounts": "root,3006,3007",
                "desc": "Get Deposit ID"
            },
            "GetDepositAccount": {
                "accounts": "root,3006,3007",
                "desc": "Get Deposit Info"
            },
            "GetDepositScale": {
                "accounts": "root,3006,3007",
                "desc": "Get Deposit Count"
            },
            "UnitTest": {
                "desc": "Unit Test"
            }
        }
    }
    result = run_module(module_dict)
    for key, value in result.items():
        print(key, value, sep=" -> ")
    with open("../exports/%s.json" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), 'w') as f:
        json.dump(result, f, indent=4)

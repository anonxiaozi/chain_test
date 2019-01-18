# -*- coding: utf-8 -*-
# @Time: 2019/1/14
# @File: allinone.py

"""
all in one
"""

import importlib


def run_module(module_dict, package_path="client"):
    result_dict = {}
    args = module_dict["gloabl"].copy()
    for module in module_dict:
        args.update(module_dict[module])
        print(module_dict[module]["desc"].center(100, "*"))
        spec = importlib.import_module(module, package_path)
        func = getattr(spec, module)()
        result = func.run(args=args)
        result_dict[module] = result
    return result_dict


if __name__ == "__main__":
    module_dict = {
        "global": {
            "host": "10.15.101.67",
            "port": 60002
        },
        "GetDepositID": {
            "accounts": "root,3006,3007",
            "desc": "Get Deposit ID"
        },
        "GetDepositAccount": {
            "accounts": "root,3006,3007",
            "desc": "Get Deposit Info"
        },
        # "DepositScale": {
        #     "accounts": "root,3006,3007",
        #     "desc": "Get Deposit Count"
        # },
        # "UnitTest": {
        #     "desc": "Unit Test"
        # }
    }
    result = run_module(module_dict)
    for key, value in result.items():
        print(key, value, sep=" -> ")

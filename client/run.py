# -*- coding: utf-8 -*-
# @Time: 2019/1/14
# @File: run.py

import os

# 压力测试
os.system("python pressure_test.py -c config.ini -t 300 -i 2 10.15.101.77 60002")

# StartTxTest
os.system("python unit_test.py -c config.ini 10.15.101.77 60002")

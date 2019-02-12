# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: test_api

import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import time
import os

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIGDIR = os.path.join(BASEDIR, "conf")
sys.path.insert(0, BASEDIR)
from tools.logger import Logger


class ApiTestData(object):

    def __init__(self):
        with open(os.path.join(CONFIGDIR, "rpc_data.json"), "r") as f:
            self.rpc_data = json.load(f)

    def get_url(self, method):
        url = self.rpc_data[method].get("uri", None)
        return url

    def get_data(self, method, sign):
        data = self.rpc_data[method].get("body", None)
        if sign:
            data = self.rpc_data[method].get("body", None)[sign]  # 一个方法，有多个body体，需要通过sign参数来区分
        if data is None:
            return None
        return json.dumps(data).encode("utf-8")

    def action(self, method, sign):
        return self.get_url(method), self.get_data(method, sign), self.rpc_data["header"]


class RunApi(ApiTestData):

    def __init__(self, host, port, method, sign, logger):
        super().__init__()
        self.host = host
        self.port = port
        self.method = method
        self.sign = sign
        self.logger = logger

    def cli_api(self, body=None):
        url, data, headers = self.action(self.method, self.sign)
        if body:
            data = body
        if data:
            if not isinstance(data, bytes):
                data = json.dumps(data).encode("utf-8")
        if not url:
            data = "ERROR: method not found: %s" % self.method
            self.logger.error(data)
            return data
        try:
            req = urllib.request.Request(url="http://%s:%d/%s" % (self.host, self.port, url), data=data, headers=headers)
            self.logger.info("[I] {} [{}] {}".format(req.get_full_url(), req.get_method(), req.data))
        except Exception as e:
            self.logger.error(e)
        try:
            res = urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as e:
            data = json.loads(e.fp.read().decode("utf-8"))
            self.logger.error("[O] {}".format(data))
        except Exception as e:
            self.logger.error("[O] {}".format(e))
            return "Error: %s" % e
        data = json.loads(res.read().decode("utf-8"))
        self.logger.info("[O] {}".format(data))
        return data

    @staticmethod
    def echo_monit_result(result, field=None):
        """
        打印结果输出，因为是json格式，可以传入field(列表形式)，来指定打印输出
        """
        if not result:
            print(None)
        elif field:
            result_dict = {}
            for key in field.split(","):
                key = key.strip()
                result_dict[key] = result.get(key, "")
                print(key, result.get(key, ""), sep=": ", end="\n")
            else:
                return result_dict
        else:
            print("\n")
            print(json.dumps(result, indent=2))

    def monit_result(self, time_internal, total=0):
        if not total:
            total = 999999999999
        count = 0
        print("\n" + str(count).center(50, "="))
        result = self.cli_api()
        self.echo_monit_result(result)
        time.sleep(time_internal)
        count += 1
        while count < total:
            print("\n" + str(count).center(50, "="))
            result = self.cli_api()
            self.echo_monit_result(result)
            time.sleep(time_internal)
            count += 1
        print()
        sys.exit()


if __name__ == "__main__":
    logger = Logger()
    host, port, method = "10.15.101.35", 60002, "GetNodeStatus"
    use = RunApi(host, port, method, None, logger)
    url, data, headers = use.action(method, None)
    if not url:
        print("Method not found: %s" % method)
        sys.exit(2)
    result = use.cli_api()
    print(result)

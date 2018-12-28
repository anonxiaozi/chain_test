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


class ApiTestData(object):

    def __init__(self):
        with open(os.path.join(CONFIGDIR, "rpc_data.json"), "r") as f:
            self.rpc_data = json.load(f)

    def get_url(self, method):
        url = self.rpc_data[method].get("uri", None)
        return url

    def get_data(self, method):
        data = self.rpc_data[method].get("body", None)
        if data is None:
            return None
        else:
            return json.dumps(data).encode("utf-8")

    def action(self, method):
        return self.get_url(method), self.get_data(method), self.rpc_data["header"]


class RunApi(ApiTestData):

    def __init__(self, host, port, method):
        super().__init__()
        self.host = host
        self.port = port
        self.method = method

    def cli_api(self):
        url, data, headers = self.action(self.method)
        if not url:
            return "ERROR: method not found: %s" % self.method
        req = urllib.request.Request(url="http://%s:%d/%s" % (self.host, self.port, url), data=data, headers=headers)
        try:
            res = urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as e:
            return json.loads(e.fp.read().decode("utf-8"))      # 返回接口错误抛出的内容
        except Exception as e:
            return "ERROR: %s" % e
        return json.loads(res.read().decode("utf-8"))

    @staticmethod
    def echo_monit_result(result):
        if not result:
            sys.exit()
        else:
            for key, value in result.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        print(subkey, subvalue, sep=": ", end="\n")
                else:
                    print(key, value, sep=": ", end="\n")

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

    host, port, method = "10.15.101.35", 60002, "GetNodeStatus"
    use = RunApi(host, port, method)
    url, data, headers = use.action(method)
    if not url:
        print("Method not found: %s" % method)
        sys.exit(2)
    result = use.cli_api()
    print(result)

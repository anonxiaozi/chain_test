# -*- coding: utf-8 -*-
# @Time: 2018/12/27
# @File: test_api

import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import time


class ApiTestData(object):

    def __init__(self):
        self.url_index = {
            "GetNodeStatus": "api/v1/GetNodeStatus",
            "StartTxTest": "api/v1/StartTxTest",
            "StopTxTest": "api/v1/StopTxTest",
            "GetTxTestStatus": "api/v1/GetTxTestStatus",
        }
        self.headers = {
            "Content-Type": "application/json"
        }

    test_systemTransfer = {
        "fromAddr": "0x7cc7836bc4e0f22df894fe3201e40f925d48eea0",
        "destAddr": "0xe6be8a4bcd35696c78eb0076e1f15d1fef0730e9",
        "amount": "1",
    }

    test_getbalance = {
        "address": "0xe6be8a4bcd35696c78eb0076e1f15d1fef0730e9"
    }

    test_StartTxTest = {
        "TestType": "SequenceTestor",
        "TestProperties": {}
    }

    test_StopTxTest = {}

    def get_url(self, method):
        url = self.url_index.get(method, None)
        return url

    def get_data(self, method):
        data = getattr(self, "test_%s" % method, None)
        if not data is None:
            return json.dumps(data).encode("utf-8")
        else:
            return None

    def action(self, method):
        return self.get_url(method), self.get_data(method), self.headers


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
        req = urllib.request.Request(url="http://%s:%d/%s" % (self.host, self.port, self.url_index[self.method]), data=data, headers=headers)
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

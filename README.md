### **测试**

* #### 目的

> 测试链是否正常
```text
1.cli在配置正确后，可以处理正确的cmd命令，具体命令要能包括所有支持的cmd命令（只测试通过的情况即可）
2.cli在配置正确后，可以处理外部发来的rpc请求，支持所有当前支持的rpc请求（只测试通过的情况即可）
3.cli如果连不上节点，不会出现运行时的panic而停止，且可以重连上节点
4.测试若干节点组成一个网络（实际测试需要支持在同一台机器上，也要能支持在不同机器上）的情况，具体如：
    质押后，按质押比例产块
    落后启动的节点，可以追赶上到最新块
    能够清空节点后，再去同步，且同步正常
    不同节点内的块数据信息和交易信息基本相同
    一笔转账，能在不同节点都被确认到，且相关账户的数据余额相同
5.加上压力测试和陶永生的测试
6.已生成的链数据，符合链的基础要求
    除了创世块，每个块都记录了其前一个块的hash值，且对应块的高度是当前块高度-1
    块的hash，符合块的内容，块具有正确的签名信息
    找不到高于当前块高度的块、通过不存在的hash无法找到块
    不同块的hash是不同
    块的时间戳是严格递增的
    创世后，数据库中反映了正确的结果
    只创建了一个账户root
    进行了确定数量的货币发行
    进行了确定数量的质押
```

* #### 使用

1. 安装python3
2. 安装依赖包 `pip install -r requirements.txt`
3. 修改`conf/config.ini`配置文件内容
3. 执行测试：`python do_work/valid_test.py`

* #### 目录介绍
```
chain_test-master/
├── bin                 # 入口
│   ├── run.py
│   └── valid_test.py   
├── chain.png
├── cmd_client          # 命令行测试用例
│   ├── cmd_base.py
├── conf
│   ├── config.ini      # 默认配置文件
│   ├── id_rsa_jump     # SSH登陆密钥
│   └── rpc_data.json   # RPC接口
├── logs                # 日志目录
│   └── test_2019_02_13_15_27.log
├── main                # 核心代码
│   ├── deploy_tools.py
│   ├── test_api.py
│   ├── bin_tools.py
│   ├── logger.py
│   └── remote_exec.py
├── README.md
├── requirements.txt    # 依赖包
└── rpc_client          # RPC测试用例
    ├── allinone.py
    ├── base.py
    ├── FindDepositBySource.py
    ├── GetAccountByAddr.py
    ├── GetAccountByName.py
    ├── GetBlockInfoByHeight.py
    ├── GetDepositAccount.py
    ├── GetDepositID.py
    ├── GetDepositScale.py
    ├── GetNodeStatus.py
    ├── PressureTest.py
    ├── UnitTest.py
    └── UnlockWallet.py
```

* #### 配置文件介绍: `config.ini`
```ini
[genesis]                           # 链的标识，genesis标识为创世节点
address = 10.15.101.114             # IP地址
ssh_user = root                     # SSH连接用户名
ssh_port = 22                       # SSH连接端口
ssh_key = G:\python_objects\chain_test\conf\id_rsa_jump     # SSH连接私钥
id = 3005                           # 表示节点ID
del_wallet = False
create_wallet = 0
deposit = False
cli_rpc_port = 60002                # 对应CLI启动的RPC端口
init_cmd = cd /root/work; ./noded init -account root -role miner -nick 3005 -genesis 1 -createwallet 0 -dev 1 ; echo $?     # 初始化节点命令
start_cmd = cd /root/work; nohup ./noded run -account root -nick 3005 -role miner -addr 10.15.101.114:3005 -rpc 1 -rpcaddr 0.0.0.0:40001 -dev 1 &> node_genesis.log &   # 启动节点命令

[node01]                            # node开头标识为节点，与链中其他节点不能相同
address = 10.15.101.114
ssh_user = root
ssh_port = 22
ssh_key = G:\python_objects\chain_test\conf\id_rsa_jump
id = 3006
del_wallet = False
create_wallet = 1
deposit = True
deposit_amount = 10000              # 质押金额
cli_rpc_port = 60012
init_cmd = cd /root/work; ./noded init -account 3006 -role miner -nick 3006 -genesis 0 -createwallet 1 -dev 1 ; echo $?
start_cmd = cd /root/work; nohup ./noded run -account 3006 -nick 3006 -role miner -addr 10.15.101.114:3006 -p2paddr 10.15.101.114:3005 -rpc 1 -rpcaddr 0.0.0.0:40011 -dev 1 -p2pid 0x04ed6eaa0fbf548b3d5f4e400423b49d76daf402308222ca0742e8cd43374b98ba668602be18dd27b7aac8113ea33d69fc583c39e47d25c38f0af975e8c68a357f &> node_3006.log &

[cli1]                              # cli开头标识为CLI，与链中其他CLI不能相同
address = 10.15.101.114
ssh_user = root
ssh_port = 22
ssh_key = G:\python_objects\chain_test\conf\id_rsa_jump
id = 3005
del_wallet = False
rpc_port = 60002                    # CLI启动的RPC端口
start_cmd = cd /root/work; nohup ./pbcli service -clirpcaddr 0.0.0.0 -nick 3005 -noderpcaddr 10.15.101.114 -noderpcport 40001 -clirpcport 60001 -clirpchttpport 60002 &> cli_3005.log &     # 启动CLI命令

[cli2]
address = 10.15.101.114
ssh_user = root
ssh_port = 22
ssh_key = G:\python_objects\chain_test\conf\id_rsa_jump
id = 3006
del_wallet = False
rpc_port = 60012
start_cmd = cd /root/work; nohup ./pbcli service -clirpcaddr 0.0.0.0 -nick 3006 -noderpcaddr 10.15.101.114 -noderpcport 40011 -clirpcport 60011 -clirpchttpport 60012 &> cli_3006.log &
```

* #### 命令行介绍: `run.py`
```bash
$ python run.py -h
usage: Deploy node [-h] {deploy,generate_config,testapi,monitapi,list} ...

positional arguments:
  {deploy,generate_config,testapi,monitapi,list}
                        Subcommand
    deploy              Deployment environment              # 部署操作
    generate_config     Generate configuration file         # 生成配置文件
    testapi             test api                            # 测试RPC接口
    monitapi            monit api result                    # 监控RPC结果
    list                list valid api                      # 列出有效的RPC接口

optional arguments:
  -h, --help            show this help message and exit

$ python run.py deploy -h       # 查询子命令
usage: Deploy node deploy [-h] [-c CONFIG] {start,stop,clean,status,init}

positional arguments:
  {start,stop,clean,status,init}
                        action      # 启动、停止、清除、查看状态、初始化

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG        # 制定配置文件
                        config file name, the file directory is
                        G:\python_objects\chain_test\conf , Default:
                        G:\python_objects\chain_test\conf\config.ini
```

---

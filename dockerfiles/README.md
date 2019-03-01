##### 使用docker版noded、cli

1. 首先获取`noded`、`pbcli`、`cli`可执行程序
2. 下载此`Dockerfile`，与`noded`、`pbcli`、`cli`放在同一目录下
3. 构建镜像：`docker build . -t noded:ubuntu -f noded.dockerfile`
4. 查看镜像：

```shell
$ docker images

REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
noded               ubuntu              ecac6c6d361b        About an hour ago   463MB
```

5. 编辑环境变量文件，在启动时需要传入:

```shell
$ cat > env_file << EOF
> node_user=root		# 启动noded的账号名
> node_pass=123456		# 密码
> bls_pass=123456		# bls账号的密码
> feetaker_pass=123456
> nick=3005				# nick id
> EOF

```

6. 启动容器：

```shell
$ docker run -d --name noded -P -v /mnt/:/root/.pb_data/ --env-file env_file noded:ubuntu
```

7. 查看容器：

```shell
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                                                                               NAMES
523f4f9eae7b        noded:ubuntu        "/root/work/startup_…"   27 minutes ago      Up 27 minutes       0.0.0.0:9046->3005/tcp, 0.0.0.0:9045->40001/tcp, 0.0.0.0:9044->60001/tcp, 0.0.0.0:9043->60002/tcp   noded
```

> 端口介绍：3005为noded service端口，40001为noded rpc端口，60001为pbcli rpc端口，60002为pbcli http端口

8. 查看链状态：

```shell
$ url http://localhost:9043/api/v1/GetNodeStatus
{
  "Code": "NODE_WORKING_FINE",		# 链工作状态，此时为正常
  "Height": "1297",			# 块高度
  "TxSerial": "5613856772279535936",
  "BlockTime": "2019-03-01T11:06:03.020410301Z",	# 出此块的时间
  "BlockTxCount": 1,		# 块中的交易数量
  "BlockPerSecond": 0.5,	# 每秒出块数，此时为2s一个块
  "TxPerSecond": 0.5,
  "TxQueueLength": 0
}
```

---
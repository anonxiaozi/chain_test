#!/usr/bin/env bash

### BEGIN INIT INFO
# Provides:		noded
# Default-Start:	2 3 4 5
# Short-Description:	Noded startup script
### END INIT INFO

. /lib/lsb/init-functions

BASEDIR=/root/work/
NODED=/root/work/noded
PBCLI=/root/work/pbcli
CLI=/root/work/cli
DATADir=/root/.pb_data
ENVFILE=${DATADir}/.noded_env
DB=level
cd /root/work/

do_check_env() {
	if [ -f $ENVFILE ]; then
		node_user=$(grep node_user $ENVFILE | cut -d "=" -f 2)
		node_pass=$(grep node_pass $ENVFILE | cut -d "=" -f 2)
		nick=$(grep nick $ENVFILE | cut -d "=" -f 2)
		feetaker_pass=$(grep feetaker_pass $ENVFILE | cut -d "=" -f 2)
		peers=$(grep peers $ENVFILE | cut -d "=" -f 2)
	fi
}

do_stop() {
	kill -9 $(pgrep noded$) &> /dev/null
}

do_clear() {
	$NODED clear -db $DB -nick $nick
}

do_status() {
	pgrep -a noded$ | grep $nick
	if [ $? == 0 ]; then
		echo "running."
	else
		echo "not running."
	fi
}

do_init() {
do_stop
do_clear
/usr/bin/env expect << EOF
set timeout 20
spawn $NODED init -account $node_user -role miner -nick $nick -genesis 1 -createwallet 1 -dev 0 -db $DB
expect "password:"
send "$node_pass\r"
expect "Repeat password: "
send "$node_pass\r"
expect "password:"
send "$bls_pass\r"
expect "Repeat password:"
send "$bls_pass\r"
expect "password:"
send "$feetaker_pass\r"
expect "Repeat password:"
send "$feetaker_pass\r"
expect eof
EOF
echo -e "node_user=${node_user}\nnode_pass=${node_pass}\nbls_pass=${bls_pass}\nfeetaker_pass=${feetaker_pass}\nnick=${nick}" > $ENVFILE
}

do_start() {
	if [ -z $peers ]; then
		peers=localhost:40001:$(grep 'node p2p id: ' ${DATADir}/logs/node_${nick}_main*.log | awk -F 'node p2p id: ' '{print $2}' | tail -n 1)	# connect yourself
		echo "peers=${peers}" >> $ENVFILE
	fi
	# start pbcli
	nohup /root/work/pbcli service -dbdriver $DB -nick $nick &
	# start noded
	echo $node_pass | exec $NODED run -account $node_user -nick $nick -role miner -addr 0.0.0.0:3005 -rpc 1 -rpcaddr 0.0.0.0:40001 -dev 0 -db $DB -peers ${peers}
}

do_run() {
	do_check_env
	if [ -f ${DATADir}/wallet_${nick}.dat ]; then
		do_start
	else
		do_init && do_start
	fi
}

case "$1" in
	run )
		do_run ;;
	* )
		echo "Usage: $0 run"
		exit 0
esac


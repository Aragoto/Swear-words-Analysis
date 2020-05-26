#!/bin/bash

echo "== Set variables =="
export masternode=$1
export slavenode1=$2
export slavenode2=$3
export nginxnode=$4

docker run -p 5984:5984 -p 4369:4369 -p 9100:9100 -d --name masternode -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password couchdb:2.3.0

sleep 10

echo "== Enable cluster setup =="
docker exec masternode bash -c "echo \"-name couchdb@$masternode\" >> /opt/couchdb/etc/vm.args"


docker restart masternode
sleep 10

echo "== Add nodes to cluster =="
curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"password", "port": 5984, "remote_node": "http://'$slavenode1'/", "remote_current_user": "admin", "remote_current_password": "password" }'
curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "add_node", "host":"'$slavenode1'", "port": "5984", "username": "admin", "password":"password"}'

curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"password", "port": 5984, "remote_node": "http://'$slavenode2'/", "remote_current_user": "admin", "remote_current_password": "password" }'
curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "add_node", "host":"'$slavenode2'", "port": "5984", "username": "admin", "password":"password"}'

curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "admin", "password":"password", "port": 5984, "remote_node": "http://'$nginxnode'/", "remote_current_user": "admin", "remote_current_password": "password" }'
curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "add_node", "host":"'$nginxnode'", "port": "5984", "username": "admin", "password":"password"}'

echo "== Finish cluster =="
curl -X POST -H "Content-Type: application/json" http://admin:password@127.0.0.1:5984/_cluster_setup -d '{"action": "finish_cluster"}'

sleep 10



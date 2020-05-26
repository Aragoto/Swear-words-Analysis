#!/bin/bash

echo "== Set variables =="
export slavenode2=$1

echo "== Start the containers =="

docker run -p 5984:5984 -p 4369:4369 -p 9100:9100 -d --name slavenode2 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password couchdb:2.3.0

sleep 10

docker exec slavenode2 bash -c "echo \"-name couchdb@$slavenode2\" >> /opt/couchdb/etc/vm.args"

echo "== Restart the containers =="
docker restart slavenode2


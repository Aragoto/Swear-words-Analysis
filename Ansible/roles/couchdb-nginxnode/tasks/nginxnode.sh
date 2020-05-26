#!/bin/bash

echo "== Set variables =="
export nginxnode=$1

echo "== Start the containers =="
docker run -p 5984:5984 -p 4369:4369 -p 9100:9100 -d --name nginxnode -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password couchdb:2.3.0
sleep 10

docker exec nginxnode bash -c "echo \"-name couchdb@$nginxnode\" >> /opt/couchdb/etc/vm.args"

echo "== Restart the containers =="
docker restart nginxnode


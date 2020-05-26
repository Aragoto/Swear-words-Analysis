#!/bin/bash

. ./unimelb-comp90024-2020-grp-66-openrc.sh; ansible-playbook --ask-become-pass instance_deploy.yaml

ansible-playbook -i ./inventory/hosts.ini -u ubuntu --key-file=./Group66.pem environment_deploy.yaml

ansible-playbook -i ./inventory/hosts.ini -u ubuntu --key-file=./Group66.pem couchdb_deploy.yaml

ansible-playbook -i ./inventory/hosts.ini -u ubuntu --key-file=./Group66.pem web_deploy.yaml

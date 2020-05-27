# Ansible Automation

In the stage of deployment we implement Ansible to deploy and configure our system environment on all the instances, by executing only one simply shell script ```all_in_one.sh```.  We divided our task into four rasks, with correspondent to one playbook each:

1. Instance deployment-```instance_deploy.yaml```
2. Environment deploment-```environment_deploy.yaml```
3. CouchDB deployment-```couchdb_deploy.yaml```
4. Web deployment-```web_deploy.yaml```

The steps of playbooks are specified in ```roles```.

We used ```host_vars```  to store all variables we need during the deployment.

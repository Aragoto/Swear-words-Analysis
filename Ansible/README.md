# Ansible Automation

In the stage of deployment we implement Ansible to deploy and configure our system environment on all the instances, by executing only one simply shell script.  We divided our task into four rasks, with correspondent to one playbook each:

1. Instance deployment
2. Environment deploment
3. CouchDB deployment
4. Web deployment

The steps of playbooks are specified in ```roles```.

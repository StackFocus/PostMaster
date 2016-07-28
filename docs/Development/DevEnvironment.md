# Create your Environment

We use [Vagrant](https://www.vagrantup.com/) and [Ansible](https://www.ansible.com/).

Install Vagrant using your package manager.  

Provision the VM:

```
$ vagrant up
```

PostMaster should now be running on http://localhost:8080  
The default Postmaster login is `admin:PostMaster`

Your instance is running a local mysql instance.  
The default mysql login is `root:vagrant`


**NOTE:** The instance is not running a local mail server


If you do not want to use Vagrant, just run the ansible playbook against a host:
```
$ ansible-playbook -i "localhost,"  \
-c local /opt/postmaster/git/ops/ansible/site.yml \
--extra-vars="remote_user=vagrant"  \
--extra-vars="provision_type=dev"
```

## Code Updates

The code is location at:
`/opt/postmaster/git`

### Activate the virtualenv
```
$ source /opt/postmaster/env/bin/activate
```

### Apply the Code Updates
Your code repo is linked onto the VM, so updates are going to be there automatically, however each python file update will require you to restart the
service.  On the vagrant host (`vagrant ssh`)  

```
$ sudo service apache2 restart
```

### Run the test suite
```
$ py.test tests
```

### Check Any Logs
```
/opt/postmaster/logs/postmaster.log
/var/log/apache2/postmaster.access.log
/var/log/apache2/postmaster.error.log
```

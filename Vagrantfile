# -*- mode: ruby -*-
# vi: set ft=ruby :

# do this to patch ansible because
#https://github.com/mitchellh/vagrant/issues/6793
$script = <<SCRIPT
GALAXY=/usr/local/bin/ansible-galaxy
echo '#!/usr/bin/env python2
import sys
import os

args = sys.argv
if args[1:] == ["--help"]:
  args.insert(1, "info")

os.execv("/usr/bin/ansible-galaxy", args)
' | sudo tee $GALAXY
sudo chmod 0755 $GALAXY
sudo apt-key update
sudo apt-key update
SCRIPT

Vagrant.configure(2) do |config|
  config.vm.box = "puphpet/ubuntu1404-x64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.synced_folder "./", "/opt/postmaster/git"


 config.vm.provision "shell", inline: $script

 config.vm.provision :ansible_local do |ansible|
    ansible.verbose = "v"
    ansible.install = true
    ansible.raw_arguments = [
      '--extra-vars="remote_user=vagrant"',
      '--extra-vars="provision_type=dev"'
    ]
    # I don't know why, but extra_vars doesn't work with ansible_local
    # or it could be something with my host. raw_arguments for local though
    ansible.extra_vars = {
      remote_user: "vagrant",
      provision_type: "dev"
    }
    ansible.playbook = "ops/ansible/site.yml"
  end
end

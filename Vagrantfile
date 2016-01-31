# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "puphpet/ubuntu1404-x64"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.synced_folder "./", "/var/www/SwagMail"
  config.vm.provision "shell", path: "Vagrantscript.sh"
end

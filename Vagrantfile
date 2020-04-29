# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.define "simpleidml", primary: true do |simpleidml|
    simpleidml.vm.box = "ubuntu/bionic64"
    simpleidml.vm.hostname = "simpleidml"

    simpleidml.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
    end

    simpleidml.vm.provision "shell", inline: <<-SHELL
      apt-get update
      DEBIAN_FRONTEND="noninteractive" apt-get install -y build-essential python3-venv \
       python3-dev
    SHELL

    simpleidml.vm.provision "create-virtualenv-py3", type: :shell, privileged: false, inline: <<-SHELL
      cd ~
      python3 -m venv venv_py3
    SHELL

    simpleidml.vm.provision "pip3-install", type: :shell, privileged: false, inline: <<-SHELL
      source ~/venv_py3/bin/activate
      pip3 install --upgrade pip
      pip3 install -r /vagrant/requirements_dev.txt
    SHELL

    simpleidml.vm.provision "bashrc", type: :shell, privileged: false, inline: <<-SHELL
      echo "cd /vagrant" >> ~/.bashrc
      echo "source ~/venv_py3/bin/activate" >> ~/.bashrc
    SHELL
  end
end

Vagrant.configure("2") do |config|
    config.vm.box = "hashicorp/bionic64"
    #config.vm.provision :shell, path: "deployment/bootstrap.sh"
    config.vm.provision "ansible_local" do |ansible|
        ansible.playbook = "provision/ubuntu_playbook.yml"
    end
end

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.define "edtest" do |edtest|
    edtest.vm.box = "ubuntu1404"
    edtest.vm.hostname = "edtest"
    edtest.vm.network "private_network", ip: "192.168.50.10"
    edtest.vm.box_url = "https://oss-binaries.phusionpassenger.com/vagrant/boxes/latest/ubuntu-14.04-amd64-vbox.box"
    edtest.vm.provision "ansible" do |ansible|
      ansible.playbook = "./ansible/edtest.yaml"
      ansible.sudo = true
      ansible.extra_vars = { ansible_ssh_user: 'vagrant' }
    end
    edtest.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", 8192]
      v.customize ["modifyvm", :id, "--cpus", 4]
    end
  end

end

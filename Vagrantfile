# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.define :flask_social_example_vm do |config|
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    config.vm.network :hostonly, "192.168.0.10"
    config.vm.provision :chef_solo do |chef|
      chef.cookbooks_path = "cookbooks"
      chef.add_recipe "flask-social-example"
      chef.json.merge!({
        :postgresql => {
          :config => {
            :listen_addresses => "*"
          },
          :password => {
            :postgres => "password"
          },
          :pg_hba => [
            {:type => 'local', :db => 'all', :user => 'postgres', :addr => nil, :method => 'trust'},
            {:type => 'local', :db => 'all', :user => 'all', :addr => nil, :method => 'trust'},
            {:type => 'host', :db => 'all', :user => 'all', :addr => 'all', :method => 'trust'}
          ]
        }
      })
    end
  end
end

include_recipe "postgresql::server"
include_recipe "database::postgresql"

postgresql_connection_info = {
  :host => 'localhost' ,
  :port => 5432,
  :username => 'postgres',
  :password => node['postgresql']['password']['postgres']
  }

postgresql_database "flask_social_example_development" do
  connection postgresql_connection_info
  action :create
end
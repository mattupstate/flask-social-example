name              "flask-social-example"
maintainer        "Matt Wright"
maintainer_email  "matt@nobien.net"
license           "Apache 2.0"
description       "Installs and configures various software to run flask-social-example"
long_description  IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version           "0.1.0"
recipe            "flask-social-example", "Installs and configures various software to run flask-social-example"

supports "ubuntu"
depends "database"
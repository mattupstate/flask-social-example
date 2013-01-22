from flask.ext.assets import ManageAssets
from flask.ext.script import Manager
from flask.ext.security.script import CreateUserCommand

from app import create_app

manager = Manager(create_app())
manager.add_command("assets", ManageAssets())
manager.add_command('create_user', CreateUserCommand())

if __name__ == "__main__":
    manager.run()
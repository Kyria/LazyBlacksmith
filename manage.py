from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand

from lazyblacksmith import app
from lazyblacksmith.models import db
from lazyblacksmith.commands.sde_import import SdeImport

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('sde_import', SdeImport)

if __name__ == '__main__':
    manager.run()

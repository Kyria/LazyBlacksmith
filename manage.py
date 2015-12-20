# -*- encoding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand

import config
from lazyblacksmith.app import create_app
from lazyblacksmith.models import db
from lazyblacksmith.commands.sde_import import SdeImport

app = create_app(config)

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('sde_import', SdeImport)

if __name__ == '__main__':
    manager.run()

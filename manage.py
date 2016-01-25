# -*- encoding: utf-8 -*-
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager

import config

from lazyblacksmith.app import create_app
from lazyblacksmith.commands.sde_import import SdeImport
from lazyblacksmith.models import db

app = create_app(config)

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('sde_import', SdeImport)

if __name__ == '__main__':
    manager.run()

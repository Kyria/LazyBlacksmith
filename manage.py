# -*- encoding: utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

import config
from lazyblacksmith.app import create_app
from lazyblacksmith.models import db
from lbcmd.admin import LbAdmin
from lbcmd.sde_import import SdeImport

app = create_app(config)

db.init_app(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('sde_import', SdeImport)
manager.add_command('lb_admin', LbAdmin)

if __name__ == '__main__':
    manager.run()

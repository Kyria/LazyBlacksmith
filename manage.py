# -*- encoding: utf-8 -*-
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from flask_script import Manager

import config

from lazyblacksmith.app import create_app
from lazyblacksmith.models import db

app = create_app(config)

db.init_app(app)
migrate = Migrate(app, db)

from lazyblacksmith.commands.admin import LbAdmin
from lazyblacksmith.commands.manual_celery_tasks import ManualCeleryTasks
from lazyblacksmith.commands.sde_import import SdeImport

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('sde_import', SdeImport)
manager.add_command('celery_task', ManualCeleryTasks)
manager.add_command('lb_admin', LbAdmin)

if __name__ == '__main__':
    manager.run()

# -*- encoding: utf-8 -*-
from flask_script import Manager

import config
from lbtasks.task_app import create_app
from lbtasks.flask_celery import celery_app

app = create_app(config)
celery_app.init_app(app)

manager = Manager(app)

# we need to import it here, because of flask app
from lbcmd.manual_celery_tasks import ManualCeleryTasks
manager.add_command('tasks', ManualCeleryTasks)

if __name__ == '__main__':
    manager.run()

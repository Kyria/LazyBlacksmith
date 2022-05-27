# -*- encoding: utf-8 -*-
from flask.cli import FlaskGroup

import config
from lbtasks.task_app import create_app
from lbtasks.flask_celery import celery_app


def create_cli_app():
    app = create_app(config)

    celery_app.init_app(app)

    # we need to import it here, because of flask app
    from lbcmd.manual_celery_tasks import celery_tasks
    app.cli.add_command(celery_tasks)

    return app


cli = FlaskGroup(create_app=create_cli_app)

if __name__ == '__main__':
    cli()

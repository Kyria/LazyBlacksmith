# -*- encoding: utf-8 -*-
from flask.cli import FlaskGroup
from flask_migrate import Migrate

import config
from lazyblacksmith.app import create_app
from lazyblacksmith.models import db
from lbcmd.admin import lb_admin
from lbcmd.sde_import import sde_import

def create_cli_app():
    app = create_app(config)

    migrate = Migrate(app, db)

    app.cli.add_command(lb_admin)
    app.cli.add_command(sde_import)
    return app


cli = FlaskGroup(create_app=create_cli_app)

if __name__ == '__main__':
    cli()

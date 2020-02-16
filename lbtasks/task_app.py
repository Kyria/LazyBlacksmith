# -*- encoding: utf-8 -*-"
""" Provide light app factory for flask app with celery requirements """
from flask import Flask

from lazyblacksmith.extension.database import db
from lazyblacksmith.extension.cache import CACHE


def create_app(config_object):
    """Flask and huey app maker.
    Loads less stuff than regular app

    Args:
        config_object (object/module): configuration object

    Returns:
        tuple: flask_app tuple
    """
    # app
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)

    register_extensions(app)

    # return app
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.app = app
    db.init_app(app)
    CACHE.init_app(app)

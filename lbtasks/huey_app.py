# -*- encoding: utf-8 -*-"
""" Provide light app factory for huey and flask app """
from flask import Flask
from huey import RedisHuey

from lazyblacksmith.models import db
from lazyblacksmith.extension.cache import CACHE

import config


def create_app(config_object):
    """Flask and huey app maker.
    Loads less stuff than regular app

    Args:
        config_object (object/module): configuration object

    Returns:
        tuple: (flask_app, huey_object) tuple
    """
    # app
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)

    huey = RedisHuey(
        host=config.HUEY_REDIS_HOST,
        port=config.HUEY_REDIS_PORT,
        db=config.HUEY_REDIS_DB,
        name=config.HUEY_QUEUE_NAME
    )

    register_extensions(app)

    # return app
    return app, huey


def register_extensions(app):
    """Register Flask extensions."""
    db.app = app
    db.init_app(app)
    CACHE.init_app(app)

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

def create_app(config_object):
    # app
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)

    # blueprint stuff
    from lazyblacksmith.views.ajax import ajax
    from lazyblacksmith.views.blueprint import blueprint
    from lazyblacksmith.views.home import home
    from lazyblacksmith.views.template import template
    from lazyblacksmith.utils.template_filter import templatefilter
    app.register_blueprint(blueprint, url_prefix='/blueprint')
    app.register_blueprint(ajax, url_prefix='/ajax')
    app.register_blueprint(template, url_prefix='/template')
    app.register_blueprint(home)
    app.register_blueprint(templatefilter)

    # db
    from lazyblacksmith.models import db
    db.app = app
    db.init_app(app)

    # csrf
    csrf = CsrfProtect()
    csrf.init_app(app)

    # cache
    from cache import cache
    cache.init_app(app)

    # return app
    return app
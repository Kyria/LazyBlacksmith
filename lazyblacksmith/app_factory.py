# -*- encoding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

from sqlalchemy.orm import sessionmaker, scoped_session

# blueprint stuff
from lazyblacksmith.views.ajax import ajax
from lazyblacksmith.views.blueprint import blueprint
from lazyblacksmith.views.home import home
from lazyblacksmith.views.industry_index import industry
from lazyblacksmith.views.sso import sso

# helpers
from lazyblacksmith.views.template import template
from lazyblacksmith.utils.template_filter import templatefilter

# others
from lazyblacksmith.cache import cache
from lazyblacksmith.models import db
from lazyblacksmith.login_manager import login_manager

def create_app(config_object):
    # app
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)

    # register blueprints & helper blueprints
    app.register_blueprint(blueprint, url_prefix='/blueprint')
    app.register_blueprint(ajax, url_prefix='/ajax')
    app.register_blueprint(template, url_prefix='/template')
    app.register_blueprint(industry, url_prefix='/industry_index')
    app.register_blueprint(sso, url_prefix='/sso')
    app.register_blueprint(home)
    app.register_blueprint(templatefilter)

    # db
    db.app = app
    db.init_app(app)

    # csrf
    csrf = CsrfProtect()
    csrf.init_app(app)

    # cache
    cache.init_app(app)

    # login
    login_manager.init_app(app)

    # return app
    return app
# -*- encoding: utf-8 -*-
from flask import Flask, g, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

import flask_login

# blueprint stuff
from lazyblacksmith.views.ajax import ajax
from lazyblacksmith.views.blueprint import blueprint
from lazyblacksmith.views.home import home
from lazyblacksmith.views.industry_index import industry
from lazyblacksmith.views.sso import sso

# helpers
from lazyblacksmith.views.template import template
from lazyblacksmith.utils.template_filter import templatefilter

# db
from lazyblacksmith.models import db

# extensions
from lazyblacksmith.extension.cache import cache
from lazyblacksmith.extension.login_manager import login_manager
from lazyblacksmith.extension.celery_app import celery_app

def create_app(config_object):
    # app
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)
    register_before_requests(app)
    register_errorhandlers(app)
    register_context_processors(app)
    register_teardown_appcontext(app)

    # return app
    return app

def register_blueprints(app):
    """ register blueprints & helper blueprints """
    app.register_blueprint(blueprint, url_prefix='/blueprint')
    app.register_blueprint(ajax, url_prefix='/ajax')
    app.register_blueprint(template, url_prefix='/template')
    app.register_blueprint(industry, url_prefix='/industry_index')
    app.register_blueprint(sso, url_prefix='/sso')
    app.register_blueprint(home)
    app.register_blueprint(templatefilter)

def register_extensions(app):
    """Register Flask extensions."""
    db.app = app
    db.init_app(app)
    csrf = CsrfProtect()
    csrf.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    celery_app.init_app(app)

def register_errorhandlers(app):
    """Add errorhandlers to the app."""
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)

def register_before_requests(app):
    """Register before_request functions."""
    def global_user():
        g.user = flask_login.current_user
    app.before_request(global_user)


def register_context_processors(app):
    """Register context_processor functions."""
    def inject_user():
        try:
            return {'user': g.user}
        except AttributeError:
            return {'user': None}
    app.context_processor(inject_user)

def register_teardown_appcontext(app):
    """Register teardown_appcontext functions."""
    def commit_on_success(error=None):
        if error is None:
            db.session.commit()
    app.teardown_appcontext(commit_on_success)
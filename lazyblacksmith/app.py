# -*- encoding: utf-8 -*-
from flask import Flask
from flask import flash
from flask import g
from flask import render_template
from flask_wtf.csrf import CSRFProtect

import flask_login

# helpers
from lazyblacksmith.utils.template_filter import templatefilter
from lazyblacksmith.utils.time import utcnow

# db
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User
from lazyblacksmith.models import db

# extensions
from lazyblacksmith.extension.cache import cache
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.login_manager import login_manager


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
    # blueprint import, only here because of exts
    from lazyblacksmith.views import ajax_eve_api
    from lazyblacksmith.views import ajax_eve_sde
    from lazyblacksmith.views import ajax_account
    from lazyblacksmith.views import blueprint
    from lazyblacksmith.views import home
    from lazyblacksmith.views import price
    from lazyblacksmith.views import sso
    from lazyblacksmith.views import template
    from lazyblacksmith.views import account

    """ register blueprints & helper blueprints """
    app.register_blueprint(ajax_eve_api, url_prefix='/ajax/eveapi')
    app.register_blueprint(ajax_eve_sde, url_prefix='/ajax/evesde')
    app.register_blueprint(ajax_account, url_prefix='/ajax/account')
    app.register_blueprint(blueprint, url_prefix='/blueprint')
    app.register_blueprint(template, url_prefix='/template')
    app.register_blueprint(sso, url_prefix='/sso')
    app.register_blueprint(price, url_prefix='/price')
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(home)
    app.register_blueprint(templatefilter)


def register_extensions(app):
    """Register Flask extensions."""
    db.app = app
    db.init_app(app)
    csrf = CSRFProtect()
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

    for errcode in [401, 403, 404, 500]:
        app.errorhandler(errcode)(render_error)


def register_before_requests(app):
    """Register before_request functions."""
    def global_user():
        g.user = flask_login.current_user

    def check_and_update_user():
        """ check for invalid token and print message and update last seen """
        if flask_login.current_user.is_authenticated:
            char_id = flask_login.current_user.character_id
            count_error = TokenScope.query.filter_by(
                valid=False
            ).join(User).filter(
                ((User.main_character_id.is_(None)) &
                    (User.character_id == char_id)) |
                (User.main_character_id == char_id)
            ).filter(
                ((TokenScope.last_update.is_(None)) &
                    (TokenScope.updated_at >= User.current_login_at)) |
                (User.current_login_at.is_(None)) |
                (TokenScope.last_update >= User.current_login_at)
            ).count()

            if count_error > 0:
                flash('You have at least one scope that have been invalidate.'
                      ' Please take a moment to check and update it, or remove it.', 'danger')

            flask_login.current_user.current_login_at = utcnow()
            db.session.commit()

    app.before_request(global_user)
    app.before_request(check_and_update_user)


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

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect

from lazyblacksmith.models import db
from lazyblacksmith.views.blueprint import blueprint
from lazyblacksmith.views.ajax import ajax
from lazyblacksmith.utils.template_filter import templatefilter

import config

app = Flask(__name__.split('.')[0])

app.config.from_object(config)
app.register_blueprint(blueprint, url_prefix='/blueprint')
app.register_blueprint(ajax, url_prefix='/ajax')
app.register_blueprint(templatefilter)

# db
db.app = app
db.init_app(app)

# csrf
csrf = CsrfProtect()
csrf.init_app(app)

from .views.home import index
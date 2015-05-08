from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from lazyblacksmith.models import db

import config

app = Flask(__name__.split('.')[0])

app.config.from_object(config)

# no app object passed! Instead we use use db.init_app in the factory.
db.app = app
db.init_app(app)
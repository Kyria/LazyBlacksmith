# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.app import create_app
from lazyblacksmith.celery_app import celery_app

app = create_app(config)
app.app_context().push()

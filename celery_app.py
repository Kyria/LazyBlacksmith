# -*- encoding: utf-8 -*-
from lazyblacksmith.app import create_app
from lazyblacksmith.celery_app import celery_app
import config

app = create_app(config)
app.app_context().push()
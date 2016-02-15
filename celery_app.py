# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.app import create_app
from lazyblacksmith.extension.celery_app import celery_app

import celery_crontab

app = create_app(config)
app.app_context().push()
celery_app.conf.update(celery_crontab)

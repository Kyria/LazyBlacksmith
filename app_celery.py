# -*- encoding: utf-8 -*-
# pylint: disable=unused-import
# flake8: noqa
from __future__ import absolute_import
import logging

import config

from lbtasks.flask_celery import celery_app
from lbtasks.task_app import create_app

# disable / enable loggers we want
logging.getLogger('pyswagger').setLevel(logging.ERROR)
logging.getLogger('lb.tasks').setLevel(logging.WARNING)

celery_app.init_app(create_app(config))

celery_app.conf.imports = [
    'lbtasks.tasks',
    'lbtasks.tasks.task_spawner'
]

# -*- encoding: utf-8 -*-
# pylint: disable=unused-import
# flake8: noqa
""" entry point for huey_consumer """
import logging

import config

from lbtasks import CELERY_APP
from lbtasks.task_app import create_app

# disable / enable loggers we want
logging.getLogger('pyswagger').setLevel(logging.ERROR)
logging.getLogger('lb.tasks').setLevel(logging.WARNING)

CELERY_APP.init_app(create_app(config))

CELERY_APP.conf.imports = [
    'lbtasks.tasks.task_adjusted_price_base_cost',
    'lbtasks.tasks.task_industry_indexes',
]
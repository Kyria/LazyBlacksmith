# -*- encoding: utf-8 -*-
# pylint: disable=unused-import
# flake8: noqa
from __future__ import absolute_import
import logging

import config

from lbtasks.flask_celery import celery_app
from lbtasks.task_app import create_app
from celery.schedules import crontab

# disable / enable loggers we want
logging.getLogger('pyswagger').setLevel(logging.ERROR)
logging.getLogger('lb.tasks').setLevel(logging.WARNING)

celery_app.init_app(create_app(config))
celery_app.autodiscover_tasks(packages=['lbtasks'])
celery_app.conf.beat_schedule = {
    'purge': {
        'task': 'schedule.purge',
        'schedule': crontab(minute=0, hour=1),
    },
    'spawn_char_tasks': {
        'task': 'schedule.character_task_spawner',
        'schedule': crontab(minute='*/5'),
    },
    'update_indexes': {
        'task': 'universe.industry_indexes',
        'schedule': crontab(minute=0, hour=0),
    },
    'update_adjusted_price': {
        'task': 'universe.adjusted_price',
        'schedule': crontab(minute=0, hour=0),
    },
    'update_market_order': {
        'task': 'universe.spawn_market_price_tasks',
        'schedule': crontab(minute='*/30'),
    },
}
celery_app.conf.timezone = 'UTC'

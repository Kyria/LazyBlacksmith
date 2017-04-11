# -*- encoding: utf-8 -*-
import config
import logging

from celery.schedules import crontab
from lazyblacksmith.app import create_app
from lazyblacksmith.extension.celery_app import celery_app

# disable / enable loggers we want
logging.getLogger('pyswagger').setLevel(logging.ERROR)



app = create_app(config)
app.app_context().push()

celery_app.init_app(app)

#celery_app.conf.broker_url = config.broker_url
celery_app.conf.beat_schedule.update({
    'character-task-spawner': {
        'task': 'schedule.character_task_spawner',
        'schedule': crontab(minute='*'),
    },
    'universe-task-spawner': {
        'task': 'schedule.universe_task_spawner',
        'schedule': crontab(minute='*/30'),
    },
})

celery_app.conf.imports = [
    'lazyblacksmith.tasks.task_spawner',
    'lazyblacksmith.tasks.market.adjusted_price',
    'lazyblacksmith.tasks.market.market_order',
    'lazyblacksmith.tasks.industry.indexes',
    'lazyblacksmith.tasks.character.skills',
    'lazyblacksmith.tasks.character.blueprints',
]

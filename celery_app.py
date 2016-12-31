# -*- encoding: utf-8 -*-
import config

from celery.schedules import crontab
from lazyblacksmith.app import create_app
from lazyblacksmith.extension.celery_app import celery_app

app = create_app(config)
app.app_context().push()

celery_app.init_app(app)

celery_app.conf.broker_url = config.broker_url
celery_app.conf.beat_schedule.update({
    'adjusted-price': {
        'task': 'schedule.update_adjusted_price',
        'schedule': crontab(hour=1, minute=30),
    },
    'item-market-price': {
        'task': 'schedule.update_market_price',
        'schedule': crontab(hour='*/2', minute=00),
    },
    'industry-index': {
        'task': 'schedule.update_industry_indexes',
        'schedule': crontab(hour='*', minute=00),
    },
})

celery_app.conf.imports = [
    'lazyblacksmith.tasks.adjusted_price',
    'lazyblacksmith.tasks.market_order',
    'lazyblacksmith.tasks.industry_index',
]

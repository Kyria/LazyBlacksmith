# -*- encoding: utf-8 -*-
import config

from celery.schedules import crontab
from lazyblacksmith.app import create_app
from lazyblacksmith.extension.celery_app import celery_app

app = create_app(config)
app.app_context().push()

celery_app.conf.update({
    'CELERYBEAT_SCHEDULE': {
        'adjusted-price': {
            'task': 'lazyblacksmith.tasks.adjusted_price.get_adjusted_price',
            'schedule': crontab(hour=1, minute=30),
        },
        'item-market-price': {
            'task': 'lazyblacksmith.tasks.market_order.update_market_price',
            'schedule': crontab(hour='*', minute=00),
        },
    }
})

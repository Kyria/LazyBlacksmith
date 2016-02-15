from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'adjusted-price': {
        'task': 'lazyblacksmith.tasks.adjusted_price.get_adjusted_price',
        'schedule': crontab(hour=1, minute=30),
    },
    'item-market-price': {
        'task': 'lazyblacksmith.tasks.market_order.update_market_price',
        'schedule': crontab(hour='*', minute=00),
    },
}

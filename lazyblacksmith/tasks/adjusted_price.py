# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_markets_prices
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import TaskStatus
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import json
import pytz

@celery_app.task(name="schedule.update_adjusted_price")
def update_adjusted_price():
    # delete everything from table first.
    db.engine.execute("TRUNCATE TABLE %s" % ItemAdjustedPrice.__tablename__)
    db.session.commit()

    item_adjusted_price = []
    count = 0

    market_price = esiclient.request(get_markets_prices())
    for item_price in market_price.data:
        count += 1
        item_adjusted_price.append({
            'item_id': item_price.type_id,
            'price': item_price.adjusted_price or 0.00
        })

    db.engine.execute(
        ItemAdjustedPrice.__table__.insert(),
        item_adjusted_price
    )
    db.session.commit()
    
    task_status = TaskStatus(
        name='schedule.update_adjusted_price',
        expire=datetime(
            *parsedate(market_price.header['Expires'][0])[:6]
        ).replace(tzinfo=pytz.utc),
        last_run=utcnow(),
        results=json.dumps({'inserted': count})
    )
    db.session.merge(task_status)
    db.session.commit()
    
    return count, count

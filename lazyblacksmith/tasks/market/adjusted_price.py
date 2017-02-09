# -*- encoding: utf-8 -*-
from ..lb_task import LbTask

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_markets_prices
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import json
import pytz


@celery_app.task(name="update_adjusted_price", base=LbTask, bind=True)
def task_update_adjusted_price(self):
    """ Task that update the adjusted prices from the API """
    self.start()
    item_adjusted_price = []
    count = 0

    market_price = esiclient.request(get_markets_prices())

    if market_price.status == 200:
        for item_price in market_price.data:
            count += 1
            item_adjusted_price.append({
                'item_id': item_price.type_id,
                'price': item_price.adjusted_price or 0.00
            })

        db.engine.execute(
            "TRUNCATE TABLE %s" % ItemAdjustedPrice.__tablename__
        )
        db.engine.execute(
            ItemAdjustedPrice.__table__.insert(),
            item_adjusted_price
        )
        db.session.commit()
        self.end(TaskState.SUCCESS)
        
    else:
        self.end(TaskState.ERROR)
        

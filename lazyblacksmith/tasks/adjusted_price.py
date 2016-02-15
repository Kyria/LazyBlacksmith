# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_crest
from sqlalchemy.exc import IntegrityError


@celery_app.task
def get_adjusted_price():
    # crest stuff
    crest = get_crest()
    item_adjusted_price = {}
    marketPrice = get_all_items(crest.marketPrices())
    for itemPrice in marketPrice:
        item_adjusted_price[int(itemPrice.type.id)] = (itemPrice.adjustedPrice, itemPrice.type.name)

    count = len(item_adjusted_price)
    failed = 0
    # update existing
    for item_price in ItemAdjustedPrice.query.yield_per(100):
        if item_price.item_id in item_adjusted_price:
            item_price.adjusted_price = item_adjusted_price[item_price.item_id][0]
            del item_adjusted_price[item_price.item_id]

    db.session.commit()

    for id, price in item_adjusted_price.items():
        try:
            item_price = ItemAdjustedPrice(item_id=id, price=price[0])
            db.session.add(item_price)
            db.session.commit()
        except IntegrityError:
            failed += 1
            db.session.rollback()
            # print "Error: (%s) %s" % (id, price[1])

    return (count-failed, count)

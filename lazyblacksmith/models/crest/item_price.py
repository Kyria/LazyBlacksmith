# -*- encoding: utf-8 -*-
from . import db

from datetime import datetime
from lazyblacksmith.models.utcdatetime import UTCDateTime
from sqlalchemy import func
from sqlalchemy.orm import MapperExtension


class ItemPriceExtension(MapperExtension):
    def before_insert(self, mapper, connection, instance):
        instance.update_at = datetime.utcnow()

    def before_update(self, mapper, connection, instance):
        instance.update_at = datetime.utcnow()


class ItemPrice(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    region_id = db.Column(db.Integer, primary_key=True)
    update_at = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    sell_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)
    buy_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)

    __mapper_args__ = {
        'extension': ItemPriceExtension()
    }

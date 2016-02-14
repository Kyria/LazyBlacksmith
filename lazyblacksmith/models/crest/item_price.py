# -*- encoding: utf-8 -*-
from . import db

from lazyblacksmith.models.utcdatetime import UTCDateTime
from sqlalchemy import func


class ItemPrice(db.Model):

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    update_at = db.Column(UTCDateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sell_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)
    buy_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)
    adjusted_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)

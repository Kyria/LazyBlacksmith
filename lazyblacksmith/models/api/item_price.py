# -*- encoding: utf-8 -*-
from . import db

from lazyblacksmith.models.utcdatetime import UTCDateTime
from lazyblacksmith.utils.time import utcnow

from sqlalchemy import func


class ItemPrice(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    region_id = db.Column(db.Integer, primary_key=True)
    sell_price = db.Column(
        db.Numeric(
            precision=17,
            scale=2,
            decimal_return_scale=2,
            asdecimal=False
        ),
        nullable=True
    )
    buy_price = db.Column(
        db.Numeric(
            precision=17,
            scale=2,
            decimal_return_scale=2,
            asdecimal=False
        ),
        nullable=True
    )
    updated_at = db.Column(
        UTCDateTime(timezone=True), server_default=func.now()
    )

    def get_delta_update(self):
        return self.updated_at - utcnow()

# -*- encoding: utf-8 -*-
from . import db

class MarketOrder(db.Model):
    """ Model that describe a market order with the info we need """
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    item_id = db.Column(db.Integer)
    region_id = db.Column(db.Integer)
    system_id = db.Column(db.Integer)
    price = db.Column(
        db.Numeric(
            precision=17,
            scale=2,
            decimal_return_scale=2,
            asdecimal=False
        ),
        nullable=True
    )
    is_buy_order = db.Column(db.Boolean(), default=False)
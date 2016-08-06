# -*- encoding: utf-8 -*-
from . import db


class ItemPrice(db.Model):
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    region_id = db.Column(db.Integer, primary_key=True)
    sell_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)
    buy_price = db.Column(db.Numeric(precision=17, scale=2, decimal_return_scale=2), nullable=True)

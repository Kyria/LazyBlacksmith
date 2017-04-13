# -*- encoding: utf-8 -*-
from . import db


class ActivityProduct(db.Model):

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)
    product_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=True)
    probability = db.Column(db.Numeric(precision=3, scale=2, decimal_return_scale=2, asdecimal=False), nullable=True)

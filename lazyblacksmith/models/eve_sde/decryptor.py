# -*- encoding: utf-8 -*-
from . import db


class Decryptor(db.Model):
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)   
    probability_multiplier = db.Column(db.Numeric(precision=4, scale=2, decimal_return_scale=2, asdecimal=False), nullable=True)
    material_modifier = db.Column(db.Integer, nullable=True)
    time_modifier = db.Column(db.Integer, nullable=True)
    run_modifier = db.Column(db.Integer, nullable=True)

    item = db.relationship("Item")
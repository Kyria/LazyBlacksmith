# -*- encoding: utf-8 -*-
from . import db


class ActivityMaterial(db.Model):

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)
    material_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=True)

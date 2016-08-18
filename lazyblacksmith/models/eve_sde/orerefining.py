# -*- encoding: utf-8 -*-
from . import db


class OreRefining(db.Model):
    ore_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)   
    material_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=True)
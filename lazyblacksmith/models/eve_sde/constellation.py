# -*- encoding: utf-8 -*-
from . import db

class Constellation(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
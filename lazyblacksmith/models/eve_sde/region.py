# -*- encoding: utf-8 -*-
from . import db

class Region(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(100), nullable=False)
    wh = db.Column(db.Boolean, default=False)
    
    __mapper_args__ = {
        "order_by":name
    }
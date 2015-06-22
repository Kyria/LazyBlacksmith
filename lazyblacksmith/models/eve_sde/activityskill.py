# -*- encoding: utf-8 -*-
from . import db

class ActivitySkill(db.Model):
 
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    level = db.Column(db.Integer, nullable=True)

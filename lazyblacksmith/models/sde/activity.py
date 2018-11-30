# -*- encoding: utf-8 -*-
from . import db


class Activity(db.Model):

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    time = db.Column(db.Integer, nullable=True)
    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)

    @classmethod
    def get_activity_name(cls, activity):
        return cls.ACTIVITIES[activity]

    @classmethod
    def check_activity_existence(cls, activity):
        return activity in cls.ACTIVITIES

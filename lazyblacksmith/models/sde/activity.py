# -*- encoding: utf-8 -*-
from . import db


class Activity(db.Model):

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    time = db.Column(db.Integer, nullable=True)
    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)

    ACTIVITY_NONE = 0
    ACTIVITY_MANUFACTURING = 1
    ACTIVITY_RESEARCHING_TIME_EFFICIENCY = 3
    ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY = 4
    ACTIVITY_COPYING = 5
    ACTIVITY_INVENTION = 8

    ACTIVITIES = {
        ACTIVITY_NONE: 'None',
        ACTIVITY_MANUFACTURING: 'Manufacturing',
        ACTIVITY_RESEARCHING_TIME_EFFICIENCY: 'Time efficiency',
        ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY: 'Material efficiency',
        ACTIVITY_COPYING: 'Copy',
        ACTIVITY_INVENTION: 'Invention',
    }

    @classmethod
    def get_activity_name(cls, activity):
        return cls.ACTIVITIES[activity]

    @classmethod
    def check_activity_existence(cls, activity):
        return activity in cls.ACTIVITIES

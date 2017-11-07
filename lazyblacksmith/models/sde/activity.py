# -*- encoding: utf-8 -*-
from . import db


class Activity(db.Model):

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    time = db.Column(db.Integer, nullable=True)
    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)

    NONE = 0
    MANUFACTURING = 1
    RESEARCH_TIME_EFFICIENCY = 3
    RESEARCH_MATERIAL_EFFICIENCY = 4
    COPYING = 5
    INVENTION = 8
    REACTIONS = 11

    ACTIVITIES = {
        NONE: 'None',
        MANUFACTURING: 'Manufacturing',
        RESEARCH_TIME_EFFICIENCY: 'Time efficiency',
        RESEARCH_MATERIAL_EFFICIENCY: 'Material efficiency',
        COPYING: 'Copy',
        INVENTION: 'Invention',
        REACTIONS: 'Reactions',
    }

    @classmethod
    def get_activity_name(cls, activity):
        return cls.ACTIVITIES[activity]

    @classmethod
    def check_activity_existence(cls, activity):
        return activity in cls.ACTIVITIES

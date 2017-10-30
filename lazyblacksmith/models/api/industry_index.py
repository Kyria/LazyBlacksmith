# -*- encoding: utf-8 -*-
from . import db
from lazyblacksmith.models import Activity


class IndustryIndex(db.Model):

    solarsystem_id = db.Column(
        db.Integer, db.ForeignKey('solar_system.id'), primary_key=True
    )
    solarsystem = db.relationship('SolarSystem', backref=db.backref('indexes'))

    activity = db.Column(db.Integer, primary_key=True, autoincrement=False)
    cost_index = db.Column(
        db.Numeric(
            precision=20,
            scale=19,
            decimal_return_scale=19,
            asdecimal=False
        ),
        nullable=True)

    @classmethod
    def activity_string_to_activity(cls, activity_string):
        if activity_string == 'invention':
            return Activity.INVENTION
        if activity_string == 'manufacturing':
            return Activity.MANUFACTURING
        if activity_string == 'researching_time_efficiency':
            return Activity.RESEARCH_TIME_EFFICIENCY
        if activity_string == 'researching_material_efficiency':
            return Activity.RESEARCH_MATERIAL_EFFICIENCY
        if activity_string == 'copying':
            return Activity.COPYING

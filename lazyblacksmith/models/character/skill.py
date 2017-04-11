# -*- encoding: utf-8 -*-
from . import db


class Skill(db.Model):
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey('item.id'),
        primary_key=True
    )
    character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        primary_key=True,
    )

    level = db.Column(db.Integer, nullable=False, default=0)

    character = db.relationship(
        'User', backref=db.backref('skills', lazy='dynamic'),
    )
    skill = db.relationship('Item')

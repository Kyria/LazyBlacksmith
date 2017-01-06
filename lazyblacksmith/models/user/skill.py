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
        db.ForeignKey('eve_user.character_id'),
        primary_key=True,
    )

    level = db.Column(db.Integer, nullable=False, default=0)

    character = db.relationship(
        'EveUser',
        remote_side=[character_id],
        backref=db.backref('skills', lazy='dynamic')
    )
    skill = db.relationship(
        'Item',
        remote_side=[skill_id],
    )

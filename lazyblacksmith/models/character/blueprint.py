# -*- encoding: utf-8 -*-
from . import db


class Blueprint(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(
        db.Integer,
        db.ForeignKey('item.id'),
    )
    character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
    )

    # quantity == -1 or > 0 mean original, -2 is copy
    original = db.Column(db.Boolean(), nullable=False, default=True)

    # cumulative number of run between all copies, -1 if original
    total_runs = db.Column(db.Integer, nullable=False, default=-1)

    material_efficiency = db.Column(db.Integer, nullable=False, default=0)
    time_efficiency = db.Column(db.Integer, nullable=False, default=0)

    character = db.relationship(
        'User', backref=db.backref('blueprints', lazy='dynamic'),
    )
    item = db.relationship('Item')

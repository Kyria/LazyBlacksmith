# -*- encoding: utf-8 -*-
from . import db
from .activity import Activity
from flask import url_for


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(100), nullable=True)
    max_production_limit = db.Column(db.Integer, nullable=True)
    market_group_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)

    # calculated field on import
    is_from_manufacturing = db.Column(db.Boolean(), default=True)
    is_from_reaction = db.Column(db.Boolean(), default=True)

    # foreign keys
    activities = db.relationship(
        'Activity',
        backref='blueprint',
        lazy='dynamic'
    )
    activity_products = db.relationship(
        'ActivityProduct',
        backref='blueprint',
        lazy='dynamic',
        foreign_keys='ActivityProduct.item_id'
    )

    activity_skills = db.relationship(
        'ActivitySkill',
        backref='blueprint',
        lazy='dynamic',
        foreign_keys='ActivitySkill.item_id'
    )
    activity_materials = db.relationship(
        'ActivityMaterial',
        backref='blueprint',
        lazy='dynamic',
        foreign_keys='ActivityMaterial.item_id'
    )

    product_for_activities = db.relationship(
        'ActivityProduct',
        backref='product',
        lazy='dynamic',
        foreign_keys='ActivityProduct.product_id'
    )
    skill_for_activities = db.relationship(
        'ActivitySkill',
        backref='skill',
        lazy='dynamic',
        foreign_keys='ActivitySkill.skill_id'
    )
    material_for_activities = db.relationship(
        'ActivityMaterial',
        backref='material',
        lazy='dynamic',
        foreign_keys='ActivityMaterial.material_id'
    )

    # relationship only defined for performance issues
    # ------------------------------------------------
    activity_products__eager = db.relationship(
        'ActivityProduct',
        lazy='joined',
        foreign_keys='ActivityProduct.item_id'
    )

    def icon_32(self):
        static_url = "ccp/Types/%d_32.png" % self.id
        return url_for('static', filename=static_url)

    def icon_64(self):
        static_url = "ccp/Types/%d_64.png" % self.id
        return url_for('static', filename=static_url)

    def is_moon_goo(self):
        return self.market_group_id == 499

    def is_pi(self):
        return self.category_id == 43

    def is_mineral_salvage(self):
        return self.market_group_id in [1857, 1033, 1863]

    def is_ancient_relic(self):
        return self.category_id == 34

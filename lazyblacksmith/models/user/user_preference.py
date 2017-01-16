# -*- encoding: utf-8 -*-
import pytz
import time

from datetime import datetime

from . import db

class UserPreference(db.Model):   
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        primary_key=True
    )
    user = db.relationship('User', backref=db.backref('pref', uselist=False))

    invention_facility = db.Column(db.Integer, nullable=False, default=0)
    invention_invention_rig = db.Column(db.Integer, nullable=False, default=0)
    invention_copy_rig = db.Column(db.Integer, nullable=False, default=0)
    invention_security = db.Column(db.String(1), nullable=False, default='h')
    invention_system = db.Column(
        db.String(100), nullable=False, default='Jita'
    )
    invention_price_region = db.Column(
        db.Integer, nullable=False, default=10000002
    )
    invention_price_type = db.Column(
        db.String(4), nullable=False, default='buy'
    )
    
    research_facility = db.Column(db.Integer, nullable=False, default=0)
    research_me_rig = db.Column(db.Integer, nullable=False, default=0)
    research_te_rig = db.Column(db.Integer, nullable=False, default=0)
    research_copy_rig = db.Column(db.Integer, nullable=False, default=0)
    research_security = db.Column(db.String(1), nullable=False, default='h')
    research_system = db.Column(db.String(100), nullable=False, default='Jita')
    
    prod_facility = db.Column(db.Integer, nullable=False, default=0)
    prod_me_rig = db.Column(db.Integer, nullable=False, default=0)
    prod_te_rig = db.Column(db.Integer, nullable=False, default=0)
    prod_security = db.Column(db.String(1), nullable=False, default='h')
    prod_system = db.Column(db.String(100), nullable=False, default='Jita')
    prod_sub_facility = db.Column(db.Integer, nullable=False, default=0)
    prod_sub_me_rig = db.Column(db.Integer, nullable=False, default=0)
    prod_sub_te_rig = db.Column(db.Integer, nullable=False, default=0)
    prod_sub_security = db.Column(db.String(1), nullable=False, default='h')
    prod_sub_system = db.Column(db.String(100), nullable=False, default='Jita')
    prod_price_region_minerals = db.Column(
        db.Integer, nullable=False, default=10000002
    )
    prod_price_region_pi = db.Column(
        db.Integer, nullable=False, default=10000002
    )
    prod_price_region_moongoo = db.Column(
        db.Integer, nullable=False, default=10000002
    )
    prod_price_region_others = db.Column(
        db.Integer, nullable=False, default=10000002
    )
    
    prod_price_type_minerals = db.Column(
        db.String(4), nullable=False, default='buy'
    )
    prod_price_type_pi = db.Column(
        db.String(4), nullable=False, default='buy'
    )
    prod_price_type_moongoo = db.Column(
        db.String(4), nullable=False, default='buy'
    )
    prod_price_type_others = db.Column(
        db.String(4), nullable=False, default='buy'
    )
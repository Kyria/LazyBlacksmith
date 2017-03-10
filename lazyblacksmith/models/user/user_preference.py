# -*- encoding: utf-8 -*-
from . import db


class UserPreference(db.Model):
    # fake enums
    LABEL_RIGS = ('None', 'T1', 'T2')
    LABEL_SECURITY = {'h': 'High Sec', 'l': 'Low Sec', 'n': 'Null Sec / WH'}
    LABEL_FACILITY = (  # order is important, same as in evedata.js
        'Station', 'Raitaru (M-EC)', 'Azbel (L-EC)',
        'Sotiyo (XL-EC)', 'Other Structures', 'Assembly Array',
        'Thukker Component Array', 'Rapid Assembly Array',
        'Laboratory', 'Hyasyoda Laboratory', 'Experimental Laboratory'
    )
    FACILITY_STRUCTURE = (1, 2, 3, 4)  # Raitaru, Azbel, Sotiyo, Others

    # helpers
    @classmethod
    def label_rig(cls, value):
        try:
            return cls.LABEL_RIGS[value]
        except IndexError:
            return cls.LABEL_RIGS[0]

    @classmethod
    def label_facility(cls, value):
        try:
            return cls.LABEL_FACILITY[value]
        except IndexError:
            return cls.LABEL_FACILITY[0]

    @classmethod
    def label_security(cls, value):
        if value in cls.LABEL_SECURITY:
            return cls.LABEL_SECURITY[value]
        else:
            return cls.LABEL_SECURITY[0]

    @classmethod
    def is_structure(cls, value):
        return value in cls.FACILITY_STRUCTURE

    # model
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        primary_key=True
    )
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref=db.backref('pref', uselist=False)
    )

    # --------------------------------------------------------
    # Invention preferences
    # --------------------------------------------------------
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
    invention_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        nullable=True
    )
    invention_character = db.relationship(
        'User',
        foreign_keys=[invention_character_id]
    )

    # --------------------------------------------------------
    # Research preferences
    # --------------------------------------------------------
    research_facility = db.Column(db.Integer, nullable=False, default=0)
    research_me_rig = db.Column(db.Integer, nullable=False, default=0)
    research_te_rig = db.Column(db.Integer, nullable=False, default=0)
    research_copy_rig = db.Column(db.Integer, nullable=False, default=0)
    research_security = db.Column(db.String(1), nullable=False, default='h')
    research_system = db.Column(db.String(100), nullable=False, default='Jita')
    research_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        nullable=True
    )
    research_character = db.relationship(
        'User',
        foreign_keys=[research_character_id]
    )

    # --------------------------------------------------------
    # Manufacturing preferences
    # --------------------------------------------------------
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
    prod_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        nullable=True
    )
    prod_character = db.relationship(
        'User',
        foreign_keys=[prod_character_id]
    )

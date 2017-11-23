# -*- encoding: utf-8 -*-
from . import db


class UserPreference(db.Model):
    # fake enums
    LABEL_RIGS = ('None', 'T1', 'T2')
    LABEL_SECURITY = {'h': 'High Sec', 'l': 'Low Sec', 'n': 'Null Sec / WH'}
    LABEL_FACILITY = (  # order is important, same as in evedata.js
        'Station', 'Raitaru (M-EC)', 'Azbel (L-EC)',
        'Sotiyo (XL-EC)', 'Other Structures', 'Athanor', 'Tatara'
    )
    FACILITY_STRUCTURE = (1, 2, 3, 4, 5, 6)  # Raitaru, Azbel, Sotiyo, Others
    LABEL_ME_IMPLANT = {
        1.00: 'None',
        0.99: 'MY-701',
        0.97: 'MY-703',
        0.95: 'MY-705'
    }
    LABEL_TE_IMPLANT = {
        1.00: 'None',
        0.99: 'RR-601',
        0.97: 'RR-603',
        0.95: 'RR-605'
    }
    LABEL_COPY_IMPLANT = {
        1.00: 'None',
        0.99: 'SC-801',
        0.97: 'SC-803',
        0.95: 'SC-805'
    }
    LABEL_MANUF_TE_IMPLANT = {
        1.00: 'None',
        0.99: 'BX-801',
        0.98: 'BX-802',
        0.96: 'BX-804'
    }

    # helpers
    @classmethod
    def label_rig(cls, value):
        try:
            return cls.LABEL_RIGS[value]
        except IndexError:
            return cls.LABEL_RIGS[0]

    @classmethod
    def label_implant_me(cls, value):
        try:
            return cls.LABEL_ME_IMPLANT[value]
        except IndexError:
            return cls.LABEL_ME_IMPLANT[1.00]

    @classmethod
    def label_implant_te(cls, value):
        try:
            return cls.LABEL_TE_IMPLANT[value]
        except IndexError:
            return cls.LABEL_TE_IMPLANT[1.00]

    @classmethod
    def label_implant_copy(cls, value):
        try:
            return cls.LABEL_COPY_IMPLANT[value]
        except IndexError:
            return cls.LABEL_COPY_IMPLANT[1.00]

    @classmethod
    def label_implant_manuf_te(cls, value):
        try:
            return cls.LABEL_MANUF_TE_IMPLANT[value]
        except IndexError:
            return cls.LABEL_MANUF_TE_IMPLANT[1.00]

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
    invention_facility = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    invention_invention_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    invention_copy_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    invention_security = db.Column(db.String(1), nullable=False, default='h', server_default='h')
    invention_system = db.Column(
        db.String(100), nullable=False, default='Jita', server_default='Jita'
    )
    invention_price_region = db.Column(
        db.Integer, nullable=False, default=10000002, server_default='10000002'
    )
    invention_price_type = db.Column(
        db.String(4), nullable=False, default='buy', server_default='buy'
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
    invention_copy_implant = db.Column(
        db.Numeric(precision=3, scale=2,
                   decimal_return_scale=2, asdecimal=False),
        nullable=False, server_default='1.00'
    )

    # --------------------------------------------------------
    # Research preferences
    # --------------------------------------------------------
    research_facility = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    research_me_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    research_te_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    research_copy_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    research_security = db.Column(db.String(1), nullable=False, default='h', server_default='h')
    research_system = db.Column(db.String(100), nullable=False, default='Jita', server_default='Jita')
    research_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        nullable=True
    )
    research_character = db.relationship(
        'User',
        foreign_keys=[research_character_id]
    )
    research_me_implant = db.Column(
        db.Numeric(precision=3, scale=2,
                   decimal_return_scale=2, asdecimal=False),
        nullable=False, server_default='1.00'
    )
    research_te_implant = db.Column(
        db.Numeric(precision=3, scale=2,
                   decimal_return_scale=2, asdecimal=False),
        nullable=False, server_default='1.00'
    )
    research_copy_implant = db.Column(
        db.Numeric(precision=3, scale=2,
                   decimal_return_scale=2, asdecimal=False),
        nullable=False, server_default='1.00'
    )

    # --------------------------------------------------------
    # Manufacturing preferences
    # --------------------------------------------------------
    prod_facility = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    prod_me_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    prod_te_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    prod_security = db.Column(db.String(1), nullable=False, default='h', server_default='h')
    prod_system = db.Column(db.String(100), nullable=False, default='Jita', server_default='Jita')
    prod_sub_facility = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    prod_sub_me_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    prod_sub_te_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    prod_sub_security = db.Column(db.String(1), nullable=False, default='h', server_default='h')
    prod_sub_system = db.Column(db.String(100), nullable=False, default='Jita', server_default='Jita')
    prod_price_region_minerals = db.Column(
        db.Integer, nullable=False, default=10000002, server_default='10000002'
    )
    prod_price_region_pi = db.Column(
        db.Integer, nullable=False, default=10000002, server_default='10000002'
    )
    prod_price_region_moongoo = db.Column(
        db.Integer, nullable=False, default=10000002, server_default='10000002'
    )
    prod_price_region_others = db.Column(
        db.Integer, nullable=False, default=10000002, server_default='10000002'
    )

    prod_price_type_minerals = db.Column(
        db.String(4), nullable=False, default='buy', server_default='buy'
    )
    prod_price_type_pi = db.Column(
        db.String(4), nullable=False, default='buy', server_default='buy'
    )
    prod_price_type_moongoo = db.Column(
        db.String(4), nullable=False, default='buy', server_default='buy'
    )
    prod_price_type_others = db.Column(
        db.String(4), nullable=False, default='buy', server_default='buy'
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
    prod_te_implant = db.Column(
        db.Numeric(precision=3, scale=2,
                   decimal_return_scale=2, asdecimal=False),
        nullable=False, server_default='1.00'
    )

    # --------------------------------------------------------
    # Reaction preferences
    # --------------------------------------------------------
    reaction_facility = db.Column(db.Integer, nullable=False, default=5, server_default='5')
    reaction_me_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    reaction_te_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    reaction_security = db.Column(db.String(1), nullable=False, default='l', server_default='l')
    reaction_system = db.Column(db.String(100), nullable=False, default='Rakapas', server_default='Rakapas')
    reaction_manuf_facility = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    reaction_manuf_me_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    reaction_manuf_te_rig = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    reaction_manuf_security = db.Column(db.String(1), nullable=False, default='h', server_default='h')
    reaction_manuf_system = db.Column(db.String(100), nullable=False, default='Jita', server_default='Jita')
    reaction_manuf_te_implant = db.Column(
        db.Numeric(precision=3, scale=2,
                   decimal_return_scale=2, asdecimal=False),
        nullable=False, server_default='1.00'
    )
    reaction_price_regions = db.Column(
        db.Integer, nullable=False, default=10000002, server_default='10000002'
    )
    reaction_price_type = db.Column(
        db.String(4), nullable=False, default='buy', server_default='buy'
    )
    reaction_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        nullable=True
    )
    reaction_character = db.relationship(
        'User',
        foreign_keys=[reaction_character_id]
    )

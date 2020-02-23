# -*- encoding: utf-8 -*-
from . import db
from lazyblacksmith.models.utcdatetime import UTCDateTime

from flask_login import UserMixin
from sqlalchemy import func


class User(db.Model, UserMixin):

    character_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=False
    )
    character_owner_hash = db.Column(db.String(255))
    character_name = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

    is_corp_director = db.Column(db.Boolean, default=False)
    corporation_id = db.Column(db.BigInteger, nullable=True)

    current_login_at = db.Column(
        UTCDateTime(timezone=True),
        server_default=func.now(),
    )

    created_at = db.Column(
        UTCDateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = db.Column(
        UTCDateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # foreign keys
    main_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        nullable=True
    )
    main_character = db.relationship(
        'User',
        remote_side=[character_id],
        backref=db.backref('alts_characters', lazy='dynamic')
    )

    # methods
    def get_portrait_url(self, datasource='tranquility', size=128):
        """returns URL to Character portrait from EVE Image Server"""
        return "{0}/character/{1}/portrait/?size={3}&tenant={4}".format(
            'https://images.evetech.net',
            self.character_id,
            size,
            datasource
        )

    def get_id(self):
        return self.character_id

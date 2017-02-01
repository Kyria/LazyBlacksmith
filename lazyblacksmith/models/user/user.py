# -*- encoding: utf-8 -*-
from . import db
from lazyblacksmith.models.utcdatetime import UTCDateTime

from esipy import EsiClient
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
        return "{0}Character/{1}_{2}.jpg".format(
             EsiClient.__image_server__[datasource],
             self.character_id,
             size
         )

    def get_id(self):
        return self.character_id

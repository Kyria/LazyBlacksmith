# -*- encoding: utf-8 -*-
import pytz
import time

from datetime import datetime

from . import db
from lazyblacksmith.models.utcdatetime import UTCDateTime
from lazyblacksmith.utils.time import utcnow

from esipy import EsiClient
from flask_login import UserMixin
from sqlalchemy import func


class EveUser(db.Model, UserMixin):

    character_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=False
    )
    character_owner_hash = db.Column(db.String(255))
    character_name = db.Column(db.String(200))

    access_token = db.Column(db.String(100))
    access_token_expires = db.Column(UTCDateTime(timezone=True))
    refresh_token = db.Column(db.String(100))
    
    main_character_id = db.Column(
        db.BigInteger,
        db.ForeignKey('eve_user.character_id'),
        nullable=True
    )
    
    alt_characters = db.relationship(
        'EveUser',
        backref='main_character',
        lazy='dynamic',
        foreign_keys='eve_user.main_character_id')

    created_at = db.Column(
        UTCDateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = db.Column(
       UTCDateTime(timezone=True),
       server_default=func.now(),
       onupdate=func.now()
    )

    def get_portrait_url(self, datasource='tranquility', size=128):
        """returns URL to Character portrait from EVE Image Server"""
        return "{0}Character/{1}_{2}.jpg".format(
             EsiClient.__image_server__[datasource],
             self.character_id,
             size
         )

    def get_id(self):
        return self.character_id

    def update_token(self, token_response):
        self.access_token = token_response['access_token']
        self.access_token_expires = datetime.fromtimestamp(
            time.time() + token_response['expires_in'],
            tz=pytz.utc
        )
        self.token_type = token_response['token_type']

        if 'refresh_token' in token_response:
            self.refresh_token = token_response['refresh_token']

    def get_sso_data(self):
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': (
                self.access_token_expires - utcnow()
            ).total_seconds()
        }

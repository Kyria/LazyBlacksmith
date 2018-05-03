# -*- encoding: utf-8 -*-
import pytz
import time

from datetime import datetime

from . import db
from lazyblacksmith.models.utcdatetime import UTCDateTime
from lazyblacksmith.utils.time import utcnow

from sqlalchemy import func


class TokenScope(db.Model):
    # known scopes
    SCOPE_SKILL = 'esi-skills.read_skills.v1'
    SCOPE_CHAR_BLUEPRINTS = 'esi-characters.read_blueprints.v1'
    SCOPE_CORP_BLUEPRINTS = 'esi-characters.read_corporation_roles.v1+esi-corporations.read_blueprints.v1'

    # model
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey('user.character_id'),
        primary_key=True
    )
    user = db.relationship('User', backref=db.backref('tokens'))
    scope = db.Column(db.String(100), primary_key=True)

    access_token = db.Column(db.String(100))
    access_token_expires = db.Column(UTCDateTime(timezone=True))
    refresh_token = db.Column(db.String(100))
    last_update = db.Column(UTCDateTime(timezone=True))
    cached_until = db.Column(UTCDateTime(timezone=True))

    # validity of the token
    valid = db.Column(db.Boolean(), default=True)
    request_try = db.Column(db.Integer(), default=0)

    created_at = db.Column(
        UTCDateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = db.Column(
        UTCDateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

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

    def get_last_update_string(self):
        """ return the utc string date in iso format without ms and TZ info"""
        if self.last_update:
            return self.last_update.replace(
                microsecond=0, tzinfo=None
            ).isoformat(' ')
        else:
            return "Never updated"

    def get_cached_until_string(self):
        """ return the utc string date in iso format without ms and TZ info"""
        if self.cached_until:
            return self.cached_until.replace(
                microsecond=0, tzinfo=None
            ).isoformat(' ')
        else:
            return "Unknown"

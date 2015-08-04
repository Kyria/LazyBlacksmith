# -*- encoding: utf-8 -*-
from flask.ext.login import UserMixin
from sqlalchemy import func
from lazyblacksmith.utils.crestutils import get_crest
from lazyblacksmith.models.utcdatetime import UTCDateTime
from lazyblacksmith.utils.time import utcnow
from . import db


class EveUser(db.Model, UserMixin):
    
    character_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    character_owner_hash = db.Column(db.String(255))
    character_name = db.Column(db.String(200))
    scopes = db.Column(db.String(200))

    token_type = db.Column(db.String(20))
    access_token = db.Column(db.String(100))
    access_token_expires_on = db.Column(UTCDateTime(timezone=True))
    access_token_expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.String(100))

    created_at = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(UTCDateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def get_portrait_url(self, size=128):
        """returns URL to Character portrait from EVE Image Server"""
        return "{0}Character/{1}_{2}.jpg".format(get_crest()._image_server, self.character_id, size)

    def get_id(self):
        return self.character_id

    def get_authed_crest(self):
        return get_crest().temptoken_authorize(
            self.access_token,
            (self.access_token_expires_on - utcnow()).total_seconds(),
            self.refresh_token
        )

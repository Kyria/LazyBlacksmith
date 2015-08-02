# -*- encoding: utf-8 -*-
from . import db
from flask import url_for
from flask.ext.login import UserMixin
from pycrest import EVE
from werkzeug import cached_property


class EveUser(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)

    def is_active(self):
        return self.active

    @cached_property
    def _eve_auth(self):
        """shortcut to python-social-auth's EVE-related extra data for this user"""
        return self.social_auth.get(provider='eveonline').extra_data

    @property
    def character_id(self):
        """get CharacterID from authentification data"""
        return self._eve_auth['id']

    def get_portrait_url(self, size=128):
        """returns URL to Character portrait from EVE Image Server"""
        return "{0}Character/{1}_{2}.jpg".format(EVE._image_server, self.character_id, size)

    def get_crest_tokens(self):
        """get tokens for authenticated CREST"""
        expires_in = time.mktime(
            dateutil.parser.parse(
                self._eve_auth['expires']  # expiration time string
            ).timetuple()                             # expiration timestamp
        ) - time.time()                               # seconds until expiration

        return {
            'access_token': self._eve_auth['access_token'],
            'refresh_token': self._eve_auth['refresh_token'],
            'expires_in': expires_in
        }
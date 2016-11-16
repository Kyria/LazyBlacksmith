# -*- encoding: utf-8 -*-
import datetime
import time

import pytz

from flask import Blueprint
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_oauthlib.client import OAuthException

from lazyblacksmith.extension.oauth import eve_oauth
from lazyblacksmith.models import EveUser
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_crest
from lazyblacksmith.utils.time import utcnow


sso = Blueprint('sso', __name__)


@sso.route('/crest/login')
def crest_login():
    return eve_oauth.authorize(
        callback=url_for(
            'sso.crest_callback',
            _external=True
        ),
    )


@sso.route('/crest/callback')
def crest_callback():
    auth_response = eve_oauth.authorized_response()

    if auth_response is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    if isinstance(auth_response, OAuthException):
        return 'Error while validating your authentification'

    # put in session for tokengetter
    session['access_token'] = auth_response['access_token']
    session['refresh_token'] = auth_response['refresh_token']

    crest_auth = get_crest()
    crest_auth = crest_auth.temptoken_authorize(
        auth_response['access_token'],
        auth_response['expires_in'],
        auth_response['refresh_token']
    )

    character_data = crest_auth.whoami()

    new_user = True
    # save user
    if current_user.is_authenticated:
        # update data
        if current_user.character_id == character_data['CharacterID']:
            update_or_create_eve_user(current_user, auth_response, character_data)
            new_user = False

        else:
            # if we log with another character, logout the current char
            logout_user()

    if new_user:
        eve_user = update_or_create_eve_user(
            EveUser(),
            auth_response,
            character_data,
            True
        )

        login_user(eve_user)

    # delete session data
    del session['access_token']
    del session['refresh_token']

    # redirect
    return redirect(url_for("home.index"))


def update_or_create_eve_user(eve_user, auth_response, character_data, create=False):
    """ create or update an "eve_user" with sso informations """

    # need to check if already exists first ! :)
    tmp_user = EveUser.query.get(character_data['CharacterID'])
    if tmp_user is not None:
        create = False
        eve_user = tmp_user

    eve_user.character_owner_hash = character_data['CharacterOwnerHash']
    eve_user.character_name = character_data['CharacterName']
    eve_user.scopes = character_data['Scopes']
    eve_user.token_type = character_data['TokenType']

    eve_user.refresh_token = auth_response['refresh_token']
    eve_user.access_token = auth_response['access_token']
    eve_user.access_token_expires_on = utcnow() + datetime.timedelta(seconds=int(auth_response['expires_in']) - 60)
    eve_user.access_token_expires_in = auth_response['expires_in']

    if create:
        eve_user.character_id = character_data['CharacterID']
        db.session.add(eve_user)
    db.session.commit()

    return eve_user


@sso.route('/logout')
@login_required
def crest_logout():
    logout_user()
    return redirect(url_for("home.index"))


@eve_oauth.tokengetter
def eve_oauth_tokengetter(token=None):
    if 'access_token' in session:
        return (session['access_token'],)
    elif current_user.is_authenticated:
        expires_at = current_user.access_token_expires_at
        if expires_at is None or (expires_at - utcnow()).total_seconds() <= 60:
            authed_crest = current_user.get_authed_crest()
            authed_crest.refr_authorize(current_user.refresh_token)

            current_user.access_token = authed_crest.token
            current_user.access_token_expires_in = authed_crest.expires - time.time()
            current_user.access_token_expires_on = datetime.fromtimestamp(authed_crest.expires,
                                                                          tz=pytz.utc)
            db.session.commit()

        return (current_user.access_token,)
    return None

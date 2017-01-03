# -*- encoding: utf-8 -*-
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

from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.extension.oauth import eve_oauth
from lazyblacksmith.models import EveUser
from lazyblacksmith.models import db


sso = Blueprint('sso', __name__)


@sso.route('/login')
def login():
    return eve_oauth.authorize(
        callback=url_for(
            'sso.callback',
            _external=True
        ),
    )


@sso.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.index"))


@sso.route('/callback')
def callback():
    auth_response = eve_oauth.authorized_response()

    if auth_response is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ), 403

    if isinstance(auth_response, OAuthException):
        return 'Error while validating your authentification', 403

    # put in session for tokengetter
    session['access_token'] = auth_response['access_token']
    session['refresh_token'] = auth_response['refresh_token']

    esisecurity.update_token(auth_response)
    cdata = esisecurity.verify()

    new_user = True
    # save user
    if current_user.is_authenticated:
        # update data
        if (current_user.character_id == cdata['CharacterID'] and
           current_user.character_owner_hash == cdata['CharacterOwnerHash']):
            update_or_create_eve_user(
                current_user,
                auth_response,
                cdata
            )
            new_user = False

        else:
            # if we log with another character, logout the current char
            logout_user()

    if new_user:
        eve_user = update_or_create_eve_user(
            EveUser(),
            auth_response,
            cdata,
            True
        )

        login_user(eve_user)

    # delete session data
    del session['access_token']
    del session['refresh_token']

    # redirect
    return redirect(url_for("home.index"))


def update_or_create_eve_user(eve_user,
                              auth_response,
                              character_data,
                              create=False):
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

    eve_user.update_token(auth_response)

    if create:
        eve_user.character_id = character_data['CharacterID']
        db.session.add(eve_user)
    db.session.commit()

    return eve_user


@eve_oauth.tokengetter
def eve_oauth_tokengetter(token=None):
    if 'access_token' in session:
        return (session['access_token'],)
    elif current_user.is_authenticated:
        esisecurity.update_token(current_user.get_sso_data())
        if esisecurity.is_token_expired(offset=60):
            token_response = esisecurity.refresh()
            current_user.update_token(token_response)
            db.session.commit()
        return (current_user.access_token,)
    return None

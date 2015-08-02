# -*- encoding: utf-8 -*-
from flask import Blueprint, redirect, session, url_for, request, jsonify
from flask_oauthlib.client import OAuthException

from lazyblacksmith.oauth import eve_oauth
from lazyblacksmith.utils.crestutils import get_crest

from flask.ext.login import current_user, login_user, logout_user
from lazyblacksmith.utils.time import utcnow
import time

sso = Blueprint('sso', __name__)

@sso.route('/crest/login')
def crest_login():
    return eve_oauth.authorize(
        callback = url_for(
            'sso.crest_callback',
            _external = True
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
    crest_auth = crest_auth.temptoken_authorize(auth_response['access_token'], auth_response['expires_in'], auth_response['refresh_token'])

    # save user
    if current_user.is_authenticated():
        # update data
        pass

    else:
        pass

    # login_user(eve_user)

    # delete session data

    # redirect
    return jsonify(crest_auth.whoami())


@sso.route('/logout')
def crest_logout():
    logout_user()
    return redirect(url_for("home.index"))

@eve_oauth.tokengetter
def eve_oauth_tokengetter(token=None):
    if 'access_token' in session:
        return (session['access_token'],)
    elif current_user.is_authenticated():
        expires_at = current_user.access_token_expires_at
        if expires_at is None or (expires_at - utcnow()).total_seconds() <= 60:
            authed_crest = current_user.get_authed_crest()
            authed_crest.refresh()

            current_user.access_token = authed_crest.token
            current_user.access_token_expires_in = authed_crest.expires - time.time()
            current_user.access_token_expires_on = datetime.fromtimestamp(authed_crest.expires, tz = pytz.utc)

        return (current_user.access_token,)
    return None
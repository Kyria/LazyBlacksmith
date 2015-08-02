# -*- encoding: utf-8 -*-
from flask import Blueprint, redirect, session, url_for, request, jsonify
from flask_oauthlib.client import OAuthException

from lazyblacksmith.oauth import eve_oauth
from lazyblacksmith.utils.crestutils import get_crest


sso = Blueprint('sso', __name__)

@sso.route('/crest/login')
def crest_login():
    return eve_oauth.authorize(
        callback = url_for(
            'sso.crest_callback',
            next = request.args.get('next') or request.referrer or None,
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



    crest_auth = get_crest()
    crest_auth = crest_auth.temptoken_authorize(auth_response['access_token'], auth_response['expires_in'], auth_response['refresh_token'])

    # save user
    # redirect

    return jsonify(crest_auth.whoami())


@sso.route('/logout')
def crest_logout():
    session.clear()
    return redirect(url_for("home.index"))

@eve_oauth.tokengetter
def get_eve_oauth_access_token(token='access'):
    print "get_eve_oauth_access_token !!!!!!!!"
    return None
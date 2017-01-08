# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user
from flask_oauthlib.client import OAuthException

from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.extension.oauth import eve_oauth
from lazyblacksmith.models import db
from lazyblacksmith.utils.login import check_login_user

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

    esisecurity.update_token(auth_response)
    cdata = esisecurity.verify()

    if current_user.is_authenticated:
        check_login_user(cdata, auth_response, current_user)
    else:
        check_login_user(cdata, auth_response)

    # redirect
    return redirect(url_for("home.index"))


@eve_oauth.tokengetter
def eve_oauth_tokengetter(token=None):
    if current_user.is_authenticated:
        esisecurity.update_token(current_user.get_sso_data())
        if esisecurity.is_token_expired(offset=60):
            token_response = esisecurity.refresh()
            current_user.update_token(token_response)
            db.session.commit()
        return (current_user.access_token,)
    return None

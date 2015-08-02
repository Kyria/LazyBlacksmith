# -*- encoding: utf-8 -*-
from flask import abort
from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import session
from flask import url_for

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
    crest_auth = eve_oauth.authorized_response()

    if crest_auth is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )

    session['access_token'] = crest_auth['access_token']
    session['refresh_token'] = crest_auth['refresh_token']



@sso.route('/logout')
def crest_logout():
    session.clear()
    return redirect(url_for("home.index"))

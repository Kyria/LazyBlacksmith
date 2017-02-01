# -*- encoding: utf-8 -*-
from esipy.exceptions import APIException
from flask import Blueprint
from flask import redirect
from flask import request
from flask import url_for
from flask import flash
from urlparse import urlparse
from urlparse import urljoin
from flask_login import current_user
from flask_login import login_required
from flask_login import logout_user

from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.models import db
from lazyblacksmith.utils.sso import add_scopes
from lazyblacksmith.utils.sso import build_state_token
from lazyblacksmith.utils.sso import extract_state_token
from lazyblacksmith.utils.sso import safe_redirect
from lazyblacksmith.utils.sso import get_redirect_target
from lazyblacksmith.utils.sso import check_login_user

sso = Blueprint('sso', __name__)


@sso.route('/login/', defaults={'scopes': ""})
@sso.route('/login/<scopes>')
def login(scopes):
    scope_list = scopes.split(',')
    state=build_state_token(
        redirect=get_redirect_target(),
        scopes=scope_list
    )
    return redirect(esisecurity.get_auth_uri(
        scopes=scope_list,
        state=state,
    ))


@sso.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", 'info')
    return redirect(url_for("home.index"))


@sso.route('/callback')
def callback():
    redirect, scopes = extract_state_token(request.args.get('state'))
    code = request.args.get('code')
    
    try:
        auth_response = esisecurity.auth(code)
    except APIException as e:
        return 'Login EVE Online SSO failed: %s' % e, 403
    
    cdata = esisecurity.verify()
    if current_user.is_authenticated:
        add_scopes(cdata, auth_response, scopes, current_user)
    else:
        check_login_user(cdata, auth_response)

    return safe_redirect(redirect)


# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from flask import flash
from flask import json
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask_login import login_user
from flask_login import logout_user
from requests.utils import quote
from requests.utils import unquote
from sqlalchemy.orm.exc import NoResultFound
from urlparse import urljoin
from urlparse import urlparse

from lazyblacksmith.models import Skill
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User
from lazyblacksmith.models import UserPreference
from lazyblacksmith.models import db

from . import logger

import base64
import config
import hashlib
import random
import hmac


def check_get_user(id, owner_hash, in_login=False):
    """ Check if a user exists and return it.

    If the user exists, we return it.
    If the user exists but with another owner hash, we delete it first
    If the user does not exist, return a new user object
    """
    try:
        user = User.query.filter(
            User.character_id == id,
            User.character_owner_hash == owner_hash
        ).one()

    except NoResultFound:
        # if none is found, try to find just with characterID
        try:
            user = User.query.filter(
                User.character_id == id,
            ).one()
            # if no exception is triggered, it mean we have a registered charID
            # but with another account: owner has changed, we'll wipe all data.
            wipe_character_data(user)
            if in_login:
                logout_user()

        except NoResultFound:
            logger.info("Unknown charID %s. Let's create a new user." % id)

        finally:
            user = User()
            user.character_id = id
    return user


def login_user_oauth(cdata, auth_response):
    """ Login the user and update his data """
    user = check_get_user(
        cdata['CharacterID'],
        cdata['CharacterOwnerHash'],
        True
    )
    user.character_owner_hash = cdata['CharacterOwnerHash']
    user.character_name = cdata['CharacterName']

    try:
        db.session.merge(user)
        db.session.commit()

        if not user.pref and not user.main_character:
            prefs = UserPreference()
            prefs.user = user
            db.session.merge(prefs)
            db.session.commit()

        login_user(user)
        session.permanent = True
        flash('You have successfully logged in.', 'success')

    except:
        logger.exception("Cannot login the user - uid: %d" % user.character_id)
        db.session.rollback()
        logout_user()
        flash('Something went wrong. Please try to login again', 'error')


def add_scopes(cdata, auth_response, scopes, current_user):
    """ Add a new scope to a logged user """
    # get or create the character
    user = check_get_user(
        cdata['CharacterID'],
        cdata['CharacterOwnerHash'],
    )
    user.character_owner_hash = cdata['CharacterOwnerHash']
    user.character_name = cdata['CharacterName']

    # if it's a new, let's federate him with the main one
    if current_user.character_id != user.character_id:
        user.main_character = current_user

    for scope in scopes:
        token_scope = TokenScope(
            user_id=user.character_id,
            scope=scope,
        )
        token_scope.update_token(auth_response)
        db.session.merge(token_scope)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    flash('You have successfully added new scopes')


def wipe_character_data(user):
    """ Remove the data from the database of a given user """
    # remove preferences
    UserPreference.query.filter(
        UserPreference.user_id == user.character_id
    ).delete()

    # remove scopes
    TokenScope.query.filter(
        TokenScope.user_id == user.character_id
    ).delete()

    # remove skills
    Skill.query.filter(Skill.character_id == user.character_id).delete()

    # remove user
    User.query.filter_by(character_id=user.character_id).delete()

    # commit
    db.session.commit()


def is_safe_url(target):
    """ check if the target url is safe (same host) """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https')
            and ref_url.netloc == test_url.netloc)


def get_redirect_target():
    """ return the redirect target (next param or referrer) """
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
    return None


def safe_redirect(target, endpoint="home.index"):
    """ redirect to target if safe, else redirect to endpoint """
    if not target or not is_safe_url(target):
        target = url_for(endpoint)
    return redirect(target)


def build_state_token(**kwargs):
    """ Build the authorization state token with some data """
    redirect_uri = kwargs.pop('redirect', 'home.index')
    scopes = kwargs.pop('scopes', [])
    token = generate_token()
    session['token'] = token

    json_string = json.dumps({
        'redirect': redirect_uri,
        'scopes': scopes,
        'token': token,
    })
    b64_json = base64.urlsafe_b64encode(json_string)
    return quote(b64_json)


def extract_state_token(token_string):
    """ Extract the data from a state token string """
    b64_json = str(unquote(token_string))
    json_string = base64.urlsafe_b64decode(b64_json)
    json_state = json.loads(json_string)

    redirect = json_state.get('redirect', 'home.index')
    scopes = json_state.get('scopes', [])
    token = json_state.get('token', None)

    return redirect, scopes, token


def generate_token():
    """Generates a non-guessable OAuth token """
    chars = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    rand = random.SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(40))
    return hmac.new(config.SECRET_KEY, random_string, hashlib.sha256).hexdigest()

# -*- encoding: utf-8 -*-
""" Utils with shortcuts for common models query """
from datetime import datetime
from email.utils import parsedate

import pytz
from esipy.exceptions import APIException
from sqlalchemy.exc import SQLAlchemyError

import config
from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.models import Region, TokenScope, db
from lazyblacksmith.utils.time import utcnow

from . import logger


def get_regions(is_wh=False):
    """ return the list of regions """
    return Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).filter_by(
        wh=is_wh
    )


def inc_fail_token_scope(token, status_code):
    """ Check if status_code is 4xx, increase counter, check validity
    """
    if (400 <= int(status_code) <= 499):
        token.request_try += 1
        token.valid = (token.request_try <= 3)
        try:
            db.session.commit()
        except SQLAlchemyError:
            logger.exception(
                'Something went wrong while updating token validity'
            )
            db.session.rollback()


def get_token_update_esipy(character_id, scope):
    """ get token, update it and return everything
    Get the token using what have been given in parameter
    then try to update esisecurity, verify the token is
    up to date and catch any APIException while updating
    it to be able to invalidate wrong tokens.
    """
    token = TokenScope.query.filter(
        TokenScope.user_id == character_id,
        TokenScope.scope == scope
    ).one()
    esisecurity.update_token(token.get_sso_data())

    if esisecurity.is_token_expired():
        try:
            token.update_token(esisecurity.refresh())
            db.session.commit()
        except APIException as e:
            inc_fail_token_scope(token, e.status_code)
            raise

    return token


def update_token_state(token, expires_header):
    """ update the token """
    token.request_try = 0
    token.last_update = utcnow()
    token.cached_until = datetime(
        *parsedate(expires_header)[:6]
    ).replace(tzinfo=pytz.utc)
    db.session.commit()

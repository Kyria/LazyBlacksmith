# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import db

import pytz
import time


def token_update_observer(access_token, refresh_token, expires_in, token_type):
    TokenScope.query.filter_by(
        refresh_token=refresh_token
    ).update({
        'access_token': access_token,
        'access_token_expires': datetime.fromtimestamp(
            time.time() + expires_in,
            tz=pytz.utc
        )
    })

    # force commit
    try:
        db.session.commit()
    except:
        db.session.rollback()

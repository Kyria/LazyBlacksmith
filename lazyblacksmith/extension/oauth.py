# -*- encoding: utf-8 -*-
from flask_oauthlib.client import OAuth

from lazyblacksmith.extension.esipy import esisecurity

import config

oauth = OAuth()

eve_oauth = oauth.remote_app(
    'lb_eve_sso',
    base_url='ESI',
    access_token_url='/token/',
    authorize_url='/authorize/',
    access_token_method='POST',
    request_token_method='GET',
    consumer_key=config.ESI_CLIENT_ID,
    consumer_secret=config.ESI_SECRET_KEY,
    request_token_params={
        'state': lambda: security.gen_salt(10)
    }
)

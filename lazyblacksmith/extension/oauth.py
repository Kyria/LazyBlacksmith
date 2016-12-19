# -*- encoding: utf-8 -*-
from flask_oauthlib.client import OAuth

import config


oauth = OAuth()

eve_oauth = oauth.remote_app(
    'lb_eve_sso',
    base_url='crest',
    access_token_url='/token/',
    authorize_url='/authorize/',
    access_token_method='POST',
    request_token_method='GET',
    request_token_params={'scope': config.ESI_SCOPE},
    consumer_key=config.ESI_CLIENT_ID,
    consumer_secret=config.ESI_SECRET_KEY,
)

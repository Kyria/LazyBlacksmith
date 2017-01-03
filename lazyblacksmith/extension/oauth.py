# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.esipy import esisecurity

from flask_oauthlib.client import OAuth
from six.moves.urllib.parse import urlparse
from werkzeug import security

import config

parsed_uri = urlparse(esisecurity.oauth_token)

oauth = OAuth()
eve_oauth = oauth.remote_app(
    'lb_eve_sso',
    access_token_url=esisecurity.oauth_token,
    authorize_url='%s://%s/oauth/authorize' % (
        parsed_uri.scheme,
        parsed_uri.netloc
    ),
    access_token_method='POST',
    request_token_method='GET',
    consumer_key=config.ESI_CLIENT_ID,
    consumer_secret=config.ESI_SECRET_KEY,
    request_token_params={
        'state': lambda: security.gen_salt(10),
        'scope': config.ESI_SCOPE,
    }
)

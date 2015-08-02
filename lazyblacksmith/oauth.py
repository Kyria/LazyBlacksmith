from flask_oauthlib.client import OAuth
from lazyblacksmith.utils.crestutils import get_crest
import config

oauth = OAuth()
crest = get_crest()

eve_oauth = oauth.remote_app(
    'lb_eve_sso',
    base_url = 'crest',
    access_token_url = '%s/token/' % crest._oauth_endpoint,
    authorize_url = '%s/authorize/' % crest._oauth_endpoint,
    access_token_method = 'POST',
    request_token_method = 'GET',
    request_token_params = {'scope': config.CREST_SCOPE}
)
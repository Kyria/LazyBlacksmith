# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.events import AFTER_TOKEN_REFRESH
from requests.adapters import HTTPAdapter

import config
from lazyblacksmith.extension.cache import LBCACHE
from .esipy_observers import token_update_observer


TRANSPORT_ADAPTER = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=300,
)

# ESI objects to be imported
esiapp = EsiApp(
    cache=LBCACHE,
    cache_time=21600,
    datasource=config.ESI_DATASOURCE
)

esisecurity = EsiSecurity(
    app=esiapp.get_latest_swagger,
    redirect_uri="%s%s" % (
        config.ESI_REDIRECT_DOMAIN, '/sso/callback',
    ),
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.ESI_SECRET_KEY,
    headers={'User-Agent': config.ESI_USER_AGENT}
)
esiclient = EsiClient(
    security=esisecurity,
    transport_adapter=TRANSPORT_ADAPTER,
    cache=LBCACHE,
    headers={'User-Agent': config.ESI_USER_AGENT},
    retry_requests=True
)
esiclient_nocache = EsiClient(
    security=esisecurity,
    transport_adapter=TRANSPORT_ADAPTER,
    cache=None,
    headers={'User-Agent': config.ESI_USER_AGENT},
    retry_requests=True
)

# register observers
AFTER_TOKEN_REFRESH.add_receiver(token_update_observer)

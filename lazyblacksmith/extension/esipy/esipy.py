# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import config

from esipy import App
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.cache import BaseCache
from lazyblacksmith.extension.cache import cache

from requests.adapters import HTTPAdapter


class LbCache(BaseCache):
    """ Custom BaseCache implementation for Lazyblacksmith
        used in esipy, to use the flask cache
    """
    def set(self, key, value, timeout=300):
        cache.set(key, value, timeout)

    def get(self, key, default=None):
        cached = cache.get(key)
        return cached if cached is not None else default

    def invalidate(self, key):
        cache.delete(key)


transport_adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=300,
)

# ESI objects to be imported
esiapp = App.create(config.ESI_SWAGGER_JSON)
esisecurity = EsiSecurity(
    app=esiapp,
    redirect_uri="%s%s" % (
        config.ESI_REDIRECT_DOMAIN, '/sso/crest/callback'
    ),
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.ESI_SECRET_KEY,
)
esiclient = EsiClient(
    security=esisecurity,
    transport_adapter=transport_adapter,
    cache=LbCache(),
    headers={'User-Agent': config.ESI_USER_AGENT}
)

import base64
import requests
import time
from pycrest import version
from pycrest.compat import bytes_, text_
from pycrest.errors import APIException, UnsupportedHTTPMethodException
from requests.adapters import HTTPAdapter
try:
    from urllib.parse import urlparse, urlunparse, parse_qsl
except ImportError:  # pragma: no cover
    from urlparse import urlparse, urlunparse, parse_qsl

try:
    from urllib.parse import quote
except ImportError:  # pragma: no cover
    from urllib import quote
import logging
import re
from pycrest.cache import DictCache, APICache, DummyCache

logger = logging.getLogger("pycrest.eve")
cache_re = re.compile(r'max-age=([0-9]+)')


class APIConnection(object):

    def __init__(
            self,
            additional_headers=None,
            user_agent=None,
            transport_adapter=None,
            **kwargs):
        '''Initialises a PyCrest object

        Keyword arguments:
        additional_headers - a list of http headers that will be sent to the server
        user_agent - a custom user agent
        cache - an instance of an APICache object that will cache HTTP Requests.
                Default is DictCache, pass cache=None to disable caching.
        '''
        # Set up a Requests Session
        session = requests.Session()
        if additional_headers is None:
            additional_headers = {}
        if user_agent is None:
            user_agent = "PyCrest/{0} +https://github.com/pycrest/PyCrest"\
                .format(version)
        if isinstance(transport_adapter, HTTPAdapter):
            session.mount('http://', transport_adapter)
            session.mount('https://', transport_adapter)

        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })
        session.headers.update(additional_headers)
        self._session = session
        if 'cache' not in kwargs:
            self.cache = DictCache()
        else:
            cache = kwargs.pop('cache')
            if isinstance(cache, APICache):
                self.cache = cache
            elif cache is None:
                self.cache = DummyCache()
            else:
                raise ValueError('Provided cache must implement APICache')

    def _parse_parameters(self, resource, params):
        '''Creates a dictionary from query_string and `params`

        Transforms the `?key=value&...` to a {'key': 'value'} and adds
        (or overwrites if already present) the value with the dictionary in
        `params`.
        '''
        # remove params from resource URI (needed for paginated stuff)
        parsed_uri = urlparse(resource)
        qs = parsed_uri.query
        resource = urlunparse(parsed_uri._replace(query=''))
        prms = {}
        for tup in parse_qsl(qs):
            prms[tup[0]] = tup[1]

        # params supplied to self.get() override parsed params
        for key in params:
            prms[key] = params[key]
        return resource, prms

    def get(self, resource, params={}, caching=True):
        logger.debug('Getting resource %s', resource)
        resource, prms = self._parse_parameters(resource, params)

        # check cache
        key = (
            resource, frozenset(
                self._session.headers.items()), frozenset(
                prms.items()))
        cached = self.cache.get(key)
        if cached and cached['expires'] > time.time():
            logger.debug(
                'Cache hit for resource %s (params=%s)',
                resource,
                prms)
            return cached['payload']
        elif cached:
            logger.debug(
                'Cache stale for resource %s (params=%s)',
                resource,
                prms)
            self.cache.invalidate(key)
        else:
            logger.debug(
                'Cache miss for resource %s (params=%s', resource, prms)

        logger.debug('Getting resource %s (params=%s)', resource, prms)
        res = self._session.get(resource, params=prms)

        if res.status_code != 200:
            raise APIException(
                resource,
                res.status_code,
                res.json()
                )

        ret = res.json()

        # cache result only if caching = True (default)
        key = (
            resource, frozenset(
                self._session.headers.items()), frozenset(
                prms.items()))

        expires = self._get_expires(res)
        if expires > 0 and caching:
            self.cache.put(
                key, {
                    'expires': time.time() + expires, 'payload': ret})

        return ret

    # post is not idempotent so there should be no caching
    def post(self, resource, data={}):
        logger.debug('Posting resource %s (data=%s)', resource, data)
        res = self._session.post(resource, data=data)
        if res.status_code not in [200, 201]:
            raise APIException(
                resource,
                res.status_code,
                res.json()
                )

        return {}

    # put is not idempotent so there should be no caching
    def put(self, resource, data={}):
        logger.debug('Putting resource %s (data=%s)', resource, data)
        res = self._session.put(resource, data=data)
        if res.status_code != 200:
            raise APIException(
                resource,
                res.status_code,
                res.json()
                )

        return {}

    # delete is not idempotent so there should be no caching
    def delete(self, resource):
        logger.debug('Deleting resource %s', resource)
        res = self._session.delete(resource)
        if res.status_code != 200:
            raise APIException(
                resource,
                res.status_code,
                res.json()
                )

        return {}

    def _get_expires(self, response):
        if 'Cache-Control' not in response.headers:
            return 0
        if any([s in response.headers['Cache-Control']
                for s in ['no-cache', 'no-store']]):
            return 0
        match = cache_re.search(response.headers['Cache-Control'])
        if match:
            return int(match.group(1))
        return 0


class EVE(APIConnection):

    def __init__(self, **kwargs):
        self.api_key = kwargs.pop('api_key', None)
        self.client_id = kwargs.pop('client_id', None)
        self.redirect_uri = kwargs.pop('redirect_uri', None)
        if kwargs.pop('testing', False):
            self._endpoint = "https://api-sisi.testeveonline.com/"
            self._image_server = "https://image.testeveonline.com/"
            self._oauth_endpoint = "https://sisilogin.testeveonline.com/oauth"
        else:
            self._endpoint = "https://crest-tq.eveonline.com/"
            self._image_server = "https://imageserver.eveonline.com/"
            self._oauth_endpoint = "https://login.eveonline.com/oauth"
        self._cache = {}
        self._data = None
        APIConnection.__init__(self, **kwargs)

    def __call__(self, caching=True):
        if not self._data:
            self._data = APIObject(self.get(self._endpoint,
                                            caching=caching),
                                   self)
        return self._data

    def __getattr__(self, item):
        return self._data.__getattr__(item)

    def auth_uri(self, scopes=None, state=None):
        s = [] if not scopes else scopes
        return "%s/authorize?response_type=code&redirect_uri=%s&client_id=%s%s%s" % (
            self._oauth_endpoint,
            quote(self.redirect_uri, safe=''),
            self.client_id,
            "&scope=%s" % '+'.join(s) if scopes else '',
            "&state=%s" % state if state else ''
        )

    def _authorize(self, params):
        auth = text_(
            base64.b64encode(
                bytes_(
                    "%s:%s" %
                    (self.client_id, self.api_key))))
        headers = {"Authorization": "Basic %s" % auth}
        resource = "%s/token" % self._oauth_endpoint
        res = self._session.post(
            resource,
            params=params,
            headers=headers)
        if res.status_code != 200:
            raise APIException(
                        resource,
                        res.status_code,
                        res.json()
                        )

        return res.json()

    def authorize(self, code):
        res = self._authorize(
            params={
                "grant_type": "authorization_code",
                "code": code})
        return AuthedConnection(res,
                                self._endpoint,
                                self._oauth_endpoint,
                                self.client_id,
                                self.api_key,
                                cache=self.cache)

    def refr_authorize(self, refresh_token):
        res = self._authorize(
            params={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token})
        return AuthedConnection({'access_token': res['access_token'],
                                 'refresh_token': refresh_token,
                                 'expires_in': res['expires_in']},
                                self._endpoint,
                                self._oauth_endpoint,
                                self.client_id,
                                self.api_key,
                                cache=self.cache)

    def temptoken_authorize(self, access_token, expires_in, refresh_token):
        return AuthedConnection({'access_token': access_token,
                                 'refresh_token': refresh_token,
                                 'expires_in': expires_in},
                                self._endpoint,
                                self._oauth_endpoint,
                                self.client_id,
                                self.api_key,
                                cache=self.cache)


class AuthedConnection(EVE):

    def __init__(
            self,
            res,
            endpoint,
            oauth_endpoint,
            client_id=None,
            api_key=None,
            **kwargs):
        EVE.__init__(self, **kwargs)
        self.client_id = client_id
        self.api_key = api_key
        self.token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expires = int(time.time()) + res['expires_in']
        self._oauth_endpoint = oauth_endpoint
        self._endpoint = endpoint
        self._session.headers.update(
            {"Authorization": "Bearer %s" % self.token})

    def __call__(self, caching=True):
        if not self._data:
            self._data = APIObject(self.get(self._endpoint, caching=caching), self)
        return self._data

    def whoami(self):
        if 'whoami' not in self._cache:
            self._cache['whoami'] = self.get(
                "%s/verify" %
                self._oauth_endpoint)
        return self._cache['whoami']

    def refresh(self):
        res = self._authorize(
            params={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token})
        self.token = res['access_token']
        self.expires = int(time.time()) + res['expires_in']
        self._session.headers.update(
            {"Authorization": "Bearer %s" % self.token})
        return self  # for backwards compatibility

    def get(self, resource, params={}, caching=True):
        if int(time.time()) >= self.expires:
            self.refresh()
        return super(self.__class__, self).get(resource, params, caching)


class APIObject(object):

    def __init__(self, parent, connection):
        self._dict = {}
        self.connection = connection
        for k, v in parent.items():
            if isinstance(v, dict):
                self._dict[k] = APIObject(v, connection)
            elif isinstance(v, list):
                self._dict[k] = self._wrap_list(v)
            else:
                self._dict[k] = v

    def _wrap_list(self, list_):
        new = []
        for item in list_:
            if isinstance(item, dict):
                new.append(APIObject(item, self.connection))
            elif isinstance(item, list):
                new.append(self._wrap_list(item))
            else:
                new.append(item)
        return new

    def __getattr__(self, item):
        if item in self._dict:
            return self._dict[item]
        raise AttributeError(item)

    def __call__(self, **kwargs):
        """carries out a CREST request

        __call__ takes two keyword parameters: method and data

        method contains the http request method and defaults to 'get'
            but could also be 'post', 'put', or 'delete'

        data contains any arguments that will be passed with the request -
            it could be a dictionary which contains parameters
            and is passed via the url for 'get' requests and as form-encoded
            data for 'post' or 'put' requests. It could also be a string if
            another format of data (e.g. via json.dumps()) must be passed in
            a 'post' or 'put' request. This parameter has no effect on
            'delete' requests.
        """

        # Caching is now handled by APIConnection
        if 'href' in self._dict:
            method = kwargs.pop('method', 'get')    # default to get: historic behaviour
            data = kwargs.pop('data', {})
            caching = kwargs.pop('caching', True)   # default caching to true, for get requests

            # retain compatibility with historic method of passing parameters.
            # Slightly unsatisfactory - what if data is dict-like but not a dict?
            if isinstance(data, dict):
                for arg in kwargs:
                    data[arg] = kwargs[arg]

            if method == 'post':
                return APIObject(self.connection.post(self._dict['href'], data=data), self.connection)
            elif method == 'put':
                return APIObject(self.connection.put(self._dict['href'], data=data), self.connection)
            elif method == 'delete':
                return APIObject(self.connection.delete(self._dict['href']), self.connection)
            elif method == 'get':
                return APIObject(self.connection.get(self._dict['href'],
                                                     params=data,
                                                     caching=caching),
                                 self.connection)
            else:
                raise UnsupportedHTTPMethodException(method)
        else:
            return self

    def __str__(self):  # pragma: no cover
        return self._dict.__str__()

    def __repr__(self):  # pragma: no cover
        return self._dict.__repr__()

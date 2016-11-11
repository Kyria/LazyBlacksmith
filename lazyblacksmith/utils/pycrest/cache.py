import hashlib
import zlib
import os

try:
    import pickle
except ImportError:  # pragma: no cover
    import cPickle as pickle

import logging
logger = logging.getLogger("pycrest.cache")


class APICache(object):

    def put(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def invalidate(self, key):
        raise NotImplementedError

    def _hash(self, data):
        h = hashlib.new('md5')
        h.update(pickle.dumps(data))
        # prefix allows possibility of multiple applications
        # sharing same keyspace
        return 'pyc_' + h.hexdigest()


class FileCache(APICache):

    def __init__(self, path):
        self._cache = {}
        self.path = path
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0o700)

    def _getpath(self, key):
        return os.path.join(self.path, self._hash(key) + '.cache')

    def put(self, key, value):
        with open(self._getpath(key), 'wb') as f:
            f.write(
                zlib.compress(
                    pickle.dumps(value,
                                 pickle.HIGHEST_PROTOCOL)))
        self._cache[key] = value

    def get(self, key):
        if key in self._cache:
            return self._cache[key]

        try:
            with open(self._getpath(key), 'rb') as f:
                return pickle.loads(zlib.decompress(f.read()))
        except IOError as ex:
            logger.debug('IOError: {0}'.format(ex))
            if ex.errno == 2:  # file does not exist (yet)
                return None
            else:   # pragma: no cover
                raise

    def invalidate(self, key):
        self._cache.pop(key, None)

        try:
            os.unlink(self._getpath(key))
        except OSError as ex:
            if ex.errno == 2:  # does not exist
                pass
            else:   # pragma: no cover
                raise


class DictCache(APICache):

    def __init__(self):
        self._dict = {}

    def get(self, key):
        return self._dict.get(key, None)

    def put(self, key, value):
        self._dict[key] = value

    def invalidate(self, key):
        self._dict.pop(key, None)


class DummyCache(APICache):
    """ Provide a fake cache class to allow a "no cache"
        use without breaking everything within APIConnection """
    def __init__(self):
        self._dict = {}

    def get(self, key):
        return None

    def put(self, key, value):
        pass

    def invalidate(self, key):
        pass


class MemcachedCache(APICache):

    def __init__(self, server_list):
        """ server_list is a list of memcached servers to connect to,
        for example ['127.0.0.1:11211'].
        """
        # import memcache here so that the dependency on the python-memcached
        # only occurs if you use it
        import memcache
        self._mc = memcache.Client(server_list, debug=0)

    def get(self, key):
        return self._mc.get(self._hash(key))

    def put(self, key, value):
        return self._mc.set(self._hash(key), value)

    def invalidate(self, key):
        return self._mc.delete(self._hash(key))

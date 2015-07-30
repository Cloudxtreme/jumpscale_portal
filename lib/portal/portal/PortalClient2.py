import requests
import os

class Resource(object):
    def __init__(self, ip, port, secret, path):
        self._ip = ip
        self._port = port
        self._secret = secret
        self._path = path

    def __getattr__(self, item):
        path = os.path.join(self._path, item)
        resource = Resource(self._ip, self._port, self._secret, path)
        setattr(self, item, resource)
        return resource

    @property
    def _url(self):
        scheme = "http" if self.port != 443 else "https"
        return "%s://%s:%s%s" % (scheme, self._ip, self._port, self._path)

    def __call__(self, **kwargs):
        kwargs['authkey'] = self._secret
        return requests.post(self._url, kwargs).json()


from urlparse import urljoin
import urllib2

from gocd.api import Pipeline


class ApiInstantiators(object):
    def pipeline(self, name):
        """Instantiates a `gocd.api.pipeline.Pipeline`.

        Instantiates the pipeline with the current server and `name` provided.

        Params:
            name: The name of the pipeline you want to interact with

        Returns:
            an instance of `gocd.api.pipeline.Pipeline`
        """
        return Pipeline(self, name)


class Server(ApiInstantiators):
    def __init__(self, host, user=None, password=None):
        self.host = host
        self.user = user
        self.password = password

        if self.user and self.password:
            self._add_basic_auth()

    def get(self, path):
        return urllib2.urlopen(self._request(path))

    def _add_basic_auth(self):
        auth_handler = urllib2.HTTPBasicAuthHandler(
            urllib2.HTTPPasswordMgrWithDefaultRealm()
        )
        auth_handler.add_password(
            realm=None,
            uri=self.host,
            user=self.user,
            passwd=self.password,
        )
        urllib2.install_opener(urllib2.build_opener(auth_handler))

    def _request(self, path, data=None, headers=None):
        default_headers = {
            'User-Agent': 'py-gocd',
        }
        default_headers.update(headers or {})

        return urllib2.Request(
            self._url(path),
            data=data,
            headers=default_headers
        )

    def _url(self, path):
        return urljoin(self.host, path)

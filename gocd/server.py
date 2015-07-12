import urllib2

from urlparse import urljoin

from gocd.api import Pipeline


class Server(object):
    def __init__(self, host, user=None, password=None):
        self.host = host
        self.user = user
        self.password = password

        if self.user and self.password:
            self._add_basic_auth()

    def get(self, path):
        return urllib2.urlopen(self._request(path))

    def pipeline(self, name):
        return Pipeline(self, name)

    def _add_basic_auth(self):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm='Cruise',  # This seems to be hard coded.
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

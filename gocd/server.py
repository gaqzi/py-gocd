from urlparse import urljoin
import re
import urllib2

from gocd.vendor.multidimensional_urlencode import urlencode

from gocd.api import Pipeline


class AuthenticationFailed(Exception):
    pass


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
    _session_id = None
    _authenticity_token = None

    def __init__(self, host, user=None, password=None):
        self.host = host
        self.user = user
        self.password = password

        if self.user and self.password:
            self._add_basic_auth()

    def get(self, path):
        return self.request(path)

    def post(self, path, **post_args):
        return self.request(path, data=post_args or {})

    def request(self, path, data=None, headers=None):
        return urllib2.urlopen(self._request(path, data=data, headers=headers))

    def add_logged_in_session(self, response=None):
        """Make the request appear to be coming from a browser

        This is to interact with older parts of Go that doesn't have a
        proper API call to be made. What will be done:

        1. If no response passed in a call to `go/api/pipelines.xml` is
           made to get a valid session
        2. JSESSIONID will be populated from this request
        3. A request to `go/pipelines` will be so the
           authenticity_token (CSRF) can be extracted. It will then
           silently be injected into `post_args` on any POST calls that
           doesn't start with `go/api` from this point.

        Args:
            response: a `gocd.api.response.Response` object from a
                      previously successful API call.
                      So we won't have to query go/api/pipelines.xml unnecessarily

        Raises:
            HTTPError: when the HTTP request fails.
            AuthenticationFailed: when failing to get the `session_id`
                                  or the `authenticity_token`.
        """
        if not response:
            response = self.get('go/api/pipelines.xml')

        for cookie in response.headers['set-cookie'].split(';'):
            if cookie.startswith('JSESSIONID'):
                self._session_id = cookie

        if not self._session_id:
            raise AuthenticationFailed('No session id extracted from request.')

        response = self.get('go/pipelines')
        match = re.search(r'name="authenticity_token".+?value="([^"]+)', response.read())
        if match:
            self._authenticity_token = match.group(1)
        else:
            raise AuthenticationFailed('Authenticity token not found on page')

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
        default_headers = {'User-Agent': 'py-gocd'}
        if self._session_id:
            default_headers['Cookie'] = 'JSESSIONID={0}'.format(self._session_id)
        default_headers.update(headers or {})

        data = self._inject_authenticity_token(data, path)
        return urllib2.Request(
            self._url(path),
            # GET is None, and anything that is a string is POST
            data=urlencode(data) if data else data,
            headers=default_headers
        )

    def _url(self, path):
        return urljoin(self.host, path)

    def _inject_authenticity_token(self, data, path):
        if(data is None
           or not self._authenticity_token
           or path.startswith('go/api')):
            return data

        if data == '':
            data = {}

        data.update(authenticity_token=self._authenticity_token)
        return data

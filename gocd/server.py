import re

try:
    # python2
    from urlparse import urljoin
    from urllib2 import (
        urlopen,
        HTTPPasswordMgrWithDefaultRealm,
        HTTPBasicAuthHandler,
        HTTPHandler,
        HTTPSHandler,
        install_opener,
        build_opener,
        Request,
    )

    class CustomRequest(Request):
        """Python2's Request class has no support
        for setting the HTTP method."""

        def __init__(self, *args, **kargs):
            if "method" in kargs:
                self.__method = kargs["method"]
                del kargs["method"]
            else:
                self.__method = None
            Request.__init__(self, *args, **kargs)

        def get_method(self):
            if self.__method is not None:
                return self.__method
            else:
                return Request.get_method(self)

except ImportError:  # pragma: no cover
    # python3
    from urllib.parse import urljoin
    from urllib.request import (
        urlopen,
        HTTPPasswordMgrWithDefaultRealm,
        HTTPBasicAuthHandler,
        HTTPHandler,
        HTTPSHandler,
        install_opener,
        build_opener,
        Request,
    )

    CustomRequest = Request

from gocd.vendor.multidimensional_urlencode import urlencoder

from gocd.api import Pipeline, PipelineGroups, Stage

__all__ = ['Server', 'AuthenticationFailed']


class AuthenticationFailed(Exception):
    pass


class Server(object):
    """Interacting with the Go server

    If user and password is supplied the client will try to login using
    HTTP Basic Auth on each request.

    The intention is to use this class as a jumping off point to the
    nicer API wrappers in the :mod:`gocd.api` package.

    Example of intended interaction with this class::

      >>> import gocd
      >>> go_server = gocd.Server('http://localhost:8153', 'admin', 'badger')
      >>> pipeline = go_server.pipeline('up42')
      >>> response = pipeline.pause('Admin says no work for you.')
      >>> response.is_ok
      True

    Args:
      host (str): The base URL for your go server.
        Example: http://go.example.com/
      user (str): The username to login as
      password (str): The password for this user
    """
    SESSION_COOKIE_NAME = 'JSESSIONID'

    #: Sets the debug level for the urllib2 HTTP(s) handlers
    request_debug_level = 0

    _session_id = None
    _authenticity_token = None

    def __init__(self, host, user=None, password=None):
        self.host = host
        self.user = user
        self.password = password

        if self.user and self.password:
            self._add_basic_auth()

    def get(self, path):
        """Performs a HTTP GET request to the Go server

        Args:
          path (str): The full path on the Go server to request.
            This includes any query string attributes.

        Raises:
          HTTPError: when the HTTP request fails.

        Returns:
          file like object: The response from a
            :func:`urllib2.urlopen` call
        """
        return self.request(path)

    def post(self, path, **post_args):
        """Performs a HTTP POST request to the Go server

        Args:
          path (str): The full path on the Go server to request.
            This includes any query string attributes.
          **post_args: Any POST arguments that should be sent to the server

        Raises:
          HTTPError: when the HTTP request fails.

        Returns:
          file like object: The response from a
            :func:`urllib2.urlopen` call
        """
        return self.request(path, data=post_args or {})

    def request(self, path, data=None, headers=None, method=None):
        """Performs a HTTP request to the Go server

        Args:
          path (str): The full path on the Go server to request.
            This includes any query string attributes.
          data (str, dict, bool, optional): If any data is present this
            request will become a POST request.
          headers (dict, optional): Headers to set for this particular
            request

        Raises:
          HTTPError: when the HTTP request fails.

        Returns:
          file like object: The response from a
            :func:`urllib2.urlopen` call
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        response = urlopen(self._request(path, data=data, headers=headers, method=method))
        self._set_session_cookie(response)

        return response

    def add_logged_in_session(self, response=None):
        """Make the request appear to be coming from a browser

        This is to interact with older parts of Go that doesn't have a
        proper API call to be made. What will be done:

        1. If no response passed in a call to `go/api/pipelines.xml` is
           made to get a valid session
        2. `JSESSIONID` will be populated from this request
        3. A request to `go/pipelines` will be so the
           `authenticity_token` (CSRF) can be extracted. It will then
           silently be injected into `post_args` on any POST calls that
           doesn't start with `go/api` from this point.

        Args:
          response: a :class:`Response` object from a previously successful
            API call. So we won't have to query `go/api/pipelines.xml`
            unnecessarily.

        Raises:
          HTTPError: when the HTTP request fails.
          AuthenticationFailed: when failing to get the `session_id`
            or the `authenticity_token`.
        """
        if not response:
            response = self.get('go/api/pipelines.xml')

        self._set_session_cookie(response)

        if not self._session_id:
            raise AuthenticationFailed('No session id extracted from request.')

        response = self.get('go/pipelines')
        match = re.search(
            r'name="authenticity_token".+?value="([^"]+)',
            response.read().decode('utf-8')
        )
        if match:
            self._authenticity_token = match.group(1)
        else:
            raise AuthenticationFailed('Authenticity token not found on page')

    def _set_session_cookie(self, response):
        if 'set-cookie' not in response.headers:
            return

        for cookie in response.headers['set-cookie'].split(';'):
            if cookie.startswith(self.SESSION_COOKIE_NAME):
                self._session_id = cookie

    def pipeline(self, name):
        """Instantiates a :class:`Pipeline` with the given name.

        Args:
          name: The name of the pipeline you want to interact with

        Returns:
          Pipeline: an instantiated :class:`Pipeline`.
        """
        return Pipeline(self, name)

    def pipeline_groups(self):
        """Returns an instance of :class:`PipelineGroups`

        Returns:
          PipelineGroups: an instantiated :class:`PipelineGroups`.
        """
        return PipelineGroups(self)

    def stage(self, pipeline_name, stage_name, pipeline_counter=None):
        """Returns an instance of :class:`Stage`

        Args:
            pipeline_name (str): Name of the pipeline the stage belongs to
            stage_name (str): Name of the stage to act on
            pipeline_counter (int): The pipeline instance the stage is for.

        Returns:
          Stage: an instantiated :class:`Stage`.
        """
        return Stage(self, pipeline_name, stage_name, pipeline_counter=pipeline_counter)

    def _add_basic_auth(self):
        auth_handler = HTTPBasicAuthHandler(
            HTTPPasswordMgrWithDefaultRealm()
        )
        auth_handler.add_password(
            realm=None,
            uri=self.host,
            user=self.user,
            passwd=self.password,
        )
        install_opener(build_opener(
            auth_handler,
            HTTPHandler(debuglevel=self.request_debug_level),
            HTTPSHandler(debuglevel=self.request_debug_level),
        ))

    def _request(self, path, data=None, headers=None, method=None):
        default_headers = {'User-Agent': 'py-gocd'}
        if self._session_id:
            default_headers['Cookie'] = self._session_id
        default_headers.update(headers or {})

        data = self._inject_authenticity_token(data, path)
        return CustomRequest(
            self._url(path),
            data=self._encode_data(data),  # None or False == GET request
            headers=default_headers,
            method=method,
        )

    def _encode_data(self, data):
        if isinstance(data, dict):
            return urlencoder.urlencode(data).encode('utf-8')
        elif isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, bytes):
            return data
        elif data is True:
            return ''.encode('utf-8')
        else:
            return None

    def _url(self, path):
        return urljoin(self.host, path)

    def _inject_authenticity_token(self, data, path):
        if (data is None or
                not self._authenticity_token or
                path.startswith('go/api')):
            return data

        if data == '':
            data = {}

        data.update(authenticity_token=self._authenticity_token)
        return data

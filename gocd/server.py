import os
import re
import json
import logging

import urllib3
from urllib3.util import make_headers
from six.moves.urllib.parse import urljoin

from gocd.api import Pipeline, PipelineGroups, Stage

__all__ = ['Server', 'AuthenticationFailed']

from gocd.config import DEBUG_MODE

FILENAME = filename = os.path.basename(__file__)


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

    #: Sets the debug level for the urllib3 HTTP(s) handlers (optional)
    # You can pass cert_reqs='CERT_REQUIRED', ca_certs=... etc. if needed
    _session_id = None
    _authenticity_token = None

    def __init__(self, host, user=None, password=None, log_file=None):
        self.host = host.rstrip('/') + '/'  # Ensure consistent trailing slash
        self.user = user
        self.password = password

        # Default headers (User-Agent + Basic Auth if provided)
        headers = {'User-Agent': 'py-gocd'}
        if user and password:
            headers.update(make_headers(basic_auth=f'{user}:{password}'))

        # Create PoolManager with default headers (reused for connection pooling)
        self.http = urllib3.PoolManager(headers=headers)

        if log_file:
            logging.basicConfig(
                filename=log_file,
                filemode='a',  # 'a' for append (default), 'w' for overwrite
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

            logging.info(f"The server is initialised @ #{self.host}")

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

        Returns an urllib3.HTTPResponse (file-like object with .read(), .data, .status, .headers)
        """
        url = self._url(path)

        # Prepare body
        body = self._encode_data(data)
        if body is not None and method is None:
            method = 'POST'

        method = method or ('POST' if body is not None else 'GET')

        # Per-request headers (session cookie + any overrides)
        req_headers = self.http.headers.copy()
        if self._session_id:
            req_headers['Cookie'] = self._session_id
        if headers:
            req_headers.update(headers)

        # Inject authenticity token for non-API POSTs
        injected_data = self._inject_authenticity_token(data, path)
        body = self._encode_data(injected_data)

        if DEBUG_MODE:
            print(f"🐞 {FILENAME} - path is %s" % path)
            print(f"🐞 {FILENAME} - data is %s" % data)
            print(f"🐞 {FILENAME} - headers is %s" % headers)
            print(f"🐞 {FILENAME} - method is %s" % method)

        response = self.http.request(
            method,
            url,
            body=body,
            headers=req_headers,
            # You can add timeout=urllib3.Timeout(...) here if desired
            # redirect=True is default in urllib3
        )

        if DEBUG_MODE:
            print(f"🐞 {FILENAME} - response.status_code is %s" % response.status)
            print(f"🐞 {FILENAME} - response is %s" % response)

        self._set_session_cookie(response)

        return response

    def add_logged_in_session(self, response=None):
        """Make the request appear to be coming from a browser

        Summary: This extracts JSESSIONID and the CSRF authenticity_token.

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
        content = response.data.decode('utf-8')  # .data is preloaded bytes
        match = re.search(
            r'name="authenticity_token".+?value="([^"]+)',
            content
        )
        if match:
            self._authenticity_token = match.group(1)
        else:
            raise AuthenticationFailed('Authenticity token not found on page')

    def _set_session_cookie(self, response):
        """Extract JSESSIONID from Set-Cookie header(s)"""
        # urllib3 normalises headers to a dict, but preserves multiple Set-Cookie as a comma-separated string

        set_cookie = response.headers.get('set-cookie') or response.headers.get('Set-Cookie')
        if not set_cookie:
            return

        # Split on commas, but be careful – values can contain commas
        # Simple split and look for the one starting with JSESSIONID
        for part in set_cookie.split(','):
            if self.SESSION_COOKIE_NAME in part:
                # Take the first occurrence (JSESSIONID=xxx; ...)
                cookie_part = part.split(';', 1)[0].strip()
                if cookie_part.startswith(self.SESSION_COOKIE_NAME + '='):
                    self._session_id = cookie_part
                    return

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

    def _encode_data(self, data):
        if isinstance(data, dict):
            return json.dumps(data, ensure_ascii=False).encode('utf-8')
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
        if data is None or not self._authenticity_token or path.startswith('go/api'):
            return data

        # if data == '':
        #     data = {}

        data.update(authenticity_token=self._authenticity_token)
        return data

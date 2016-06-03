import json
import re


# TODO: Test this class explicitly, the implicit testing we got now
# works but it doesn't define the behavior.
class Response(object):
    """A nicely wrapped HTTP Response

    This class will be instantiated from API calls and is not intended
    to be used in any other way.

    Special handling of the responses:

    1. A response has a boolean value that corresponds with :meth:`is_ok`:

        >>> bool(Response(404, 'Not found'))
        False
        >>> bool(Response(200, 'OK'))
        True

    2. If the payload is json you can access the json object through
       the response as if it was a `dict`:
        >>> response = Response(200, '{"hello": "there"}',
                                {'Content-Type': 'application/json'})
        >>> response['hello']
        "there"

    3. If the payload is json you can look if a key is part of the
       payload as you would with a `dict`:
        >>> response = Response(200, '{"hello": "there"}',
                                {'Content-Type': 'application/json'})
        >>> 'hello' in response
        True

    Args:
      status_code (int): The HTTP status of this response
      body (str, fp): The HTTP response body/payload of this response
      headers (dict, optional): The headers supplied by this response
      ok_status (int, optional): If the `status_code` is this then this
        response is successful. Default: 200
    """
    def __init__(self, status_code, body, headers=None, ok_status=200):
        self.__body = None
        self.status_code = status_code
        self._body = body
        self._body_parsed = None
        self.content_type = headers.get('content-type', '').split(';')[0] or False
        self.headers = headers or {}
        self.ok_status = ok_status or 200

    @property
    def is_ok(self):
        """Whether this response is considered successful

        Returns
          bool: True if `status_code` is `ok_status`
        """
        return self.status_code == self.ok_status

    @property
    def is_json(self):
        """
        Returns:
          bool: True if `content_type` is `application/json`
        """
        return (self.content_type.startswith('application/json') or
                re.match(r'application/vnd.go.cd.v(\d+)\+json', self.content_type))

    def __bool__(self):
        # XXX
        # I'm not sure if this is a good idea or not,
        # but I think a response should be true/false depending on whether it was ok or not.
        # Let's try it out and see whether it's a crazy idea.
        return self.is_ok
    __nonzero__ = __bool__

    def __getitem__(self, item):
        if self.is_json:
            return self.payload[item]

        self._raise_non_json_response()

    def __contains__(self, item):
        if self.is_json:
            return item in self.payload

        self._raise_non_json_response()

    @property
    def payload(self):
        """
        Returns:
          `str` when not json.
          `dict` when json.
        """
        if self.is_json:
            if not self._body_parsed:
                if hasattr(self._body, 'decode'):
                    body = self._body.decode('utf-8')
                else:
                    body = self._body

                self._body_parsed = json.loads(body)

            return self._body_parsed
        else:
            return self._body
    #: Alias for :meth:`payload`
    body = payload

    @property
    def _body(self):
        if hasattr(self.__body, 'read'):
            self.__body = self.__body.read()

        return self.__body

    @_body.setter
    def _body(self, value):
        self.__body = value

    @property
    def fp(self):
        """Returns a file-like object if the class was instantiated with one

        Returns:
          None, file-like object: If :attribute:`_body` responds to read else None
        """
        if hasattr(self.__body, 'read'):
            return self.__body

        return None

    @property
    def etag(self):
        return self.headers["ETag"]

    @classmethod
    def _from_request(cls, response, ok_status=None):
        return Response(
            response.code,
            response,
            response.headers,
            ok_status=ok_status
        )

    @classmethod
    def _from_http_error(cls, http_error):
        return Response(
            http_error.code,
            http_error.fp.read(),
            http_error.headers,
        )

    @classmethod
    def _from_json(cls, body):
        return Response(200, json.dumps(body), {'content-type': 'application/json'})

    def _raise_non_json_response(self):
        raise AttributeError(
            "Can't lookup item in a non-JSON response.",
            content_type=self.content_type
        )

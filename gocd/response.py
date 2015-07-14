import json


# TODO: Test this class explicitly, the implicit testing we got now works but it doesn't define the behavior.
class Response(object):
    def __init__(self, status_code, body, headers=None, ok_status=None):
        self.status_code = status_code
        self._body = body
        self._body_parsed = None
        self.content_type = headers['content-type'].split(';')[0]
        self.headers = headers
        self.ok_status = ok_status or 200

    @property
    def is_ok(self):
        return self.status_code == self.ok_status

    @property
    def is_json(self):
        return self.content_type.startswith('application/json')

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
        if self.is_json:
            if not self._body_parsed:
                self._body_parsed = json.loads(self._body)

            return self._body_parsed
        else:
            return self._body

    @classmethod
    def from_request(cls, response, ok_status=None):
        return Response(
            response.code,
            response.read(),
            response.headers,
            ok_status=ok_status
        )

    @classmethod
    def from_http_error(cls, http_error):
        return Response(
            http_error.code,
            http_error.read(),
            http_error.headers,
        )

    def _raise_non_json_response(self):
        raise AttributeError(
            "Can't lookup item in a non-JSON response.",
            content_type=self.content_type
        )

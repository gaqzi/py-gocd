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

    def __bool__(self):
        # XXX
        # I'm not sure if this is a good idea or not,
        # but I think a response should be true/false depending on whether it was ok or not.
        # Let's try it out and see whether it's a crazy idea.
        return self.is_ok
    __nonzero__ = __bool__


    @property
    def payload(self):
        if self.content_type.startswith('application/json'):
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

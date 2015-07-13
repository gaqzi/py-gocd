import urllib2
from gocd import Response


class Pipeline(object):
    uri = 'go/api/pipelines'

    def __init__(self, server, name):
        self.server = server
        self.name = name

    def history(self, offset=0):
        return Response.from_request(self.server.get(
            '{base_uri}/{pipeline}/history/{offset}'.format(
                base_uri=self.uri,
                pipeline=self.name,
                offset=offset or 0,
            )))

    def release(self):
        try:
            return Response.from_request(self.server.post(
                '{base_uri}/{pipeline}/releaseLock'.format(
                    base_uri=self.uri,
                    pipeline=self.name,
                )))
        except urllib2.HTTPError as exc:
            return Response.from_http_error(exc)

    def pause(self, reason=''):
        try:
            return Response.from_request(self.server.post(
                '{base_uri}/{pipeline}/pause'.format(
                    base_uri=self.uri,
                    pipeline=self.name,
                ),
                pauseCause=reason,
            ))
        except urllib2.HTTPError as exc:
            return Response.from_http_error(exc)

    def unpause(self):
        try:
            return Response.from_request(self.server.post(
                '{base_uri}/{pipeline}/unpause'.format(
                    base_uri=self.uri,
                    pipeline=self.name,
                )))
        except urllib2.HTTPError as exc:
            return Response.from_http_error(exc)

    def status(self):
        return Response.from_request(self.server.get(
            '{base_uri}/{pipeline}/status'.format(
                base_uri=self.uri,
                pipeline=self.name,
            )))

    def instance(self, counter):
        return Response.from_request(self.server.get(
            '{base_uri}/{pipeline}/instance/{counter:d}'.format(
                base_uri=self.uri,
                pipeline=self.name,
                counter=counter,
            )))

    def schedule(self, **material_args):
        try:
            return Response.from_request(
                self.server.post(
                    '{base_uri}/{pipeline}/schedule'.format(
                        base_uri=self.uri,
                        pipeline=self.name,
                    ),
                    **material_args
                ),
                ok_status=202.
            )
        except urllib2.HTTPError as exc:
            return Response.from_http_error(exc)

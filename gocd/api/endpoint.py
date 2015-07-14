import urllib2

from gocd.api.response import Response


class Endpoint(object):
    # The cached responses
    _base_path = None
    _id = None

    def get_id(self):
        if self._id is None:
            self._id = getattr(self, self.id, None)
            if self._id is None:
                raise NotImplementedError(
                    'id is not set. It is needed when calling a specific '
                    'instance of an endpoint. '
                )

        return self._id

    def get_base_path(self):
        if getattr(self, 'base_path', None) is None:
            raise NotImplementedError(
                "base_path is not set. I don't know where to query on "
                "the Go server."
            )

        if not self._base_path:
            self._base_path = self.base_path.format(id=self.get_id())

        return self._base_path

    def _join_path(self, path):
        return '{0}/{1}'.format(self.get_base_path(), path).replace('//', '/')

    def _get(self, path, ok_status=None):
        return self._request(path, ok_status=ok_status)

    def _post(self, path, ok_status=None, **post_args):
        return self._request(path, ok_status=ok_status, data=post_args or '')

    def _request(self, path, ok_status, data=None):
        try:
            return Response.from_request(
                self.server.request(self._join_path(path), data=data),
                ok_status=ok_status
            )
        except urllib2.HTTPError as exc:
            return Response.from_http_error(exc)

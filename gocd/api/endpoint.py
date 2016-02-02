try:
    # python2
    from urllib2 import HTTPError
except ImportError:  # pragma: no cover
    # python3
    from urllib.request import HTTPError


from gocd.api.response import Response


class Endpoint(object):
    # The cached responses
    _base_path = None
    _id = None

    id = None  #: This points to an attribute that contains the id of this endpoint
    base_path = None  #: URI base path to search for. Any URL generated will start with this.
    server = None  #: An instance of :class:`gocd.Server`.

    def get_id(self):
        if self._id is None:
            if self.id is not None:
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
        # TODO: Make this more robust. `urlparse.urljoin` didn't quite work as I wanted.
        return '{0}/{1}'.format(self.get_base_path(), path).replace('//', '/')

    def _get(self, path, ok_status=None, headers=None):
        return self._request(path, ok_status=ok_status, headers=headers)

    def _post(self, path, ok_status=None, headers=None, **post_args):
        return self._request(path, ok_status=ok_status, data=post_args or {}, headers=headers)

    # TODO: Add tests for adding headers
    def _request(self, path, ok_status, data=None, headers=None, method=None):
        try:
            return Response._from_request(
                self.server.request(
                    self._join_path(path),
                    data=data,
                    headers=headers,
                    method=method,
                ),
                ok_status=ok_status
            )
        except HTTPError as exc:
            return Response._from_http_error(exc)

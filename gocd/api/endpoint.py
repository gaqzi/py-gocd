import urllib2
from gocd.response import Response


# TODO: Think about the design of this class.
# The handling of base_path doesn't feel pythonesque, probably should
# follow the `get_base_path()` pattern from Django instead. Same with _id.
class Endpoint(object):
    _base_path = None   # What should be configured for each pipeline
    __base_path = None  # The cached response of replacing `_id`

    @property
    def _id(self):
        raise KeyError('No `_id` defined as the primary identifier for this API endpoint.')

    @property
    def base_path(self):
        if not self.__base_path:
            self.__base_path = self._base_path.format(id=self._id)

        return self.__base_path

    def _join_path(self, path):
        return '{0}/{1}'.format(self.base_path, path).replace('//', '/')

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

import json
from gocd.api.endpoint import Endpoint

__all__ = ['PluggableSCM']


class PluggableSCM(Endpoint):
    base_path = 'go/api/admin/scms'
    id = 'name'

    def __init__(self, server, name=""):
        """A wrapper for the `Go pluggable SCM API`__

        .. __: https://api.go.cd/current/#scms

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          name (str): The name of the SCM material
        """
        self.server = server
        self.name = name

    def list(self):
        """Lists all available pluggable scm materials,
           these are materials that are present in the in cruise-config.xml.

        See the `Go pluggable SCM documentation`__ for example responses.

        .. __: https://api.go.cd/current/#get-all-pluggable-scm-materials

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get("", headers={"Accept": self._accept_header_value})

    def get(self):
        """Gets SCM material for specified material name

        See `The global scm config object`__ for example responses.

        .. __: https://api.go.cd/current/#the-global-scm-config-object

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get(self.name, headers={"Accept": self._accept_header_value})

    def edit(self, config, etag):
        """Update SCM material for specified material  name.

        .. __: https://api.go.cd/current/#update-pluggable-scm-object

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        data = self._json_encode(config)
        headers = self._default_headers()

        if etag is not None:
            headers["If-Match"] = etag

        return self._request(self.name,
                             ok_status=None,
                             data=data,
                             headers=headers,
                             method="PUT")

    def create(self, config):
        """Create a global SCM object

        .. __: https://api.go.cd/current/#create-a-scm-object

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        assert config["name"] == self.name, "SCM configuration name doesn't match"
        assert "configuration" in config, "SCM has no configuration"

        data = self._json_encode(config)
        headers = self._default_headers()

        return self._request("",
                             ok_status=None,
                             data=data,
                             headers=headers,
                             method="POST")

    def _default_headers(self):
        return {"Accept": self._accept_header_value,
                "Content-Type": "application/json"}

    @property
    def _accept_header_value(self):
        return "application/vnd.go.cd.v1+json"

    @staticmethod
    def _json_encode(config):
        return json.dumps(config)

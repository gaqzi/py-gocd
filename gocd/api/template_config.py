import json
from gocd.api.endpoint import Endpoint

__all__ = ['TemplateConfig']


class TemplateConfig(Endpoint):
    base_path = 'go/api/admin/templates'
    id = 'name'

    def __init__(self, server, name, api_version=2):
        """A wrapper for the `Go template config API`__

        .. __: https://api.go.cd/current/#template-config

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          name (str): The name of the template we're working on
        """
        self.server = server
        self.name = name
        self.api_version = api_version

    def get(self):
        """Get template config for specified template name.

        See `The template config object`__ for example responses.

        .. __: https://api.go.cd/current/#the-template-config-object

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get(self.name, headers={"Accept": self._accept_header_value})

    def edit(self, config, etag):
        """Update template config for specified template name.

        .. __: https://api.go.cd/current/#edit-template-config

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
        """Create template config for specified template name.

        .. __: https://api.go.cd/current/#create-template-config

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        assert config["name"] == self.name, "Given config is not for this template"

        data = self._json_encode(config)
        headers = self._default_headers()

        return self._request("",
                             ok_status=None,
                             data=data,
                             headers=headers)

    def delete(self):
        """Delete template config for specified template name.

        .. __: https://api.go.cd/current/#delete-a-template

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        headers = self._default_headers()

        return self._request(self.name,
                             ok_status=None,
                             data=None,
                             headers=headers,
                             method="DELETE")

    def _default_headers(self):
        return {"Accept": self._accept_header_value,
                "Content-Type": "application/json"}

    @property
    def _accept_header_value(self):
        return "application/vnd.go.cd.v{0}+json".format(self.api_version)

    @staticmethod
    def _json_encode(config):
        return json.dumps(config)

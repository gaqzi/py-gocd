import json
from gocd.api.endpoint import Endpoint

__all__ = ['PipelineConfig']


class PipelineConfig(Endpoint):
    base_path = 'go/api/admin/pipelines'
    id = 'name'
    #: The result of a job/stage has been finalised when these values are set
    final_results = ['Passed', 'Failed']

    def __init__(self, server, name, api_version=2):
        """A wrapper for the `Go pipeline config API`__

        .. __: https://api.go.cd/current/#pipeline-config

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          name (str): The name of the pipeline we're working on
        """
        self.server = server
        self.name = name
        self.api_version = api_version

    def get(self):
        """Gets pipeline config for specified pipeline name.

        See `The pipeline config object`__ for example responses.

        .. __: https://api.go.cd/current/#the-pipeline-config-object

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get(self.name, headers={"Accept": self._accept_header_value})

    def edit(self, config, etag):
        """Update pipeline config for specified pipeline name.

        .. __: https://api.go.cd/current/#edit-pipeline-config

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
        """Update pipeline config for specified pipeline name.

        .. __: https://api.go.cd/current/#edit-pipeline-config

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        assert config["name"] == self.name, "Given config is not for this pipeline"
        assert "group" in config, "Given config has no group"

        data = self._json_encode(config)
        headers = self._default_headers()

        return self._request("",
                             ok_status=None,
                             data=data,
                             headers=headers)

    def _default_headers(self):
        return {"Accept": self._accept_header_value,
                "Content-Type": "application/json"}

    @property
    def _accept_header_value(self):
        return "application/vnd.go.cd.v{0}+json".format(self.api_version)

    @staticmethod
    def _json_encode(config):
        return json.dumps(config)

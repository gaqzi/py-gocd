from gocd.api.endpoint import Endpoint


class PipelineGroups(Endpoint):
    base_path = 'go/api/config'
    _id = False
    _response = None
    _pipelines = None

    def __init__(self, server):
        self.server = server

    def get_pipeline_groups(self):
        """Makes a call to the Go server to fetch the pipeline groups.

        Saves the response to :attr:`response`.

        Returns:
          Response: an instance of :class:`gocd.api.Response`
        """
        self._response = self._get('/pipeline_groups')

        return self._response

    @property
    def response(self):
        """Returns the last response from fetching the pipeline groups from Go

        If there is no response then one will be fetched and returned.

        Returns:
          Response: an instance of :class:`gocd.api.Response`
        """
        if self._response is None:
            self.get_pipeline_groups()

        return self._response

    @property
    def pipelines(self):
        """Returns a set of all pipelines from the last response

        Returns:
          set: Response success: all the pipelines available in the response
               Response failure: an empty set
        """
        if not self.response:
            return set()
        elif self._pipelines is None and self.response:
            self._pipelines = set()
            for group in self.response.payload:
                for pipeline in group['pipelines']:
                    self._pipelines.add(pipeline['name'])

        return self._pipelines

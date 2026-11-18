from enum import Enum

from gocd.api.endpoint import Endpoint

__all__ = ['Stage']


class Stage(Endpoint):
    # Todo: I think we can remove {id} as the components of the stage URIs is not fixed
    base_path = 'go/api/stages/{id}'

    class PathAssist(Enum):
        INSTANCE = 'instance'
        HISTORY = 'history'
        CANCEL = 'cancel'

    def __init__(self, server, pipeline_name, stage_name, pipeline_counter=None,
        stage_counter=None):
        """A wrapper for the `Go stage API`__

        .. __: http://api.go.cd/current/#stages
        details: only 1 API - to run a stage, stage_counter is not used

        .. __: http://api.go.cd/current/#stage-instances
        details: 5 APIs, stage_counter is used in 4/5 of them

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          pipeline_name (str): The name of the pipeline we're working on
          stage_name (str): The name of the stage we're working on
        """
        self.server = server
        self.pipeline_name = pipeline_name
        self.pipeline_counter = pipeline_counter
        self.stage_name = stage_name
        self.stage_counter = stage_counter
        self.assist_in_getting_id = True
        self.get_path_for = None;

    def get_id(self):
        if not self.assist_in_getting_id:
            return ""

        if self.pipeline_name is None or self.pipeline_counter is None or self.stage_name is None:
            raise Exception('You must provide a pipeline name, a pipeline counter, and a stage '
                            'name')
        value = self.get_path_for

        if value in (self.PathAssist.INSTANCE, self.PathAssist.CANCEL):
           return "{}/{}/{}".format(
               self.pipeline_name,
               self.pipeline_counter,
               self.stage_name
           )

        elif value == self.PathAssist.HISTORY:
           return "{}/{}".format(
               self.pipeline_name,
               self.stage_name
           )

        else:
           return None

    def run(self):
        """Runs a specified stage

        See the `Go stage run documentation`__ for example responses.

        .. __: https://api.gocd.org/current/#run-stage

        Args:
          pipeline_name (str): Name of the pipeline.
          pipeline_counter (int): Name of the pipeline.
          stage_name (str): Name of the pipeline.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        return self._post('/run', 202, headers={
            "X-GoCD-Confirm": "true",
            "Accept": "application/vnd.go.cd.v2+json"},
                          method="POST"
                          )

    def cancel(self, stage_counter=None):
        """Cancels a currently running stage

        See the `Go stage cancel documentation`__ for example responses.

        .. __: https://api.gocd.org/current/#cancel-stage

        Args:
          stage_counter (int): Name of the pipeline.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        if stage_counter is None:
            raise Exception('You must provide a stage counter')

        if type(stage_counter) is not int:
            raise Exception('Stage counter must be an integer')

        # We need it specifically for test_cancel_error
        self.stage_counter = stage_counter

        self.get_path_for = self.PathAssist.CANCEL

        path = f'/{stage_counter}/cancel'

        return self._post(path, headers={
            "X-GoCD-Confirm": "true", "Accept":
                "application/vnd.go.cd.v3+json"},
                          method="POST"
                          )

    def history(self, page_size=0, after=None, before=None):
        """Lists previous instances/runs of the stage

        See the `Go stage history documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-stage-history

        Args:
          page_size (int, optional): The number of records per page. Can be between 10 and 100. Defaults to 10.
          after (int, optional): The cursor value for fetching the next set of records.
          before (int, optional): The cursor value for fetching the previous set of records.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        ps = page_size or 10
        parts = [f'page_size={ps}']

        if after is not None:
            parts.append(f'after={after}')
        if before is not None:
            parts.append(f'before={before}')

        query = '&'.join(parts)
        path = f'/history?{query}'

        self.get_path_for = self.PathAssist.HISTORY

        return self._get(path, headers={"Accept": "application/vnd.go.cd.v3+json"})

    def instance(self, stage_counter=None):
        """Returns all the information regarding a specific stage run

        See the `Go stage instance documentation`__ for examples.

        .. __: http://api.go.cd/current/#get-stage-instance

        Args:
          stage_counter (int): The stage instance to fetch.
            If falsey returns the latest stage instance from :meth:`history`.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """

        if not stage_counter:
            raise Exception('You must provide a stage counter')

        self.get_path_for = self.PathAssist.INSTANCE

        return self._get('/{counter:d}'
                         .format(counter=stage_counter), headers={"Accept": "application/vnd.go.cd.v3+json"})

from gocd.api.endpoint import Endpoint

__all__ = ['Stage']


class Stage(Endpoint):
    base_path = 'go/api/stages/{id}'

    def __init__(self, server, pipeline_name, pipeline_counter, stage_name):
        """A wrapper for the `Go stage API`__

        .. __: http://api.go.cd/current/#stages

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

    def get_id(self):
        return "{pipeline}/{stage}".format(pipeline=self.pipeline_name,
                                           stage=self.stage_name)

    def history(self, offset=0):
        """Lists previous instances/runs of the stage

        See the `Go stage history documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-stage-history

        Args:
          offset (int, optional): How many instances to skip for this response.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get('/history/{offset:d}'.format(offset=offset or 0))

    def instance(self, counter=None):
        """Returns all the information regarding a specific stage run

        See the `Go stage instance documentation`__ for examples.

        .. __: http://api.go.cd/current/#get-stage-instance

        Args:
          counter (int): The stage instance to fetch.
            If falsey returns the latest stage instance from :meth:`history`.

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        # if not counter:
        #     history = self.history()
        #     if not history:
        #         return history
        #     else:
        #         return Response._from_json(history['stages'][0])

        return self._get('/instance/{pipeline_counter:d}/{counter:d}'
                         .format(pipeline_counter=self.pipeline_counter,
                                 counter=counter))

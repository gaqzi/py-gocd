from gocd.api.endpoint import Endpoint


class Artifact(Endpoint):
    base_path = 'go/files/{pipeline}/{counter}/{stage}/{stage_counter}/{job}'

    def __init__(self, server, pipeline, counter, stage, job, stage_counter=1):
        """A wrapper for the `Go artifact API`__

        .. __: http://api.go.cd/current/#artifacts

        Args:
          server (Server): A configured instance of
            :class:gocd.server.Server
          pipeline (str): The name of the pipeline to work with
          counter (int): The counter of the pipeline to work with
          stage (str): The name of the stage to work with
          job (str): The name of the job to work with
          stage_counter (int): The counter of the stage to work with, defaults to 1
        """
        self.server = server
        self.pipeline = pipeline
        self.counter = counter
        self.stage = stage
        self.job = job
        self.stage_counter = stage_counter

        self._base_path = self.base_path.format(
            pipeline=self.pipeline,
            counter=self.counter,
            stage=self.stage,
            stage_counter=self.stage_counter,
            job=self.job
        )

    def list(self):
        """Lists all available artifacts in this job.

        See the `Go artifact list documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-all-artifacts

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get('.json')

    def get(self, path_to_file):
        """Gets an artifact directory by its path.

        See the `Go artifact file documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-artifact-file

        Args:
          path_to_file (str): The path to file to get. It can be nested eg
            ```dist/foobar-widgets-1.2.0.jar```

        Returns:
          file like object: The response from a
            :func:`urllib2.urlopen` call
        """
        return self.server.request(
            self._join_path(path_to_file),
            data=None,
            headers=None
        )

    def get_directory(self, path_to_directory):
        """Gets an artifact directory by its path.

        See the `Go artifact directory documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-artifact-directory

        Args:
          path_to_directory (str): The path to the directory to get.
            It can be nested eg ```target/dist.zip```

        Returns:
          file like object: The response from a
            :func:`urllib2.urlopen` call
        """
        return self.server.request(
            self._join_path(path_to_directory + ".zip"),
            data=None,
            headers=None
        )

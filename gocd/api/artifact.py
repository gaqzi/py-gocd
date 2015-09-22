from gocd.api.endpoint import Endpoint
import time


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
            ``dist/foobar-widgets-1.2.0.jar``

        Returns:
          Response: :class:`gocd.api.response.Response` object
        """
        return self._get(path_to_file)

    def get_directory(self, path_to_directory, timeout=30, backoff=0.4, max_wait=4):
        """Gets an artifact directory by its path.

        See the `Go artifact directory documentation`__ for example responses.

        .. __: http://api.go.cd/current/#get-artifact-directory

        .. note::
          Getting a directory relies on Go creating a zip file of the
          directory in question. Because of this Go will zip the file in
          the background and return a 202 Accepted response. It's then up
          to the client to check again later and get the final file.

          To work with normal assumptions this :meth:`get_directory` will
          retry itself up to ``timeout`` seconds to get a 200 response to
          return. At that point it will then return the response as is, no
          matter whether it's still 202 or 200. The retry is done with an
          exponential backoff with a max value between retries. See the
          ``backoff`` and ``max_wait`` variables.

          If you want to handle the retry logic yourself then use :meth:`get`
          and add '.zip' as a suffix on the directory.

        Args:
          path_to_directory (str): The path to the directory to get.
            It can be nested eg ``target/dist.zip``
          timeout (int): How many seconds we will wait in total for a
            successful response from Go when we're receiving 202
          backoff (float): The initial value used for backoff, raises
            exponentially until it reaches ``max_wait``
          max_wait (int): The max time between retries

        Returns:
          Response: :class:`gocd.api.response.Response` object
            A successful response is a zip-file.
        """
        response = None
        started_at = None
        time_elapsed = 0

        i = 0
        while time_elapsed < timeout:
            response = self._get('{0}.zip'.format(path_to_directory))

            if response:
                break
            else:
                if started_at is None:
                    started_at = time.time()

                time.sleep(min(backoff * (2 ** i), max_wait))
                i += 1
                time_elapsed = time.time() - started_at

        return response

from gocd.api.endpoint import Endpoint


class Pipeline(Endpoint):
    base_path = 'go/api/pipelines/{id}'
    id = 'name'

    def __init__(self, server, name):
        self.server = server
        self.name = name

    def history(self, offset=0):
        return self._get('/history/{offset:d}'.format(offset=offset or 0))

    def release(self):
        return self._post('/releaseLock')
    unlock = release

    def pause(self, reason=''):
        return self._post('/pause', pauseCause=reason)

    def unpause(self):
        return self._post('/unpause')

    def status(self):
        return self._get('/status')

    def instance(self, counter):
        return self._get('/instance/{counter:d}'.format(counter=counter))

    def schedule(self, variables=None, secure_variables=None, materials=None):
        """Schedule a pipeline run

        Args:
          variables (dict, optional): Variables to set/override
          secure_variables (dict, optional): Secure variables to set/override
          materials (dict, optional): Material revisions to be used for
            this pipeline run. The exact format for this is a bit iffy,
            have a look at the official  `Go documentation`_ or inspect
            a call from triggering manually in the UI.

         .. _`Go documentation`: http://api.go.cd/current/#scheduling-pipelines

        Returns:
          :class:`gocd.api.Response`
        """
        scheduling_args = dict(
            variables=variables,
            secure_variables=secure_variables,
            material_fingerprint=materials,
        )

        for k, v in scheduling_args.items():
            if v is None:
                del scheduling_args[k]

        return self._post('/schedule', ok_status=202, **scheduling_args)
    run = schedule
    trigger = schedule

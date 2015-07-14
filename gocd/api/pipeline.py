from gocd.api.endpoint import Endpoint


class Pipeline(Endpoint):
    _base_path = 'go/api/pipelines/{id}'

    @property
    def _id(self):
        return self.name

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

    def schedule(self, **material_args):
        return self._post('/schedule', ok_status=202, **material_args)
    run = schedule

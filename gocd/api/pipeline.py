from gocd import Response


class Pipeline(object):
    uri = 'go/api/pipelines'

    def __init__(self, server, name):
        self.server = server
        self.name = name

    def history(self, offset=0):
        return Response.from_request(self.server.get(
            '{base_uri}/{pipeline}/history/{offset}'.format(
                base_uri=self.uri,
                pipeline=self.name,
                offset=offset or 0,
            )))

    def schedule(self, materials=None):
        pass

    def release(self):
        pass

    def pause(self):
        pass

    def unpause(self):
        pass

    def status(self):
        pass

    def instance(self, counter):
        pass

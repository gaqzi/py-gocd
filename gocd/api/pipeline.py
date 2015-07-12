class Pipeline(object):
    def __init__(self, server, name):
        self.server = server
        self.name = name

    def history(self, offset=0):
        return self.server.get(
            '/api/pipelines/{pipeline}/history/{offset}'.format(
                pipeline=self.name,
                offset=offset,
            ))

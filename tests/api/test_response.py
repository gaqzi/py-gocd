from gocd.api.response import Response


class TestResponseContentType(object):
    def test_no_content_type(self):
        response = Response(status_code=200, body='hello', headers={})

        assert not response.content_type

    def test_normal_content_type(self):
        response = Response(
            status_code=200,
            body='hello',
            headers={'content-type': 'application/json; charset=utf8'}
        )

        assert response.content_type == 'application/json'

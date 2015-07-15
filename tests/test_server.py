import pytest
import vcr

from gocd.server import Server
from gocd.vendor.multidimensional_urlencode import urlencode
import gocd.api


@pytest.fixture
def server():
    return Server('http://localhost:8153', user='ba', password='secret')


@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-basic-auth-get.yml',
    'tests/fixtures/cassettes/server-without-auth-get.yml',
])
def test_get_request_with_and_without_auth(server, cassette_name):
    with vcr.use_cassette(cassette_name) as _:
        response = server.get('go/api/pipelines/Simple/history/0')

    assert response.code == 200
    assert response.headers.type == 'application/json'


@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-basic-auth-post.yml',
    'tests/fixtures/cassettes/server-without-auth-post.yml',
])
def test_post_request_without_argument(server, cassette_name):
    with vcr.use_cassette(cassette_name) as _:
        response = server.post('go/api/pipelines/Simple/schedule')

    assert response.code == 202
    assert response.headers.type == 'text/html'


@vcr.use_cassette('tests/fixtures/cassettes/post-with-argument.yml')
def test_post_with_an_argument(server):
    response = server.post(
        'go/api/pipelines/Simple/pause',
        pauseCause='Time to sleep'
    )

    assert response.code == 200


@vcr.use_cassette('tests/fixtures/cassettes/server-enable-session-auth.yml')
def test_post_with_an_argument(server):
    server.add_logged_in_session()
    request = server._request('go/run/Simple-with-lock/11/firstStage', data={})

    assert 'JSESSIONID={0}'.format(server._session_id) in request.headers['Cookie']
    assert 'authenticity_token' in request.data


def test_pipeline_creates_a_pipeline_instance(server):
    pipeline = server.pipeline('Simple')

    assert isinstance(pipeline, gocd.api.Pipeline)
    assert pipeline.name == 'Simple'

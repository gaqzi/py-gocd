import pytest
try:
    #python2
    from urllib2 import urlopen, HTTPError
except ImportError:
    #python3
    from urllib.request import urlopen, HTTPError


import vcr

from gocd.server import Server
import gocd.api


@pytest.fixture
def server():
    return Server('http://localhost:8153', user='ba', password='secret')


@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-basic-auth-get.yml',
    'tests/fixtures/cassettes/server-without-auth-get.yml',
])
def test_get_request_with_and_without_auth(server, cassette_name):
    with vcr.use_cassette(cassette_name):
        response = server.get('go/api/pipelines/Simple/history/0')

    assert response.code == 200
    assert response.headers["Content-Type"] == 'application/json; charset=utf-8'


@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-basic-auth-post.yml',
    'tests/fixtures/cassettes/server-without-auth-post.yml',
])
def test_post_request_without_argument(server, cassette_name):
    with vcr.use_cassette(cassette_name):
        response = server.post('go/api/pipelines/Simple/schedule')

    assert response.code == 202
    assert response.headers["Content-Type"] == 'text/html; charset=utf-8'


@pytest.mark.parametrize('data', [{}, '', True])
def test_request_with_all_kinds_of_falsey_values_that_should_be_post(server, data):
    with vcr.use_cassette('tests/fixtures/cassettes/server-data-for-post-requests.yml'):
        response = urlopen(
            server._request('go/api/pipelines/Simple-with-lock/pause', data=data)
        )

    assert response.code == 200
    assert response.headers["Content-Type"] == 'text/html; charset=utf-8'
    #assert response.fp.read() == ' '


@pytest.mark.parametrize('data', [[], None, False])
def test_request_with_with_explicitly_no_post_data(server, data):
    # This is meant to fail with a 404 since this endpoint is post only.
    with vcr.use_cassette('tests/fixtures/cassettes/server-data-for-get-requests.yml'):
        with pytest.raises(HTTPError) as exc:
            urlopen(server._request('go/api/pipelines/Simple-with-lock/pause', data=data))

    assert exc.value.code == 404


@vcr.use_cassette('tests/fixtures/cassettes/post-with-argument.yml')
def test_post_with_an_argument(server):
    response = server.post(
        'go/api/pipelines/Simple/pause',
        pauseCause='Time to sleep'
    )

    assert response.code == 200


@vcr.use_cassette('tests/fixtures/cassettes/server-enable-session-auth.yml')
def test_post_session_with_an_argument(server):
    server.add_logged_in_session()
    request = server._request('go/run/Simple-with-lock/11/firstStage', data={})

    assert server._session_id in request.headers['Cookie']
    assert 'JSESSIONID=JSESSIONID=' not in request.headers['Cookie']
    assert 'authenticity_token' in request.data.decode("utf-8")


@vcr.use_cassette('tests/fixtures/cassettes/server-without-auth-get.yml')
def test_set_session_cookie_after_successful_request(server):
    assert server._session_id is None

    server.get('go/api/pipelines/Simple/history/0')
    assert server._session_id

    # Ensure the saved session cookie is used in subsequent requests
    with vcr.use_cassette('tests/fixtures/cassettes/server-enable-session-auth.yml'):
        request = server._request('go/run/Simple-with-lock/11/firstStage', data={})
        assert server._session_id in request.headers['Cookie']


def test_pipeline_creates_a_pipeline_instance(server):
    pipeline = server.pipeline('Simple')

    assert isinstance(pipeline, gocd.api.Pipeline)
    assert pipeline.name == 'Simple'


def test_pipeline_groups_creates_a_pipeline_groups_instance(server):
    pipeline_groups = server.pipeline_groups()

    assert isinstance(pipeline_groups, gocd.api.PipelineGroups)

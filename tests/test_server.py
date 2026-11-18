import pytest

import vcr

from gocd.server import Server
import gocd.api


@pytest.fixture
def server():
    return Server('http://localhost:8153', user='ba', password='secret')


@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-basic-auth-get.yml',
    'tests/fixtures/cassettes/server-without-auth-get-considering-a-proxy-injecting-an-auth-token'
    '-or-the-gocd-server-itself-has-no-auth-for-this-specific-uri.yml',
])
def test_get_request_with_and_without_auth(server, cassette_name):
    with vcr.use_cassette(cassette_name):
        response = server.get('go/api/pipelines/Simple/history/0')

    assert response.status == 200
    assert response.headers["Content-Type"] == 'application/json; charset=utf-8'

@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-without-auth-get.yml',
])
def test_get_request_without_auth(server, cassette_name):
    with vcr.use_cassette(cassette_name):
        response = server.get('go/api/pipelines/Simple/history/0')

    assert response.status == 401
    assert response.headers["Content-Type"] == 'text/html; charset=iso-8859-1'

    payload = response.data.decode("iso-8859-1")

    assert "Full authentication is required to access this resource" in payload

@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-basic-auth-post.yml',
    'tests/fixtures/cassettes/server-without-auth-post-considering-a-proxy-injecting-an-auth-token'
    '-or-the-gocd-server-itself-has-no-auth-for-this-specific-uri.yml',
])
def test_post_request_without_argument(server, cassette_name):
    with vcr.use_cassette(cassette_name):
        response = server.post('go/api/pipelines/Simple/schedule')

    assert response.status == 202
    assert response.headers["Content-Type"] == 'text/html; charset=utf-8'

@pytest.mark.parametrize('cassette_name', [
    'tests/fixtures/cassettes/server-without-auth-post.yml',
])
def test_post_request_without_argument_unauthorised(server, cassette_name):
    with vcr.use_cassette(cassette_name):
        response = server.post('go/api/pipelines/Simple/schedule')

    assert response.status == 401
    assert response.headers["Content-Type"] == 'text/html; charset=iso-8859-1'

    payload = response.data.decode("iso-8859-1")

    assert "Full authentication is required to access this resource" in payload

@pytest.mark.parametrize('data', [{}, '', True])
def test_request_with_all_kinds_of_falsey_values_that_should_be_post(server, data):
    with vcr.use_cassette('tests/fixtures/cassettes/server-data-for-post-requests.yml'):
        response = server.request('go/api/pipelines/Simple-with-lock/pause', data=data)

    assert response.status == 200
    assert response.headers["Content-Type"] == 'text/html; charset=utf-8'
    assert response.read() in (b'', b' ')


@pytest.mark.parametrize('data', [[], None, False])
def test_request_with_with_explicitly_no_post_data(server, data):
    # This is meant to fail with a 404 since this endpoint is post only.
    with vcr.use_cassette('tests/fixtures/cassettes/server-data-for-get-requests.yml'):
            response = server.request('go/api/pipelines/Simple-with-lock/pause', data=data)

    assert response.status in (404, 405), f"Expected 404/405, got {response.status}"


@vcr.use_cassette('tests/fixtures/cassettes/post-with-argument.yml')
def test_post_with_an_argument(server):
    response = server.post(
        'go/api/pipelines/Simple/pause',
        pauseCause='Time to sleep'
    )

    assert response.status == 200


@vcr.use_cassette('tests/fixtures/cassettes/server-enable-session-auth.yml')
def test_post_session_with_an_argument(server):
    server.add_logged_in_session()
    response = server.request('go/run/Simple-with-lock/11/firstStage', data={})

    assert response is not None
    assert server._session_id is not None
    assert 'JSESSIONID=' in server._session_id

    assert 'authenticity_token' in response.data.decode('utf-8')

@vcr.use_cassette('tests/fixtures/cassettes/server-without-auth-get.yml')
def test_set_session_cookie_after_successful_request(server):
    assert server._session_id is None

    server.get('go/api/pipelines/Simple/history/0')
    assert server._session_id

    # Ensure the saved session cookie is used in subsequent requests
    with vcr.use_cassette('tests/fixtures/cassettes/server-enable-session-auth.yml'):
        request = server.request('go/run/Simple-with-lock/11/firstStage', data={})
        assert request is not None


def test_pipeline_creates_a_pipeline_instance(server):
    pipeline = server.pipeline('Simple')

    assert isinstance(pipeline, gocd.api.Pipeline)
    assert pipeline.name == 'Simple'


def test_pipeline_groups_creates_a_pipeline_groups_instance(server):
    pipeline_groups = server.pipeline_groups()

    assert isinstance(pipeline_groups, gocd.api.PipelineGroups)

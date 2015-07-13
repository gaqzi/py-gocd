import pytest
import vcr

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='ba', password='secret')


@pytest.fixture
def pipeline(server):
    return server.pipeline('Simple')


@pytest.fixture
def locked_pipeline(server):
    return server.pipeline('Simple-with-lock')


@pytest.mark.parametrize('cassette_name,offset,counter', [
    ('tests/fixtures/cassettes/api/pipeline/history-offset-0.yml', 0, 11),
    ('tests/fixtures/cassettes/api/pipeline/history-offset-10.yml', 10, 1)
])
def test_history(pipeline, cassette_name, offset, counter):
    with vcr.use_cassette(cassette_name) as _:
        response = pipeline.history(offset=offset)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert 'pipelines' in response.payload
    run = response.payload['pipelines'][0]
    assert run['name'] == 'Simple'
    assert run['counter'] == counter


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-successful.yml')
def test_release(locked_pipeline):
    response = locked_pipeline.release()

    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == 'pipeline lock released for {0}\n'.format(
        locked_pipeline.name
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-unsuccessful.yml')
def test_release_when_pipeline_is_unlocked(locked_pipeline):
    response = locked_pipeline.release()

    assert not response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == (
        'lock exists within the pipeline configuration but no pipeline '
        'instance is currently in progress\n'
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/pause-successful.yml')
def test_pause(pipeline):
    response = pipeline.pause('Time to sleep')

    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == ' '


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/unpause-successful.yml')
def test_unpause(pipeline):
    response = pipeline.unpause()

    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == ' '


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/status.yml')
def test_status(pipeline):
    response = pipeline.status()

    assert response.is_ok
    assert response.content_type == 'application/json'
    status = response.payload
    assert not status['locked']
    assert not status['paused']
    assert status['schedulable']

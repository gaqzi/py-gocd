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

    assert not response
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


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/instance.yml')
def test_instance(pipeline):
    response = pipeline.instance(1)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert response.payload['name'] == pipeline.name
    assert response.payload['counter'] == 1


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-successful-no-args.yml')
def test_schedule(pipeline):
    response = pipeline.schedule()

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == (
        'Request to schedule pipeline {0} accepted\n'.format(pipeline.name)
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-successful-with-arg.yml')
def test_schedule_with_git_arg(pipeline):
    git_revision = (
        '29f5d8ec63b7200d06a25f0b1df0e321bd95f1ec823d3ef8bac7c5295affa488'
    )
    # This feels bananas.
    # TODO: Check with Go devs what the format for all these material
    #       revs are, and how to figure it out
    # If this is it then I need to find a better way for users of this
    # library to interact with it, duplicating the revision isn't cool.
    response = pipeline.schedule(
        material_fingerprint={git_revision: git_revision}
    )

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == (
        'Request to schedule pipeline {0} accepted\n'.format(pipeline.name)
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-unsuccessful-when-already-running.yml')
def test_schedule_when_pipeline_is_already_running(pipeline):
    response = pipeline.schedule()

    assert response.status_code == 409
    assert not response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload == (
        'Failed to trigger pipeline [{pipeline}] {{ Stage [Hello] in '
        'pipeline [{pipeline}] is still in progress }}\n'
    ).format(pipeline=pipeline.name)

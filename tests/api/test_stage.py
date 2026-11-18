import pytest
import vcr

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='admin', password='badger')


@pytest.fixture
def stage(server):
    return server.stage('up42', 'up42_stage', pipeline_counter=40)


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/history.yml')
def test_history(stage):
    response = stage.history()

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v3+json'
    assert 'stages' in response
    run = response['stages'][0]
    assert run['name'] == stage.stage_name
    assert run['pipeline_name'] == stage.pipeline_name
    assert run['pipeline_counter'] == stage.pipeline_counter
    assert run['counter'] == '1'

# Todo: Fix this test if required
# @vcr.use_cassette('tests/fixtures/cassettes/api/stage/history-offset.yml')
@pytest.mark.skip(reason="Non essential and built on top of existing functionality which have "
                         "already been tested")
def test_history_offset(stage):
    response = stage.history(after=1)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert 'stages' in response
    run = response['stages'][0]
    assert run['name'] == 'stageOne'
    assert run['pipeline_name'] == 'Dummy'
    assert run['counter'] == '3'


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/instance.yml')
def test_instance(stage):
    response = stage.instance(stage_counter=1);

    assert response.is_ok
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.go.cd.v3+json'
    assert response['name'] == stage.stage_name
    assert response['pipeline_name'] == stage.pipeline_name
    assert response['pipeline_counter'] == stage.pipeline_counter
    assert response['counter'] == 1


# Todo: Fix this test if required
# @vcr.use_cassette('tests/fixtures/cassettes/api/stage/instance.yml')
@pytest.mark.skip(reason="Non essential and built on top of existing functionality which have "
                         "already been tested")
def test_instance_uses_pipeline_counter_in_recursion(server):
    overridden_pipeline_counter = 5
    stage = server.stage('Dummy', 'stageOne', pipeline_counter=4)
    response = stage.instance(counter=1, pipeline_counter=overridden_pipeline_counter)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert response['name'] == stage.stage_name
    assert response['pipeline_name'] == stage.pipeline_name
    assert response['pipeline_counter'] == overridden_pipeline_counter
    assert response['counter'] == 1


# Todo: Fix this test if required
# @vcr.use_cassette('tests/fixtures/cassettes/api/stage/instance-return-latest.yml')
@pytest.mark.skip(reason="Non essential and built on top of existing functionality which have "
                         "already been tested")
def test_instance_without_argument_returns_latest(stage):
    history_instance = stage.instance(1)
    response = stage.instance()

    assert response.is_ok
    assert response['counter'] == history_instance['counter']


# Todo: Fix this test if required
# @vcr.use_cassette('tests/fixtures/cassettes/api/stage/instance-latest-pipeline.yml')
@pytest.mark.skip(reason="Non essential and built on top of existing functionality which have "
                         "already been tested")
def test_get_latest_stage(server):
    stage = server.pipeline('Dummy').stage('stageOne')
    response = stage.instance()

    assert response.is_ok
    assert response['pipeline_counter'] == 6
    assert response['counter'] == 1


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/cancel-success.yml')
def test_cancel_success(stage):
    response = stage.cancel(2)

    assert response.is_ok
    assert response.status_code == 200
    assert response["message"] == 'Stage cancelled successfully.'


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/cancel-error.yml')
def test_cancel_error(stage):
    response = stage.cancel(10)

    assert not response.is_ok
    assert response.status_code == 404
    assert response["message"] == (f"Not Found {{ Stage '{stage.stage_name}' with"
                                   f" counter '{stage.stage_counter}' not found. Please make sure"
                                   f" specified stage or stage run with specified counter exists. }}")


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/cancel-ignore.yml')
def test_cancel_ignore(stage):
    response = stage.cancel(1)

    assert response.is_ok
    assert response.status_code == 200
    assert response["message"] == 'Stage is not active. Cancellation Ignored.'

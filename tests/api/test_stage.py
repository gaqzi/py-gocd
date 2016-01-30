import pytest
import vcr

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://192.168.99.100:8153')


@pytest.fixture
def stage(server):
    return server.stage('Dummy', 5, 'stageOne')


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/history.yml')
def test_history(stage):
    response = stage.history()

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert 'stages' in response
    run = response['stages'][0]
    assert run['name'] == 'stageOne'
    assert run['pipeline_name'] == 'Dummy'
    assert run['counter'] == '1'


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/history-offset.yml')
def test_history_offset(stage):
    response = stage.history(offset=5)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert 'stages' in response
    run = response['stages'][0]
    assert run['name'] == 'stageOne'
    assert run['pipeline_name'] == 'Dummy'
    assert run['counter'] == '3'


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/instance.yml')
def test_instance(stage):
    response = stage.instance(1)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert response['name'] == stage.stage_name
    assert response['pipeline_name'] == stage.pipeline_name
    assert response['pipeline_counter'] == stage.pipeline_counter
    assert response['counter'] == 1


@vcr.use_cassette('tests/fixtures/cassettes/api/stage/instance-return-latest.yml')
def test_instance_without_argument_returns_latest(stage):
    history_instance = stage.instance(1)
    response = stage.instance()

    assert response.is_ok
    assert response['counter'] == history_instance['counter']

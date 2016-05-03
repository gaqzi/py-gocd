import pytest
import vcr

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server('http://192.168.99.100:8153', user='bot', password='12345678')


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/get-successful.yml')
def test_get_existing(server):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")

    response = api_config.get()

    assert response.is_ok
    assert response.etag is not None
    assert response["name"] == "PyGoCd"
    assert response["template"] is None
    assert response["stages"][0]["name"] == "defaultStage"


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/get-missing.yml')
def test_get_missing(server):
    api_config = gocd.api.PipelineConfig(server, "MissingPipeline")

    response = api_config.get()

    assert not response.is_ok

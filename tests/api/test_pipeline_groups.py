import pytest
import vcr

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='ba', password='secret')


@pytest.fixture
def pipeline_groups(server):
    return server.pipeline_groups()


class TestPipelineGroups(object):
    def test_id_can_be_false(self, pipeline_groups):
        assert pipeline_groups.get_base_path() == pipeline_groups.base_path

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/small.yml')
    def test_get_pipeline_groups_returns_api_response(self, pipeline_groups):
        assert pipeline_groups.get_pipeline_groups().payload[0]['name'] == 'defaultGroup'

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/small.yml')
    def test_response_returns_api_response(self, pipeline_groups):
        assert pipeline_groups.response.payload[0]['name'] == 'defaultGroup'

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/small.yml')
    def test_pipelines_returns_a_list_of_all_pipeline_names(self, pipeline_groups):
        assert pipeline_groups.pipelines == set(['No-valid-agents'])

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/failed.yml')
    def test_pipelines_returns_false_if_invalid_response(self, pipeline_groups):
        assert not pipeline_groups.pipelines

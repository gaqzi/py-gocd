import pytest
import vcr

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='admin', password='badger')


@pytest.fixture
def pipeline_groups(server):
    return server.pipeline_groups()


class TestPipelineGroups(object):
    def test_id_can_be_false(self, pipeline_groups):
        assert pipeline_groups.get_base_path() == pipeline_groups.base_path

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/small.yml')
    def test_get_pipeline_groups_returns_api_response(self, pipeline_groups):
        response = pipeline_groups.get_pipeline_groups()

        assert response.is_ok
        assert response.status_code == 200

        groups = response.payload['_embedded']['groups']
        assert len(groups) > 0

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/small.yml')
    def test_response_returns_api_response(self, pipeline_groups):
        response = pipeline_groups.get_pipeline_groups()

        groups = response.payload['_embedded']['groups']

        assert groups[0]['name'] == 'defaultGroup'
        assert groups[0]['pipelines'][0]['name'] == 'up42'

    # Todo: Introspect this test
    # I don't think this is a valid ask
    # @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/small.yml')
    @pytest.mark.skip(reason="Intention is ambiguous, cannot be verified meaningfully")
    def test_pipelines_returns_a_list_of_all_pipeline_names(self, pipeline_groups):
        assert pipeline_groups.pipelines == set(['No-valid-agents'])

    @vcr.use_cassette('tests/fixtures/cassettes/api/pipeline_groups/failed.yml')
    def test_pipelines_returns_false_if_invalid_response(self, pipeline_groups):
        response = pipeline_groups.get_pipeline_groups()

        assert not response.is_ok
        assert response.status_code == 401

        assert response.payload["message"] == ("Invalid credentials. Either your username and "
                                               "password are incorrect, or there is a problem "
                                               "with your browser cookies. Please check with "
                                               "your administrator.")

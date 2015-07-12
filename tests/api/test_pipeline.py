import pytest
import vcr

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='ba', password='secret')


@pytest.fixture
def pipeline(server):
    return server.pipeline('Simple')


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

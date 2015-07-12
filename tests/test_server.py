import pytest
import vcr

from gocd.server import Server


@pytest.fixture
def server():
    return Server('http://localhost:8153', user='ba', password='secret')


def test_init_server():
    server = Server('http://localhost:8153', user='ba', password='secret')

    assert server.host == 'http://localhost:8153'
    assert server.user == 'ba'
    assert server.password == 'secret'


@vcr.use_cassette('tests/fixtures/cassettes/server-basic-auth.yml')
def test_ensure_it_can_handle_basic_auth(server):
    response = server.get('go/api/pipelines/Simple/history/0')

    assert response.code == 200
    assert response.headers.type == 'application/json'


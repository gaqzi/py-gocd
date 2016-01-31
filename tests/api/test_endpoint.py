import pytest

from gocd.api.endpoint import Endpoint


class TestEndpoint(object):
    def test_get_id_is_not_defined(self):
        endpoint = Endpoint()

        with pytest.raises(NotImplementedError):
            endpoint.get_id()

    def test_get_id_returns_set_id(self):
        endpoint = Endpoint()
        endpoint.id = 'name'
        endpoint.name = 'place'

        assert endpoint.get_id() == 'place'

    def test_get_base_path_is_not_defined(self):
        endpoint = Endpoint()

        with pytest.raises(NotImplementedError):
            endpoint.get_base_path()

    def test_get_base_path_returns_set_base_path(self):
        endpoint = Endpoint()
        endpoint.id = 'name'
        endpoint.name = 'place'
        endpoint.base_path = '/m000'

        assert endpoint.get_base_path() == '/m000'

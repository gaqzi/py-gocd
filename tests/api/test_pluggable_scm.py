import pytest
import vcr

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='bot', password='12345678')


@pytest.fixture
def scm_object():
    return {
        "id": "8c9a502a-67e0-41c5-8bbe-53c901055ac9",
        "name": "foobar",
        "auto_update": True,
        "plugin_metadata": {
            "id": "gocd.scm.material",
            "version": "1"
        },
        "configuration": [
            {
                "key": "BASE_URL",
                "value": "https://localhost"
            },
            {
                "key": "APP_NAME",
                "value": "Foobar"
            },
            {
                "key": "name",
                "value": "foobar"
            }
        ]
    }


@vcr.use_cassette('tests/fixtures/cassettes/api/pluggable_scm/list.yml')
def test_list(server):
    response = gocd.api.PluggableSCM(server).list()

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert isinstance(response["_embedded"]["scms"], list)


@vcr.use_cassette('tests/fixtures/cassettes/api/pluggable_scm/get-found.yml')
def test_get_found(server):
    name = "SCM-NAME"
    response = gocd.api.PluggableSCM(server, name).get()

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert "id" in response
    assert response["name"] == name
    assert isinstance(response["configuration"], list)


@vcr.use_cassette('tests/fixtures/cassettes/api/pluggable_scm/get-not-found.yml')
def test_get_not_found(server):
    name = "abcd-invalid"
    response = gocd.api.PluggableSCM(server, name).get()

    assert not response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert "message" in response


@vcr.use_cassette('tests/fixtures/cassettes/api/pluggable_scm/create.yml')
def test_create(server, scm_object):
    response = gocd.api.PluggableSCM(server, scm_object["name"]).create(scm_object)

    # exclude for comparison
    response_dict = response.payload
    del response_dict["_links"]

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert scm_object == response_dict


@vcr.use_cassette('tests/fixtures/cassettes/api/pluggable_scm/edit-success.yml')
def test_edit_success(server, scm_object):
    etag = '"483ba431cc141323e3c7c00c944d4878"'
    response = gocd.api.PluggableSCM(server, scm_object["name"]).edit(scm_object, etag)

    # exclude for comparison
    response_dict = response.payload
    del response_dict["_links"]

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert scm_object == response_dict


@vcr.use_cassette('tests/fixtures/cassettes/api/pluggable_scm/edit-fail.yml')
def test_edit_fail(server, scm_object):
    etag = "invalid"
    response = gocd.api.PluggableSCM(server, scm_object["name"]).edit(scm_object, etag)

    assert not response.is_ok

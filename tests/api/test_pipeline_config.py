import pytest
import vcr
import copy

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='admin', password='badger')


@pytest.fixture
def pipeline_json():
    return {
        "label_template": "${COUNT}",
        "enable_pipeline_locking": False,
        "name": "PyGoCd",
        "template": None,
        "parameters": [],
        "environment_variables": [],
        "materials": [
            {
                "type": "git",
                "attributes": {
                    "url": "https://github.com/gaqzi/py-gocd.git",
                    "destination": None,
                    "filter": None,
                    "name": None,
                    "auto_update": True,
                    "branch": "master",
                    "submodule_folder": None,
                    "shallow_clone": True
                }
            }
        ],
        "stages": [
            {
                "name": "defaultStage",
                "fetch_materials": True,
                "clean_working_directory": False,
                "never_cleanup_artifacts": False,
                "approval": {
                    "type": "success",
                    "authorization": {
                        "roles": [],
                        "users": []
                    }
                },
                "environment_variables": [],
                "jobs": [
                    {
                        "name": "defaultJob",
                        "run_instance_count": None,
                        "timeout": None,
                        "environment_variables": [],
                        "resources": [],
                        "tasks": [
                            {
                                "type": "exec",
                                "attributes": {
                                    "run_if": [],
                                    "on_cancel": None,
                                    "command": "make",
                                    "arguments": [
                                        "pre-commit"
                                    ],
                                    "working_directory": None
                                }
                            }
                        ],
                        "tabs": [],
                        "artifacts": [],
                        "properties": None
                    }
                ]
            }
        ],
        "tracking_tool": None,
        "timer": None
    }


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/get-successful.yml')
def test_get_existing(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")

    response = api_config.get()

    assert response.is_ok
    assert response.etag is not None

    response_body = copy.copy(response.body)
    del response_body["_links"]
    assert response_body == pipeline_json

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/get-unauthorised.yml')
def test_get_existing_unauthorised(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")

    response = api_config.get()

    assert not response.is_ok
    assert response.status_code == 401
    assert response.content_type == "application/vnd.go.cd.v1+json"

    payload = response.payload
    assert "message" in payload
    assert "not authorized" in payload["message"].lower()

    assert "_links" not in payload
    assert "name" not in payload

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/get-missing.yml')
def test_get_missing(server):
    api_config = gocd.api.PipelineConfig(server, "MissingPipeline")

    response = api_config.get()

    assert not response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/edit-successful.yml')
def test_edit_successful(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")
    etag = '"6b60a77d27312e3a21bfd59163db1e48"'
    pipeline_json["materials"][0][
        "attributes"]["url"] = "https://github.com/henriquegemignani/py-gocd.git"

    response = api_config.edit(pipeline_json, etag)

    assert response.is_ok

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/edit-unauthorised.yml')
def test_edit_unauthorised(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")
    etag = '"6b60a77d27312e3a21bfd59163db1e48"'
    pipeline_json["materials"][0][
        "attributes"]["url"] = "https://github.com/henriquegemignani/py-gocd.git"

    response = api_config.edit(pipeline_json, etag)

    assert not response.is_ok
    assert response.status_code == 401
    assert response.content_type == "application/vnd.go.cd.v1+json"

    payload = response.payload

    assert len(payload) == 1
    assert payload == {
        "message": "You are not authorized to access this resource!"
    }

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/edit-error.yml')
def test_edit_error(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")
    etag = 'invalid etag'

    response = api_config.edit(pipeline_json, etag)

    assert not response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/create-successful.yml')
def test_create_successful(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd-Copy")
    pipeline_json["name"] = "PyGoCd-Copy"
    pipeline_json["group"] = "Tools"

    response = api_config.create(pipeline_json)

    assert response.is_ok

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/create-unauthorised.yml')
def test_create_unauthorised(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd-Copy-UnAuth")

    pipeline_json["name"] = "PyGoCd-Copy-UnAuth"
    pipeline_json["group"] = "Tools"

    response = api_config.create(pipeline_json)

    assert not response.is_ok
    assert response.status_code == 401
    assert response.content_type == "application/vnd.go.cd.v1+json"

    payload = response.payload

    assert len(payload) == 1
    assert "message" in payload
    assert "not authorized" in payload["message"].lower()

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/create-error.yml')
def test_create_error(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")
    pipeline_json["group"] = "Tools"

    response = api_config.create(pipeline_json)

    assert not response.is_ok
    assert response.body["message"] == "You are not authorized to access this resource!"

@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/create-pipeline-error.yml')
def test_create_error(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")
    pipeline_json["group"] = "Tools"

    response = api_config.create(pipeline_json)

    assert not response.is_ok
    assert response.body["message"] == "Failed to create pipeline 'PyGoCd' as another pipeline by the same name already exists."

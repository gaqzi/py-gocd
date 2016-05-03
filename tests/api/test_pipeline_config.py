import pytest
import vcr
import copy

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server('http://192.168.99.100:8153', user='bot', password='12345678')


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


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline-config/get-missing.yml')
def test_get_missing(server):
    api_config = gocd.api.PipelineConfig(server, "MissingPipeline")

    response = api_config.get()

    assert not response.is_ok


def test_edit_successful(server, pipeline_json):
    api_config = gocd.api.PipelineConfig(server, "PyGoCd")
    pipeline_json["materials"][0]["attributes"]["url"] = "https://github.com/henriquegemignani/py-gocd.git"

    response = api_config.get()
    response = api_config.edit({}, response.etag)

    assert response.is_ok

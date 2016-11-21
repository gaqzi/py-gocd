import pytest
import vcr
import copy

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server("http://127.0.0.1:8153", user=None, password=None)


@pytest.fixture
def template_json():
    return {
        "name": "MyTemplate",
        "stages": [
            {
                "environment_variables": [],
                "jobs": [
                    {
                        "environment_variables": [],
                        "artifacts": [],
                        "timeout": None,
                        "tabs": [],
                        "resources": [
                            "resource1"
                        ],
                        "properties": None,
                        "run_instance_count": None,
                        "tasks": [
                            {
                                "attributes": {
                                    "run_if": [
                                        "passed"
                                    ],
                                    "command": "/bin/bash",
                                    "on_cancel": None,
                                    "working_directory": None,
                                    "arguments": [
                                        "-c",
                                        "echo i am a default job"
                                    ]
                                },
                                "type": "exec"
                            }
                        ],
                        "name": "defaultJob"
                    }
                ],
                "never_cleanup_artifacts": False,
                "approval": {
                    "authorization": {
                        "roles": [],
                        "users": []
                    },
                    "type": "success"
                },
                "fetch_materials": True,
                "name": "defaultStage",
                "clean_working_directory": False},
            {
                "environment_variables": [
                    {
                        "name": "ENV_VAR1",
                        "value": "value1",
                        "secure": False
                    }
                ],
                "jobs": [
                    {
                        "environment_variables": [],
                        "artifacts": [],
                        "timeout": None,
                        "tabs": [],
                        "resources": [],
                        "properties": None,
                        "run_instance_count": None,
                        "tasks": [
                            {
                                "attributes": {
                                    "run_if": [],
                                    "command": "/bin/bash",
                                    "on_cancel": None,
                                    "working_directory": None,
                                    "arguments": [
                                        "-c",
                                        "echo i am a post job"
                                    ]
                                },
                                "type": "exec"
                            }
                        ],
                        "name": "PostJob"
                    }
                ],
                "never_cleanup_artifacts": False,
                "approval": {
                    "authorization": {
                        "roles": [],
                        "users": []
                    },
                    "type": "success"
                },
                "fetch_materials": True,
                "name": "PostStage",
                "clean_working_directory": False
            }
        ]
    }


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/get-successful.yml')
def test_get_existing(server, template_json):
    api_config = gocd.api.TemplateConfig(server, "MyTemplate")

    response = api_config.get()

    assert response.is_ok
    assert response.etag is not None

    response_body = copy.copy(response.body)
    del response_body["_links"]
    assert response_body == template_json


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/get-missing.yml')
def test_get_missing(server):
    api_config = gocd.api.TemplateConfig(server, "MissingTemplate")

    response = api_config.get()

    assert not response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/edit-successful.yml')
def test_edit_successful(server, template_json):
    api_config = gocd.api.TemplateConfig(server, "MyTemplate")
    etag = '"daee15ed82d2286d7a5956a6c88f5069"'
    template_json["stages"][0]["environment_variables"] = [
        {
            "name": "NEW_VAR",
            "value": "NEW_VALUE",
            "secure": False
        }
    ]

    response = api_config.edit(template_json, etag)

    assert response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/edit-error.yml')
def test_edit_error(server, template_json):
    api_config = gocd.api.TemplateConfig(server, "MyTemplate")
    etag = 'invalid etag'

    response = api_config.edit(template_json, etag)

    assert not response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/create-successful.yml')
def test_create_successful(server, template_json):
    api_config = gocd.api.TemplateConfig(server, "MyTemplateCreated")
    template_json["name"] = "MyTemplateCreated"

    response = api_config.create(template_json)

    assert response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/create-error.yml')
def test_create_error(server, template_json):
    api_config = gocd.api.TemplateConfig(server, "MyTemplate")

    response = api_config.create(template_json)

    assert not response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/delete-successful.yml')
def test_delete_successful(server):
    api_config = gocd.api.TemplateConfig(server, "MyTemplate")

    response = api_config.delete()

    assert response.is_ok


@vcr.use_cassette('tests/fixtures/cassettes/api/template-config/delete-error.yml')
def test_create_error(server):
    api_config = gocd.api.TemplateConfig(server, "MyTemplateThatDoesntExist")

    response = api_config.delete()

    assert not response.is_ok

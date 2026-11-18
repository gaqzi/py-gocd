import pytest
import vcr

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='admin', password='badger')


@pytest.fixture
def pipeline(server):
    return server.pipeline('up42')


@pytest.fixture
def locked_pipeline(server):
    return server.pipeline('up42')


@pytest.fixture
def pipeline_multiple_stages(server):
    return server.pipeline('up42')


@pytest.fixture
def pipeline_multiple_stages_manual(server):
    return server.pipeline('up42')


@pytest.mark.parametrize('cassette_name,page_size,expected_counter', [
    ('tests/fixtures/cassettes/api/pipeline/history-page-default.yml', 0, 12),
])
def test_history(pipeline, cassette_name, page_size, expected_counter):
    with vcr.use_cassette(cassette_name):
        response = pipeline.history(page_size=page_size)

    payload = response.payload

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'

    assert 'pipelines' in payload
    assert isinstance(payload["pipelines"], list)

    assert "_links" in payload

    run = response['pipelines'][0]
    assert run['name'] == 'up42'
    assert run['counter'] == expected_counter


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-successful.yml')
def test_release(locked_pipeline):
    response = locked_pipeline.release()

    assert response.is_ok
    assert response.content_type == "application/vnd.go.cd.v1+json"
    assert response.payload["message"] == f"Pipeline lock released for {locked_pipeline.name}"


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-when-pipeline-is-running.yml')
def test_release_when_pipeline_is_running(locked_pipeline):
    response = locked_pipeline.release()

    assert not response.is_ok
    assert response.content_type == "application/vnd.go.cd.v1+json"
    assert response.payload["message"] == ("Locked pipeline instance is currently running (one of "
                                           "the stages is in progress)")


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-unsuccessful.yml')
def test_release_when_pipeline_is_unlocked(locked_pipeline):
    response = locked_pipeline.release()

    assert not response.is_ok
    assert response.content_type == "application/vnd.go.cd.v1+json"
    assert response.payload["message"] == ("Lock exists within the pipeline configuration but no "
                                           "pipeline instance is currently in progress")


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/pause-successful.yml')
def test_pause_successful(pipeline):
    response = pipeline.pause('Time to sleep')

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response.payload["message"] == f"Pipeline '{pipeline.name}' paused successfully."


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/pause-unsuccessful.yml')
def test_pause_unsuccessful(pipeline):
    response = pipeline.pause('Time to sleep')

    assert not response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response.payload[
               "message"] == f"Failed to pause pipeline '{pipeline.name}'. Pipeline '{pipeline.name}' is already paused."


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/unpause-successful.yml')
def test_unpause_successful(pipeline):
    response = pipeline.unpause()

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response.payload["message"] == f"Pipeline '{pipeline.name}' unpaused successfully."


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/unpause-unsuccessful.yml')
def test_unpause_unsuccessful(pipeline):
    response = pipeline.unpause()

    assert not response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response.payload["message"] == (f"Failed to unpause pipeline '{pipeline.name}'. "
                                           f"Pipeline '{pipeline.name}' is already unpaused.")


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/status_when_schedulable.yml')
def test_status_when_schedulable(pipeline):
    response = pipeline.status()

    payload = response.payload

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'

    assert payload['schedulable'] is True
    assert payload['paused'] is False
    assert len(payload['paused_cause']) is 0
    assert payload['locked'] is False


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/status_when_paused.yml')
def test_status_when_paused(pipeline):
    response = pipeline.status()

    payload = response.payload

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'

    assert payload['paused'] is True
    assert len(payload['paused_cause']) > 0
    assert payload['schedulable'] is False
    assert payload['locked'] is False


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/status_when_locked.yml')
def test_status_when_locked(pipeline):
    response = pipeline.status()

    payload = response.payload

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'

    assert payload['locked'] is True
    assert payload['paused'] is False
    assert len(payload['paused_cause']) is 0
    assert payload['schedulable'] is False


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/instance.yml')
def test_instance(pipeline):
    response = pipeline.instance(23)

    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response['name'] == pipeline.name
    assert response['counter'] == 23


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/instance-zero-pipeline-counter.yml')
def test_instance_without_argument_returns_latest(pipeline):
    response = pipeline.instance()

    assert not response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response.payload["message"] == ("Your request could not be processed. The pipeline "
                                           "counter cannot be less than 1.")


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-successful-no-args.yml')
def test_schedule(pipeline):
    response = pipeline.schedule()

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert response.payload["message"] == f"Request to schedule pipeline {pipeline.name} accepted"


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-successful-with-material.yml')
def test_schedule_with_git_arg(pipeline):
    git_revision = (
        '29f5d8ec63b7200d06a25f0b1df0e321bd95f1ec823d3ef8bac7c5295affa488'
    )
    # This feels bananas.
    # TODO: Check with Go devs what the format for all these material
    #       revs are, and how to figure it out
    # If this is it then I need to find a better way for users of this
    # library to interact with it, duplicating the revision isn't cool.
    response = pipeline.schedule(materials={git_revision: git_revision})

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == (
        'Request to schedule pipeline {0} accepted\n'.format(pipeline.name)
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-successful-with-env-var.yml')
def test_schedule_with_environment_variable_passed(pipeline):
    response = pipeline.schedule(variables=dict(UPSTREAM_REVISION='42'))

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == (
        'Request to schedule pipeline {0} accepted\n'.format(pipeline.name)
    )


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/schedule-successful-with-secure-env-var.yml'
)
def test_schedule_with_secure_environment_variable_passed(pipeline):
    response = pipeline.schedule(secure_variables=dict(UPLOAD_PASSWORD='ssh, not so loud'))

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == (
        'Request to schedule pipeline {0} accepted\n'.format(pipeline.name)
    )


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/schedule-unsuccessful-when-already-running.yml'
)
def test_schedule_when_pipeline_is_already_running(pipeline):
    response = pipeline.schedule()

    assert response.status_code == 409
    assert not response.is_ok
    assert response.content_type == "application/vnd.go.cd.v1+json"
    assert response.payload["message"] == (f"Failed to trigger pipeline [{pipeline.name}]"
                                           " { Stage [up42_stage]"
                                           " in pipeline [up42] is still in progress }")


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/schedule-successful-and-return-new-instance.yml'
)
def test_schedule_pipeline_and_return_new_instance(pipeline):
    before_run = pipeline.history()['pipelines'][0]
    # By setting the backoff to 0 the test runs faster, since it's all mocked out anyway.
    response = pipeline.schedule(return_new_instance=True, maximum_backoff_time=100)

    assert response.is_ok
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.go.cd.v1+json'
    assert before_run['counter'] == 88
    assert response.payload['counter'] != before_run['counter']
    assert (before_run['counter'] + 1) == response['counter']


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/console-output.yml')
def test_console_output_single_stage(pipeline):
    instance = pipeline.instance(40)
    metadata, output = next(pipeline.console_output(instance))

    assert r'[go] Job completed' in output.decode('utf8')
    assert {'pipeline': 'up42',
            'pipeline_counter': instance['counter'],
            'stage': 'up42_stage',
            'stage_counter': '1',
            'job': 'up42_job',
            'job_result': 'Failed',
            } == metadata


# To-do: Remove the asserts and fix the logic
@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/console-output-multiple-stages.yml')
def test_console_output_multiple_stages(pipeline_multiple_stages):
    pipeline = pipeline_multiple_stages

    valid_args = ['Good Bye', 'Hello', 'ehlo test.somewhere.tld']
    valid = 0
    for metadata, output in pipeline.console_output(pipeline.instance(40)):
        output = output.decode('utf8')
        assert r'[go] Job completed' in output
        # assert True in (
        #     '<arg>{0}</arg>'.format(job) in output for job in valid_args
        # ), 'No match for {0}'.format(metadata)
        valid += 1

    # assert valid == 3


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/console-output-job-not-finished.yml')
def test_console_output_only_where_stage_has_finished(pipeline_multiple_stages_manual):
    # The second stage has been scheduled but has no agent to run on, so the only output in
    # the console.log is that there's no console.log To avoid showing that message it'll only
    # output if the pipeline has gotten into a finalized state.
    pipeline = pipeline_multiple_stages_manual

    jobs_with_output = set()
    for metadata, output in pipeline.console_output(pipeline.instance(40)):
        if output:
            jobs_with_output.add(metadata['job'])

    assert 'Ehlo' not in jobs_with_output
    assert 'up42_job' in jobs_with_output
    assert 'up42_job' in jobs_with_output


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/stage.yml'
)
def test_get_stage_for_a_pipeline(pipeline):
    stage = pipeline.stage('Hello')

    assert isinstance(stage, gocd.api.Stage)
    assert stage.pipeline_name == pipeline.name
    assert stage.stage_name == 'Hello'

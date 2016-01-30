import pytest
import vcr

import gocd
import gocd.api


@pytest.fixture
def server():
    return gocd.Server('http://localhost:8153', user='ba', password='secret')


@pytest.fixture
def pipeline(server):
    return server.pipeline('Simple')


@pytest.fixture
def locked_pipeline(server):
    return server.pipeline('Simple-with-lock')


@pytest.fixture
def pipeline_multiple_stages(server):
    return server.pipeline('Multiple-Stages-And-Jobs')


@pytest.fixture
def pipeline_multiple_stages_manual(server):
    return server.pipeline('Multiple-Stages-And-Jobs-Manual')


@pytest.mark.parametrize('cassette_name,offset,counter', [
    ('tests/fixtures/cassettes/api/pipeline/history-offset-0.yml', 0, 11),
    ('tests/fixtures/cassettes/api/pipeline/history-offset-10.yml', 10, 1)
])
def test_history(pipeline, cassette_name, offset, counter):
    with vcr.use_cassette(cassette_name):
        response = pipeline.history(offset=offset)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert 'pipelines' in response
    run = response['pipelines'][0]
    assert run['name'] == 'Simple'
    assert run['counter'] == counter


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-successful.yml')
def test_release(locked_pipeline):
    response = locked_pipeline.release()

    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == 'pipeline lock released for {0}\n'.format(
        locked_pipeline.name
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/release-unsuccessful.yml')
def test_release_when_pipeline_is_unlocked(locked_pipeline):
    response = locked_pipeline.release()

    assert not response
    assert not response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == (
        'lock exists within the pipeline configuration but no pipeline '
        'instance is currently in progress\n'
    )


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/pause-successful.yml')
def test_pause(pipeline):
    response = pipeline.pause('Time to sleep')

    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == ' '


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/unpause-successful.yml')
def test_unpause(pipeline):
    response = pipeline.unpause()

    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == ' '


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/status.yml')
def test_status(pipeline):
    response = pipeline.status()

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert not response['locked']
    assert not response['paused']
    assert response['schedulable']


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/instance.yml')
def test_instance(pipeline):
    response = pipeline.instance(1)

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert response['name'] == pipeline.name
    assert response['counter'] == 1


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/instance-return-latest.yml')
def test_instance_without_argument_returns_latest(pipeline):
    history_instance = pipeline.history()['pipelines'][0]
    response = pipeline.instance()

    assert response.is_ok
    assert response['counter'] == history_instance['counter']


@vcr.use_cassette('tests/fixtures/cassettes/api/pipeline/schedule-successful-no-args.yml')
def test_schedule(pipeline):
    response = pipeline.schedule()

    assert response.status_code == 202
    assert response.is_ok
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == (
        u'Request to schedule pipeline {0} accepted\n'.format(pipeline.name)
    )


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
    assert response.content_type == 'text/html'
    assert response.payload.decode('utf-8') == (
        'Failed to trigger pipeline [{pipeline}] {{ Stage [Hello] in '
        'pipeline [{pipeline}] is still in progress }}\n'
    ).format(pipeline=pipeline.name)


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/schedule-successful-and-return-new-instance.yml'
)
def test_schedule_pipeline_and_return_new_instance(pipeline):
    before_run = pipeline.history()['pipelines'][0]
    # By setting the backoff to 0 the test runs faster, since it's all mocked out anyway.
    response = pipeline.schedule(return_new_instance=True, backoff_time=0)

    assert response.status_code == 200
    assert response.is_ok
    assert response.content_type == 'application/json'
    assert response['counter'] != before_run['counter']
    assert (before_run['counter'] + 1) == response['counter']


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/console-output.yml'
)
def test_console_output_single_stage(pipeline):
    instance = pipeline.instance()
    metadata, output = next(pipeline.console_output(instance))

    assert r'[go] Job completed' in output.decode('utf8')
    assert {'pipeline': 'Simple',
            'pipeline_counter': instance['counter'],
            'stage': 'defaultStage',
            'stage_counter': '1',
            'job': 'defaultJob',
            'job_result': 'Passed',
            } == metadata


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/console-output-multiple-stages.yml'
)
def test_console_output_multiple_stages(pipeline_multiple_stages):
    pipeline = pipeline_multiple_stages

    valid_args = ['Good Bye', 'Hello', 'ehlo test.somewhere.tld']
    valid = 0
    for metadata, output in pipeline.console_output():
        output = output.decode('utf8')
        assert r'[go] Job completed' in output
        assert True in (
            '<arg>{0}</arg>'.format(job) in output for job in valid_args
        ), 'No match for {0}'.format(metadata)
        valid += 1

    assert valid == 3


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/console-output-job-not-finished.yml'
)
def test_console_output_only_where_stage_has_finished(pipeline_multiple_stages_manual):
    # The second stage has been scheduled but has no agent to run on, so the only output in
    # the console.log is that there's no console.log To avoid showing that message it'll only
    # output if the pipeline has gotten into a finalized state.
    pipeline = pipeline_multiple_stages_manual

    jobs_with_output = set()
    for metadata, output in pipeline.console_output():
        if output:
            jobs_with_output.add(metadata['job'])

    assert 'Ehlo' not in jobs_with_output
    assert 'Hello' in jobs_with_output
    assert 'Bye' in jobs_with_output


@vcr.use_cassette(
    'tests/fixtures/cassettes/api/pipeline/stage.yml'
)
def test_get_stage_for_a_pipeline(pipeline):
    stage = pipeline.stage('Hello')

    assert isinstance(stage, gocd.api.Stage)
    assert stage.pipeline_name == pipeline.name
    assert stage.stage_name == 'Hello'

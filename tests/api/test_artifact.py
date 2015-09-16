import pytest
import vcr
import zipfile
import io
import time

import gocd


@pytest.fixture
def server():
    return gocd.Server('http://192.168.24.67:32769')


@pytest.fixture
def artifact(server):
    return gocd.api.Artifact(server, "Art", 2, "defaultStage", "defaultJob", 3)


@vcr.use_cassette('tests/fixtures/cassettes/api/artifact/list.yml')
def test_release(artifact):
    response = artifact.list()

    assert response.is_ok
    assert response.content_type == 'application/json'
    assert len(response.payload) == 3
    assert set(x["name"] for x in response) == set(["cruise-output", "foo", "output.txt"])
    foo = next(x for x in response if x["name"] == "foo")
    assert len(foo["files"]) == 2


@pytest.mark.parametrize('cassette_name,path_to_file, expected_content', [
    ('tests/fixtures/cassettes/api/artifact/get-output.yml', "output.txt", "3239273"),
    ('tests/fixtures/cassettes/api/artifact/get-foo-a.yml', "foo/a.txt", "5933126")
])
def test_get(artifact, cassette_name, path_to_file, expected_content):
    with vcr.use_cassette(cassette_name):
        response = artifact.get(path_to_file)

    assert response.code == 200
    assert response.read() == expected_content


@vcr.use_cassette('tests/fixtures/cassettes/api/artifact/get_directory.yml')
def test_get_directory(artifact):
    for i in xrange(10):
        response = artifact.get_directory("foo")
        if response.code != 202:
            break
        time.sleep(0.1)

    assert response.code == 200

    file_like_object = io.BytesIO(response.read())
    zip_file = zipfile.ZipFile(file_like_object)
    assert set(['foo/', 'foo/a.txt', 'foo/b.txt']) == set(zip_file.namelist())

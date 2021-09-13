import pytest
import json

from fastapi.testclient import TestClient

from thor.main import app

client = TestClient(app)


with open("release_test_data.txt", "r") as read_release_test:
    expected_output_for_get_releases = json.load(read_release_test)

with open("task_test_data.txt", "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)


def test_read_releases():
    response = client.get("/releases")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_releases


@pytest.mark.parametrize("release_id", [3, 4])
def test_read_single_release(release_id):
    response = client.get(f"/releases/{release_id}")
    assert response.status_code == 200
    if release_id == 3:
        # convert py dictionary to json string
        release3_payload = json.dumps(expected_output_for_get_releases["releases"][0])
        expected_output_for_get_release = f'{{ "release": {release3_payload} }}'
    elif release_id == 4:
        release4_payload = json.dumps(expected_output_for_get_releases["releases"][1])
        expected_output_for_get_release = f'{{ "release": {release4_payload} }}'
    # convert json string back to json object for comparison
    assert response.json() == json.loads(expected_output_for_get_release)


def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_tasks

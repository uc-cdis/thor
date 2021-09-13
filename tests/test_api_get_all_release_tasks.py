import pytest
import json

from fastapi.testclient import TestClient

from thor.main import app

client = TestClient(app)


with open("task_test_data.txt", "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)


@pytest.mark.parametrize("release_id", [3, 4])
def test_get_all_release_tasks(release_id):
    response = client.get(f"/releases/{release_id}/tasks")
    assert response.status_code == 200

    list_of_desired_tasks = [
        task
        for task in expected_output_for_get_tasks["tasks"]
        if task["release_id"] == release_id
    ]

    expected_output_for_get_all_release_tasks = (
        f'{{ "release": {json.dumps(list_of_desired_tasks)} }}'
    )

    print(response.json)
    assert response.json() == json.load(expected_output_for_get_all_release_tasks)

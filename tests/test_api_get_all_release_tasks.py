import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app

client = TestClient(app)


test_data_file_name = "tests/test_files/task_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)


@pytest.mark.parametrize("release_id", [3, 4])
def test_get_all_release_tasks(release_id):
    # Note: release_id instead of release name does not conform
    # to the pattern established elsewhere, 
    # but that's the state of the code so far. 
    response = client.get(f"/releases/{release_id}/tasks")
    assert response.status_code == 200

    list_of_desired_tasks = [
        task
        for task in expected_output_for_get_tasks["tasks"]
        if task["release_id"] == release_id
    ]

    expected_output_for_get_all_release_tasks = json.dumps(
        {"release_tasks": list_of_desired_tasks}
    )

    assert response.json() == json.loads(expected_output_for_get_all_release_tasks)

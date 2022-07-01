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

release_task_id_list = [
    [task["release_id"], task["task_id"]]
    for task in expected_output_for_get_tasks["tasks"]
]


@pytest.mark.parametrize("release_task_id", release_task_id_list)
def test_get_release_task_specific(release_task_id):
    release_id = release_task_id[0]
    task_id = release_task_id[1]

    response = client.get(f"/releases/{release_id}/tasks/{task_id}")
    assert response.status_code == 200

    # creates a dictionary associating each release with its numerical release id
    tasks_dict_byID = {
        task["task_id"]: task for task in expected_output_for_get_tasks["tasks"]
    }

    expected_output_for_get_release_task_specific = json.dumps(
        {"release_task": [tasks_dict_byID[task_id]]}
    )

    # convert json string back to json object for comparison
    assert response.json() == json.loads(expected_output_for_get_release_task_specific)

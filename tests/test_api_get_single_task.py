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


@pytest.mark.parametrize("task_id", range(1, 11))
def test_read_single_task(task_id):
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

    # creates a dictionary associating each release with its numerical release id
    tasks_dict_byID = {
        task["task_id"]: task for task in expected_output_for_get_tasks["tasks"]
    }

    expected_output_for_get_task = (
        f'{{ "task": {json.dumps(tasks_dict_byID[task_id])} }}'
    )

    # convert json string back to json object for comparison
    assert response.json() == json.loads(expected_output_for_get_task)

import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient
from thor.dao.clear_tables_reseed import reseed
from thor.dao.release_dao import release_id_lookup_class
from thor.main import app

client = TestClient(app)


test_data_file_name = "tests/test_files/task_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)


@pytest.mark.parametrize("release_name", ["2021.09", "2021.07"])
def test_get_all_release_tasks(release_name):
    reseed()

    rid_lookupper = release_id_lookup_class()
    release_id = rid_lookupper.release_id_lookup(release_name)

    response = client.get(f"/releases/{release_name}/tasks")
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

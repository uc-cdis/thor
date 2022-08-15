import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient
from thor.dao.clear_tables_reseed import reseed

from thor.main import app

client = TestClient(app)


test_data_file_name = "tests/test_files/task_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)
    task_list = expected_output_for_get_tasks["tasks"]

# Apologies for the hardcoding, but I'm not sure if it's worth it 
# to formalize this in some file. 
release_id_name_dict = {3: "2021.09", 4: "2021.07"}

def test_get_all_tasks():
    reseed()
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_tasks

@pytest.mark.parametrize("task", task_list)
def test_get_single_from_all(task):
    reseed()
    release_name = release_id_name_dict[task["release_id"]]
    step_num = task["step_num"]
    response = client.get(f"/releases/{release_name}/tasks/{step_num}")
    assert response.status_code == 200
    assert response.json() == {"task": task}

@pytest.mark.parametrize("release_name", ["2021.07", "2021.09"])
def test_all_for_release_from_all(release_name):
    reseed()
    response = client.get("/tasks", params = {"release_name": release_name})
    assert response.status_code == 200

    release_id = next(key for key, value in release_id_name_dict.items() if value == release_name)

    list_of_desired_tasks = [
        task
        for task in expected_output_for_get_tasks["tasks"]
        if task["release_id"] == release_id
    ]

    expected_output_for_get_all_release_tasks = json.dumps(
        {"release_tasks": list_of_desired_tasks}
    )

    assert response.json() == json.loads(expected_output_for_get_all_release_tasks)

def test_get_single_from_all_failing():
    reseed()

    # If the release_name does not exist, the response should be 404
    # Similarly, if the step_num does not exist, the response should be 404
    
    # Failing because the step_num cannot exist
    response = client.get("/tasks", params = {"release_name": "2021.09", "step_num": 1000})
    assert response.status_code == 404

    # Failing because the release_name cannot exist
    response = client.get("/tasks", params = {"release_name": "2000.09", "step_num": 1})
    assert response.status_code == 404

    # Failing because release_name not given
    response = client.get("/tasks", params = {"step_num": "1"})
    assert response.status_code == 400

    # The below test is now acceptable as expected behavior. 
    # # Failing because step_num not given
    # response = client.get("/tasks", params = {"release_name": "2021.09"})
    # assert response.status_code == 400
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.release_dao import release_id_lookup_class

client = TestClient(app)

test_data_file_name = "tests/test_files/task_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)

# Apologies for the hardcoding, but I'm not sure if it's worth it 
# to formalize this in some file. 
release_id_name_dict = {3: "2021.09", 4: "2021.07"}

@pytest.mark.parametrize("task_dict", expected_output_for_get_tasks["tasks"])
def test_get_release_task_specific(task_dict):

    release_id = task_dict["release_id"]
    release_name = release_id_name_dict[release_id]
    step_num = task_dict["step_num"]

    response = client.get(f"/releases/{release_name}/tasks/{step_num}")
    assert response.status_code == 200
    assert response.json() == {"task": task_dict}

failing_pairs = [
    ("invalid_release", 1), 
    ("2021.09", -1),
    ("invalid release", -1)
]

@pytest.mark.parametrize("release_name, step_num", failing_pairs)
def test_get_release_task_specific_failing(release_name, step_num):
    response = client.get(f"/releases/{release_name}/tasks/{step_num}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"No task found for release with name {release_name} and step_num {step_num}."}

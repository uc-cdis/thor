from platform import release
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed
from thor.dao.release_dao import release_id_lookup_class
from thor.dao.task_dao import get_release_task_step

client = TestClient(app)

test_data_file_name = "tests/test_files/post_release_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as post_release_test:
    expected_output_for_post_release = json.load(post_release_test)


@pytest.mark.parametrize("release_name, step_num, status", 
[("2021.09", 1, "SUCCESS"), ("2021.09", 3, "FAILURE"), ("2021.07", 4, "PENDING")])
def test_put_task_status(release_name, step_num, status):
    reseed()
    put_response = client.put(f"/thor-admin/releases/{release_name}/tasks/{step_num}", json={"status": status}, headers={"Content-Type": "application/json"})
    assert put_response.status_code == 200
    assert put_response.json() == {
        "release_name": release_name, "step_num": step_num, "status": status
        }

    # Testing status in database as well:
    get_response = client.get(f"/releases/{release_name}/tasks/{step_num}")
    assert get_response.status_code == 200
    release_id = release_id_lookup_class().release_id_lookup(release_name)
    # print(get_release_task_step(release_name, step_num), release_name, step_num, type(release_id), type(step_num))
    current_task = get_release_task_step(release_name, step_num)
    task_id = current_task.task_id
    task_name = current_task.task_name
    assert get_response.json() == {
        "task": {
            "task_name": task_name, 
            "release_id": release_id,
            "status": status,
            "task_id": task_id,
            "step_num": step_num
            }
        }

@pytest.mark.parametrize("release_name, step_num", [("invalid_release", 1), ("2021.09", -1), ("invalid release", -1)])
def test_put_task_status_failing(release_name, step_num):
    reseed()
    put_response = client.put(f"/thor-admin/releases/{release_name}/tasks/{step_num}", json={"status": "SUCCESS"}, headers={"Content-Type": "application/json"})
    assert put_response.status_code == 422
    assert put_response.json() == {
        "detail": [{
            "loc":["body","release_name"],
            "msg": f"No task with step_num {step_num} and release_name {release_name} exists."
        }]
    }
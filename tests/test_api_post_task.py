from turtle import pos
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

test_data_file_name = "tests/test_files/sample_task_0.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as post_task_test:
    dummy_post_test = json.load(post_task_test)


def test_post_task():
    reseed()
    post_response = client.post("/tasks", json = dummy_post_test)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["task_id"]
    task_id = post_response.json()["task_id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200

    post_task_good_file = "tests/test_files/post_task_good_test_data.json"
    post_task_good_test_data_absolute_path = os.path.join(os.getcwd(), post_task_good_file)

    with open(post_task_good_test_data_absolute_path, "r") as post_task_good_test_data:
        expected_post_test_result = json.load(post_task_good_test_data)

    assert get_response.json() == expected_post_test_result
    reseed()

def test_post_task_bad():
    # Zeroth, we test posting a task in a not-JSON format. 
    reseed()
    post_response = client.post("/tasks", headers={"Content-Type": "application/json"}, \
        data = "not-a-json")
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    error_message["type"] == "value_error.jsondecode"
    # May want to make this case a little more thorough, 
    # but I'm not sure if this test actually corresponds to a bad request.

    # First, we test posting a task without a release ID
    post_response = client.post("/tasks", json = \
        {"task_name": "no_release_id", "step_num": 0})
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    assert error_message["loc"] == ["body", "release_id"]
    assert error_message["msg"] == "field required"
    assert error_message["type"] == "value_error.missing"
    reseed()

    # Next, we test posting a task without a task name
    post_response = client.post("/tasks", json = \
        {"release_id": 3, "step_num": 0})
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    assert error_message["loc"] == ["body", "task_name"]
    assert error_message["msg"] == "field required"
    assert error_message["type"] == "value_error.missing"
    reseed()

    # Next, we test posting a task without a task num
    post_response = client.post("/tasks", json = \
        {"task_name": "no_step_num", "release_id": 3})
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    assert error_message["loc"] == ["body", "step_num"]
    assert error_message["msg"] == "field required"
    assert error_message["type"] == "value_error.missing"
    reseed()

    # Note for maintenance: There are no bad task names (so far), 
    # as the task name is a string and passed via JSON. 
    # Task names as bad datatypes (e.g. int) are JSONed away
    # and are indistinguishble from good task names.

    # Next, we test posting a task with a release ID with a bad type
    post_response = client.post("/tasks", json = \
        {"release_id": "bad_type", \
        "task_name": "release_ID_bad_type_task_test",
        "step_num": 0})
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    assert error_message["loc"] == ["body", "release_id"]
    assert error_message["msg"] == "value is not a valid integer"
    assert error_message["type"] == "type_error.integer"
    reseed()

    # We also test posting a task with a task number with a bad type
    post_response = client.post("/tasks", json = \
        {"release_id": 3, \
        "task_name": "release_ID_bad_type_task_test",
        "step_num": "bad_type"})
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    assert error_message["loc"] == ["body", "step_num"]
    assert error_message["msg"] == "value is not a valid integer"
    assert error_message["type"] == "type_error.integer"
    reseed()

    # Above are all the errors we can expect Pydantic to catch. 
    # The rest should be handled by logic in main, and should be done gracefully.

    # Next, we test posting a task with a release ID not corresponding to a release
    post_response = client.post("/tasks", json = \
        {"release_id": -1, \
        "task_name": "release_ID_not_corresponding_to_release_test",\
        "step_num": 0})
    assert post_response.status_code == 422
    assert list(post_response.json().keys()) == ["detail"]
    error_message = post_response.json()["detail"][0]
    assert error_message["loc"] == ["body", "release_id"]
    assert error_message["msg"] == "No such release_id exists."
    reseed()
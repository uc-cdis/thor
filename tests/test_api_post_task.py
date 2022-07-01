from turtle import pos
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

reseed()

test_data_file_name = "tests/test_files/sample_task_0.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as post_task_test:
    dummy_post_test = json.load(post_task_test)


def test_post_task():
    post_response = client.post("/tasks", json = dummy_post_test)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["task_id"]
    task_id = post_response.json()["task_id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert list(get_response.json().keys()) == ["task"]
    response_body = get_response.json()["task"]
    assert set(response_body.keys()) == {"task_id", "task_name", "release_id", "status"}
    assert response_body["task_id"] == task_id
    assert response_body["task_name"] == dummy_post_test["task_name"]
    assert response_body["release_id"] == dummy_post_test["release_id"]
    assert response_body["status"] == "PENDING"
    
    reseed()

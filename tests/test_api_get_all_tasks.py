import pytest
import json

from fastapi.testclient import TestClient

from thor.main import app

client = TestClient(app)


with open("task_test_data.txt", "r") as read_task_test:
    expected_output_for_get_tasks = json.load(read_task_test)

print(expected_output_for_get_tasks)


def test_get_all_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_tasks

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


def test_get_all_tasks():
    reseed()
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_tasks

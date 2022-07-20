from platform import release
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

test_data_file_name = "tests/test_files/post_release_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as post_release_test:
    expected_output_for_post_release = json.load(post_release_test)


@pytest.mark.parametrize("task_id, status", [(1, "SUCCESS"), (2, "FAILURE"), (3, "PENDING")])
def test_put_task_status(task_id, status):
    reseed()
    put_response = client.put(f"/tasks/{task_id}", json={"status": status}, headers={"Content-Type": "application/json"})
    assert put_response.status_code == 200
    assert put_response.json() == {"task_id": task_id, "status": status}

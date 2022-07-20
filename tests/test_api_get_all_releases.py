import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

test_data_file_name = "tests/test_files/release_test_data.json"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as read_task_test:
    expected_output_for_get_releases = json.load(read_task_test)


def test_read_releases():
    reseed()
    response = client.get("/releases")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_releases

import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app

client = TestClient(app)

test_data_file_name = "tests/release_test_data.txt"
test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

with open(test_data_absolute_path, "r") as read_task_test:
    expected_output_for_get_releases = json.load(read_task_test)


@pytest.mark.parametrize("release_id", [3, 4])
def test_read_single_release(release_id):
    response = client.get(f"/releases/{release_id}")
    assert response.status_code == 200

    # creates a dictionary associating each release with its numerical release id
    releases_dict_byID = {
        rel["release_id"]: rel for rel in expected_output_for_get_releases["releases"]
    }

    expected_output_for_get_release = (
        f'{{ "release": {json.dumps(releases_dict_byID[release_id])} }}'
    )

    # convert json string back to json object for comparison
    assert response.json() == json.loads(expected_output_for_get_release)

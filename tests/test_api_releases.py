import pytest
import json
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

expected_output_for_get_releases = {
  "releases": [
    {
      "version": "2021.09",
      "result": "In Progress",
      "id": 3
    },
    {
      "version": "2021.07",
      "result": "Completed",
      "id": 4
    }
  ]
}

def test_read_releases():
    response = client.get("/releases")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_releases

@pytest.mark.parametrize("release_id", [3, 4])
def test_read_single_release(release_id):
    response = client.get(f"/releases/{release_id}")
    assert response.status_code == 200
    if release_id == 3:
      # convert py dictionary to json string
      release3_payload = json.dumps(expected_output_for_get_releases['releases'][0])
      expected_output_for_get_release = f"{{ \"release\": {release3_payload} }}"
    elif release_id == 4:
      release4_payload = json.dumps(expected_output_for_get_releases['releases'][1])
      expected_output_for_get_release = f"{{ \"release\": {release4_payload} }}"
    # convert json string back to json object for comparison
    assert response.json() == json.loads(expected_output_for_get_release)

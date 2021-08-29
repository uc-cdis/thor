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

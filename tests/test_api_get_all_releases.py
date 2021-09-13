import pytest
import json

from fastapi.testclient import TestClient

from thor.main import app

client = TestClient(app)


with open("release_test_data.txt", "r") as read_release_test:
    expected_output_for_get_releases = json.load(read_release_test)


def test_read_releases():
    response = client.get("/releases")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_releases

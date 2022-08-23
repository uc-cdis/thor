# test_run_task.py
from requests import request
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient
from thor.main import app

client = TestClient(app)

def test_status_ui():
    """
    Tests to make sure that we can return an HTML thing?
    """

    status_get = client.get("/status")
    
    # Check JSON response of direct call to start task
    assert status_get.status_code == 200
    
    html_absolute_path = os.path.join(os.getcwd(), "src/thor/status_ui.html")
    with open(html_absolute_path, "r") as html_expected_file:
        html_expected = html_expected_file.read()
        assert status_get.text == html_expected

from platform import release
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

reseed()

def test_post_release():
    test_version_name = "5"
    post_response = client.post("/releases/" + test_version_name)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["release_id"]
    release_id = post_response.json()["release_id"]

    release_get_response = client.get(f"/releases/{release_id}")
    assert release_get_response.status_code == 200
    assert list(release_get_response.json().keys()) == ["release"]
    release_response_body = release_get_response.json()["release"]
    assert set(release_response_body.keys()) == {"release_id", "version", "result"}
    assert release_response_body["release_id"] == release_id
    assert release_response_body["version"] == test_version_name
    assert release_response_body["result"] == "PENDING"

    tasks_get_response = client.get(f"/releases/{release_id}/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    response_body = tasks_get_response.json()["release_tasks"]

    test_data_file_name = "thor_config.json"
    test_data_absolute_path = os.path.join(os.getcwd(), test_data_file_name)

    with open(test_data_absolute_path, "r") as test_release_tasks:
        release_tasks_dict = json.load(test_release_tasks)

    expected_jobname_list = []

    for step in release_tasks_dict:
        jobname = release_tasks_dict[step]["job_name"]
        expected_jobname_list.append(jobname)

    for task in response_body:
        assert task["status"] == "PENDING"
        jobname = task["task_name"]
        assert jobname in expected_jobname_list
        expected_jobname_list.remove(jobname)
    
    assert expected_jobname_list == []
    
    reseed()
    


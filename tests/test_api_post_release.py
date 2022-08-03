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



@pytest.mark.parametrize("release_name", ["test_release_5"])
def test_post_release(release_name: str):
    reseed()
    post_response = client.post("/releases/" + release_name)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["release_id"]
    release_id = post_response.json()["release_id"]

    release_get_response = client.get(f"/releases/{release_name}")
    assert release_get_response.status_code == 200
    json_response = release_get_response.json()
    expected_output_for_post_release["release"]["release_id"] = release_id
    assert json_response == expected_output_for_post_release

    tasks_get_response = client.get(f"/releases/{release_name}/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    response_body = tasks_get_response.json()["release_tasks"]

    test_data_file_name = "dummy_thor_config.json"
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
    
def test_post_release_when_empty():
    # What happens when tables of both are empty? 
    # This was an error that was fixed, and we should keep it that way. 
    # We should be creating with no issues. 

    client.put("/clear")

    post_response = client.post("/releases/test_release_5")
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["release_id"]
    release_id = post_response.json()["release_id"]

    release_get_response = client.get(f"/releases/test_release_5")
    assert release_get_response.status_code == 200
    json_response = release_get_response.json()
    expected_output_for_post_release["release"]["release_id"] = release_id
    assert json_response == expected_output_for_post_release

    tasks_get_response = client.get(f"/releases/test_release_5/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    response_body = tasks_get_response.json()["release_tasks"]

    test_data_file_name = "dummy_thor_config.json"
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
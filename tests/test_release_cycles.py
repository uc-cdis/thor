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

def clear_shell_script_target():
    script_target_file_name = "shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "w") as target_file:
        target_file.write("Shell Script Target\n\n")



@pytest.mark.parametrize("release_name", ["test_release_1"])
def test_successful_release_cycle(release_name):
    """
    Runs through all steps of a release, from creation to completion, 
    and ensures that they all work out. 
    Expects this release cycle to be successful. 
    """
    reseed()
    clear_shell_script_target()

    # Creates a release (and associated tasks)
    post_response = client.post("/releases/" + release_name)
    assert post_response.status_code == 200
    release_id = post_response.json()["release_id"]

    # Starts the release, causing the associated shell scripts to be run
    start_results = client.post(f"/releases/{release_id}/start")
    # print(start_results.json())

    # Checks contents of the "shell_script_target.txt" file to ensure that
    # all the shell scripts were run correctly.

    script_target_file_name = "shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "r") as read_target_file:
        target_file_contents = read_target_file.read()

    test_target_file_name = "tests/test_files/test_good_shell_script_target.txt"
    test_target_absolute_path = os.path.join(os.getcwd(), test_target_file_name)
    with open(test_target_absolute_path, "r") as read_test_target_file:
        test_target_file_contents = read_test_target_file.read()

    assert target_file_contents == test_target_file_contents


    # Checks tasks and release object in database to make sure that execution
    # occurred as expected. 

    # Release:
    release_get_response = client.get(f"/releases/")
    assert release_get_response.status_code == 200
    assert release_name in [r["version"] for r in release_get_response.json()["releases"]]
    
    # print(start_results.json())
    assert {r["release_id"]:r["result"] \
        for r in release_get_response.json()["releases"]}[release_id] == "Success."

    # Tasks:
    tasks_get_response = client.get(f"/releases/{release_id}/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    response_body = tasks_get_response.json()["release_tasks"]
    for response in response_body:
        assert response["status"] == "SUCCESS"
    


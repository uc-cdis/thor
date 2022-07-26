import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

def clear_shell_script_target():
    script_target_file_name = "workspace/shell_script_target.txt"
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
    start_results = client.post(f"/releases/{release_name}/start")
    # print(start_results.json())

    # Checks contents of the "shell_script_target.txt" file to ensure that
    # all the shell scripts were run correctly.

    script_target_file_name = "workspace/shell_script_target.txt"
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
        for r in release_get_response.json()["releases"]}[release_id] == "RELEASED"

    # Tasks:
    tasks_get_response = client.get(f"/releases/{release_name}/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    response_body = tasks_get_response.json()["release_tasks"]
    for response in response_body:
        assert response["status"] == "SUCCESS"
    

@pytest.mark.parametrize("release_name", ["test_release_2"])
def test_failing_release_cycle(release_name):
    """
    Runs through all steps of a release, from creation to completion,
    but watches as the release fails and checks that everything is as it should be. 
    Expects to fail the release at step 7, 
    and actively writes to the step7 script to ensure this. 
    Will rewrite afterwards with the correct script. 
    """
    reseed()
    clear_shell_script_target()

    # Creates a release (and associated tasks)
    post_response = client.post("/releases/" + release_name)
    assert post_response.status_code == 200
    release_id = post_response.json()["release_id"]

    # IMPORTANT: REWRITES SHELL SCRIPT 7 TO FAIL
    shell_script_fail_file_name = "jenkins-jobs-scripts/step7/dummy7.sh"
    shell_script_fail_absolute_path = os.path.join(os.getcwd(), shell_script_fail_file_name)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("INVALID COMMAND")

    # Starts the release, causing the associated shell scripts to be run
    start_results = client.post(f"/releases/{release_name}/start")
    print(start_results.json())

    # REWRITES SHELL SCRIPT 7 TO BE CORRECT AGAIN (IMPORTANT)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("echo dummy step 7 >> ../shell_script_target.txt")

    # Checks contents of the "shell_script_target.txt" file to ensure that
    # only the first 7 shell scripts were run before stopping. 

    script_target_file_name = "workspace/shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "r") as read_target_file:
        target_file_contents = read_target_file.read()

    test_target_file_name = "tests/test_files/test_bad_shell_script_target.txt"
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
        for r in release_get_response.json()["releases"]}[release_id] == "PAUSED"

    # Tasks:
    tasks_get_response = client.get(f"/releases/{release_name}/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    task_results = {int(t["step_num"]):t["status"] for t in tasks_get_response.json()["release_tasks"]}
    # print(task_results)
    for i in range(1,12):
        # print(i, task_results[i], i < 7)
        if i < 7:
            assert task_results[i] == "SUCCESS" 
        elif i == 7:
            assert task_results[i] == "FAILED"
        else:
            assert task_results[i] == "PENDING"
        


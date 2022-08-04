import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import clear_tables

client = TestClient(app)

def clear_shell_script_target():
    script_target_file_name = "workspace/shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    if os.path.exists(target_absolute_path):
        with open(target_absolute_path, "w") as target_file:
            target_file.write("Shell Script Target\n\n")

def ensure_shell_script_integrity():
    """
    Checks all the shell scripts before running to ensure that 
    they're all in the original, unaltered state. 
    Mostly useful while testing here, as destructively rewriting critical functions
    leads to errors when left half-done. """

    with open("dummy_thor_config.json", "r") as read_config_file:
        config = json.load(read_config_file)
    for i in range(1, len(config) + 1):
        script_name = "dummy" + str(i) + ".sh"
        script_path = os.path.join(os.getcwd(), f"jenkins-jobs-scripts/step{i}/", script_name)
        # print(script_path)
        with open(script_path, "w") as write_script_file:
            write_script_file.write(f"echo dummy step {i} >> ../shell_script_target.txt")


@pytest.mark.parametrize("release_name", ["test_release_1"])
def test_successful_release_cycle(release_name):
    """
    Runs through all steps of a release, from creation to completion, 
    and ensures that they all work out. 
    Expects this release cycle to be successful. 
    """
    ensure_shell_script_integrity()
    client.put("/clear")
    clear_shell_script_target()

    # Creates and starts a release, running through tasks.
    start_results = client.post(f"/releases/{release_name}/start")
    assert start_results.status_code == 200
    print(start_results.json())

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
    release_get_response = client.get(f"/releases/{release_name}")
    assert release_get_response.status_code == 200
    assert release_get_response.json()["release"] != None
    
    assert release_get_response.json()["release"]["result"] == "RELEASED"

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
    ensure_shell_script_integrity()
    client.put("/clear")
    clear_shell_script_target()

    # IMPORTANT: REWRITES SHELL SCRIPT 7 TO FAIL
    shell_script_fail_file_name = "jenkins-jobs-scripts/step7/dummy7.sh"
    shell_script_fail_absolute_path = os.path.join(os.getcwd(), shell_script_fail_file_name)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("INVALID COMMAND")

    # Creates and starts the release, causing the associated shell scripts to be run
    start_results = client.post(f"/releases/{release_name}/start")
    # print(start_results.json())

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
    
    release_id = [r["release_id"] for r in release_get_response.json()["releases"] if r["version"] == release_name][0]
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
        

@pytest.mark.parametrize("release_name", ["bad_release_name"])
def test_bad_release_name(release_name):
    """
    Tests that a bad release name returns a bad response. 
    """
    client.put("/clear")
    client.post(f"/releases/{release_name}/start")
    post_response = client.post(f"/releases/{release_name}/start")
    assert post_response.status_code == 422
    assert post_response.json()["detail"] == [{"loc":["body","release_name"],"msg":f"Release with name {release_name} already exists."}]


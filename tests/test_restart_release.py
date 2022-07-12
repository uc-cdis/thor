import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed

client = TestClient(app)

def clear_shell_script_target():
    script_target_file_name = "shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "w") as target_file:
        target_file.write("Shell Script Target\n\n")

@pytest.mark.parametrize("release_name", ["test_release_3"])
def test_restart_release(release_name):
    """
    Runs through a release that fails at step 8. 
    Deliberately edits dummy8.sh to ensure failure. 
    Then, fixes the error and restarts the release, succeeding.
    """
    reseed()
    clear_shell_script_target()

    # Creates a release (and associated tasks)
    post_response = client.post("/releases/" + release_name)
    assert post_response.status_code == 200
    release_id = post_response.json()["release_id"]

    # IMPORTANT: REWRITES SHELL SCRIPT 8 TO FAIL
    shell_script_fail_file_name = "jenkins-jobs-scripts/step8/dummy8.sh"
    shell_script_fail_absolute_path = os.path.join(os.getcwd(), shell_script_fail_file_name)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("definitely not a command")

    # Starts the release, causing the associated shell scripts to be run
    start_results = client.post(f"/releases/{release_id}/start")
    # print(start_results.json())

    # REWRITES SHELL SCRIPT 8 TO BE CORRECT AGAIN (IMPORTANT)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("echo dummy step 8 >> ../shell_script_target.txt")

    # We don't check the intermediate step here because it's essentially 
    # the same as a failing release, as seen in test_release_cycles. 


    # Restarts the release, running shell scripts from 8 onwards
    restart_results = client.post(f"/releases/{release_id}/restart")
    # print(restart_results.json())

    # Checks contents of the "shell_script_target.txt" file to ensure that
    # 1-8 were run, then 8-11 as well. 

    script_target_file_name = "shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "r") as read_target_file:
        target_file_contents = read_target_file.read()

    # Note that as 8 doesn't output the first time, 
    # the resulting expected output is the same as a successful release
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
        


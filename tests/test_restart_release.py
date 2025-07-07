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
        script_path = os.path.join(os.getcwd(), f"release-task-scripts/step{i}/", script_name)
        # print(script_path)
        with open(script_path, "w") as write_script_file:
            write_script_file.write(f"echo dummy step {i} >> ../shell_script_target.txt")


@pytest.mark.parametrize("release_name", ["test_release_3"])
def test_restart_release(release_name):
    """
    Runs through a release that fails at step 8. 
    Deliberately edits dummy8.sh to ensure failure. 
    Then, fixes the error and restarts the release, succeeding.
    """
    ensure_shell_script_integrity()
    client.put("/thor-admin/clear")
    clear_shell_script_target()

    # print("bananas good")

    # Creates a release (and associated tasks)
        # Note: This is no longer necessary as /start does this. 
    # post_response = client.post("/thor-admin/releases/" + release_name)
    # assert post_response.status_code == 200
    # release_id = post_response.json()["release_id"]

    # IMPORTANT: REWRITES SHELL SCRIPT 8 TO FAIL
    shell_script_fail_file_name = "release-task-scripts/step8/dummy8.sh"
    shell_script_fail_absolute_path = os.path.join(os.getcwd(), shell_script_fail_file_name)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("INVALID COMMAND")

    # Starts the release, causing the associated shell scripts to be run
    start_results = client.post(f"/thor-admin/releases/{release_name}/start")
    # print(start_results.json())

    # REWRITES SHELL SCRIPT 8 TO BE CORRECT AGAIN (IMPORTANT)
    with open(shell_script_fail_absolute_path, "w") as shell_script_fail_file:
        shell_script_fail_file.write("echo dummy step 8 >> ../shell_script_target.txt")

    # We don't check the intermediate step here because it's essentially 
    # the same as a failing release, as seen in test_release_cycles. 


    # Restarts the release, running shell scripts from 8 onwards
    restart_results = client.post(f"/thor-admin/releases/{release_name}/restart")
    # print(restart_results.json())

    # Checks contents of the "shell_script_target.txt" file to ensure that
    # 1-8 were run, then 8-11 as well. 

    script_target_file_name = "workspace/shell_script_target.txt"
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
    print(release_get_response.json()["releases"])
    assert {dict["version"]: dict["result"]
        for dict in release_get_response.json()["releases"]}[release_name] == "RELEASED"

    # Tasks:
    tasks_get_response = client.get(f"/releases/{release_name}/tasks")
    assert tasks_get_response.status_code == 200
    assert list(tasks_get_response.json().keys()) == ["release_tasks"]
    response_body = tasks_get_response.json()["release_tasks"]
    for response in response_body:
        assert response["status"] == "SUCCESS"
    

@pytest.mark.parametrize("release_name", ["bad_release_name"])
def test_bad_release_name(release_name):
    """
    Tests that a bad release name returns a bad response. 
    """
    client.put("/thor-admin/clear")
    post_response = client.post(f"/thor-admin/releases/{release_name}/restart")
    assert post_response.status_code == 422
    assert post_response.json()["detail"] == [{"loc":["body","release_name"],"msg":f"No release with name {release_name} exists."}]




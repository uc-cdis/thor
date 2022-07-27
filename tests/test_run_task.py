# test_run_task.py
from requests import request
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed
from thor.dao.release_dao import release_id_lookup_class, read_release
from thor.dao.task_dao import get_release_task_step, get_release_tasks, update_task

client = TestClient(app)

def clear_shell_script_target():
    script_target_file_name = "workspace/shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "w") as target_file:
        target_file.write("Shell Script Target\n\n")

@pytest.mark.parametrize("release_name, step_num", [("2021.07", 1), ("2021.07", 2), ("2021.07", 3)])
def test_run_task_incomplete(release_name, step_num):
    """
    Tests the running of one task to make sure that it is run properly. 
    """
    reseed()
    clear_shell_script_target()

    start_task_result = client.post(f"/tasks/start", 
        json={"release_name": release_name, "step_num": step_num},
        headers={"Content-Type": "application/json"}
        )
    
    # Check JSON response of direct call to start task
    assert start_task_result.status_code == 200
    assert start_task_result.json() == {
        "release_name": release_name,
        "step_num": step_num,
        "status": "SUCCESS"
    }

    # Check target file to make sure that the shell script was run correctly.
    script_target_file_name = "workspace/shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "r") as read_target_file:
        target_file_contents = read_target_file.read()
        assert target_file_contents == "Shell Script Target\n\ndummy step " + str(step_num) + "\n"

    # Check actual task status in DB
    current_task = get_release_task_step(release_name, step_num)
    assert current_task.status == "SUCCESS"

    # Check release status in DB
    release_id = release_id_lookup_class.release_id_lookup(None, release_name)
    assert read_release(release_id).result == "PAUSED"
    


def test_run_task_complete():
    """
    Runs a single task that finishes a release, and ensures that the release
    is marked as complete.
    """
    reseed()
    clear_shell_script_target()

    # Create new test release for working with
    release_name = "test_release_run_task"
    post_response = client.post(f"/releases/{release_name}")
    assert post_response.status_code == 200
    release_id = post_response.json()["release_id"]
    
    # Manually set all tasks except last to 'SUCCESS'

    test_config_file_name = "dummy_thor_config.json"
    config_abs_path = os.path.join(os.getcwd(), test_config_file_name)
    with open(config_abs_path, "r") as read_config:
        config = read_config.read()
    
    task_list = get_release_tasks(release_id)
    last_task = task_list.pop(-1)

    for task in task_list:
        update_task(task.task_id, "status", "SUCCESS")

    # Run last task

    start_task_result = client.post(f"/tasks/start",
        json={"release_name": release_name, "step_num": last_task.step_num},
        headers={"Content-Type": "application/json"}
        )

    # Check JSON response of direct call to start task
    assert start_task_result.status_code == 200
    assert start_task_result.json() == {
        "release_name": release_name,
        "step_num": last_task.step_num,
        "status": "SUCCESS"
    }

    # Check target file to make sure that the shell script was run correctly.
    script_target_file_name = "workspace/shell_script_target.txt"
    target_absolute_path = os.path.join(os.getcwd(), script_target_file_name)
    with open(target_absolute_path, "r") as read_target_file:
        target_file_contents = read_target_file.read()
        assert target_file_contents == f"Shell Script Target\n\ndummy step {last_task.step_num}\n"

    # Check actual task status in DB
    current_task = get_release_task_step(release_name, last_task.step_num)
    assert current_task.status == "SUCCESS"

    # Check release status in DB
    assert read_release(release_id).result == "RELEASED"


def test_run_task_invalids():
    """
    Tests the behavior of the endpoint when passing invalid parameters.
    """
    reseed()
    clear_shell_script_target()

    # Test invalid release name
    start_task_result = client.post(f"/tasks/start", 
        json={"release_name": "invalid_release_name", "step_num": 1},
        headers={"Content-Type": "application/json"}
        )
    assert start_task_result.status_code == 422
    assert start_task_result.json() == {
            "detail": [{
                'loc': ['body', 'release_name'], 
                'msg': "Release_name invalid_release_name does not exist."}]
        }

    # Test invalid step number
    start_task_result = client.post(f"/tasks/start", 
        json={"release_name": "2021.07", "step_num": -1},
        headers={"Content-Type": "application/json"}
        )
    assert start_task_result.status_code == 422
    assert start_task_result.json() == {
            "detail": [{
                'loc': ['body', 'step_num'], 
                'msg': "No step with number -1 exists."}]
        }
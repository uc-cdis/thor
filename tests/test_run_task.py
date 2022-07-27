# test_run_task.py
import pytest
import json
import os

import os.path
from fastapi.testclient import TestClient

from thor.main import app
from thor.dao.clear_tables_reseed import reseed
from thor.dao.release_dao import release_id_lookup_class, read_release
from thor.dao.task_dao import get_release_task_step

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
    print(start_task_result.json())
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
    



import pytest
import json
from fastapi.testclient import TestClient

# This is a pretty delicate thing, any change could cause it to break
# Is there a better way to make this work?
import sys

from thor.main import app

client = TestClient(app)

print("working")

expected_output_for_get_task = {
    "tasks": [
        {
            "release_id": 3,
            "status": "success",
            "task_id": 8,
            "task_name": "Create Release in JIRA",
        },
        {
            "release_id": 3,
            "status": "success",
            "task_id": 9,
            "task_name": "Cut integration branch",
        },
        {
            "release_id": 3,
            "status": "success",
            "task_id": 10,
            "task_name": "Cut integration branch",
        },
    ]
}

@pytest.mark.parametrize("task_id", [8, 9, 10])
def test_read_single_task(task_id):
    response = client.get(f"/tasks/{task_id}")
    # TODO: changed status code to 404 might need to revert to 200
    assert response.status_code == 200
    if task_id == 8:
      # convert py dictionary to json string
      task8_payload = json.dumps(expected_output_for_get_tasks['tasks'][7])
      expected_output_for_get_task = f"{{ \"task\": {task8_payload} }}"
    elif task_id == 9:
      task9_payload = json.dumps(expected_output_for_get_tasks['tasks'][8])
      expected_output_for_get_task = f"{{ \"task\": {task9_payload} }}"
    elif task_id == 10:
      task10_payload = json.dumps(expected_output_for_get_tasks['tasks'][9])
      expected_output_for_get_task = f"{{ \"task\": {task10_payload} }}"
    assert response.json() == json.loads(expected_output_for_get_task)
    

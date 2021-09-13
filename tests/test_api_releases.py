import pytest
import json
from fastapi.testclient import TestClient

# This is a pretty delicate thing, any change could cause it to break
# Is there a better way to make this work?
import sys

from thor.main import app

client = TestClient(app)


print("working")
# Question: Would it be better to put the expected outputs into a separate file,
# to avoid making the code harder to read?
expected_output_for_get_releases = {
    "releases": [
        {"version": "2021.09", "result": "In Progress", "release_id": 3},
        {"version": "2021.07", "result": "Completed", "release_id": 4},
    ]
}

expected_output_for_get_tasks = {
    "tasks": [
        {
            "task_id": 1,
            "task_name": "Create Release in JIRA",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 2,
            "task_name": "Cut integration branch",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 3,
            "task_name": "Update CI env with the latest integration branch",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 4,
            "task_name": "Generate release notes",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 5,
            "task_name": "Run Load Tests",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 6,
            "task_name": "Merge integration branch into stable and tag release",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 7,
            "task_name": "Mark gen3 release as released in JIRA",
            "status": "success",
            "release_id": 4,
        },
        {
            "task_id": 8,
            "task_name": "Create Release in JIRA",
            "status": "success",
            "release_id": 3,
        },
        {
            "task_id": 9,
            "task_name": "Cut integration branch",
            "status": "success",
            "release_id": 3,
        },
        {
            "task_id": 10,
            "task_name": "Update CI env with the latest integration branch",
            "status": "in progress",
            "release_id": 3,
        },
    ]
}

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


def test_read_releases():
    response = client.get("/releases")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_releases


@pytest.mark.parametrize("release_id", [3, 4])
def test_read_single_release(release_id):
    response = client.get(f"/releases/{release_id}")
    assert response.status_code == 200
    if release_id == 3:
        # convert py dictionary to json string
        release3_payload = json.dumps(expected_output_for_get_releases["releases"][0])
        expected_output_for_get_release = f'{{ "release": {release3_payload} }}'
    elif release_id == 4:
        release4_payload = json.dumps(expected_output_for_get_releases["releases"][1])
        expected_output_for_get_release = f'{{ "release": {release4_payload} }}'
    # convert json string back to json object for comparison
    assert response.json() == json.loads(expected_output_for_get_release)


def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == expected_output_for_get_tasks

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

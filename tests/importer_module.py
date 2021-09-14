# importer_module.py

import json

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

with open("task_test_data.txt", "w") as output_file:
    json.dump(expected_output_for_get_tasks, output_file)

#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

poetry run python /src/release-task-scripts/step1/create-release-in-jira.py
poetry run python /src/release-task-scripts/step1/create-release-tasks-in-jira.py

#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

poetry run python /src/release-task-scripts/step15/mark-gen3-release-as-released.py

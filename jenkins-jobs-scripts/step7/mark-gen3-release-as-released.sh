#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

poetry install

poetry run python3 jenkins-jobs-scripts/step7/mark-gen3-release-as-released.py

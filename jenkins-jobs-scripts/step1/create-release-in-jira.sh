#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

pip install --upgrade pip
export CRYPTOGRAPHY_DONT_BUILD_RUST=1

python3 -m pip install jira==2.0 --user

python3 gen3release-sdk/create_jira_project_version.py


#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

pip install --upgrade pip
export CRYPTOGRAPHY_DONT_BUILD_RUST=1

/env/bin/python /src/jenkins-jobs-scripts/step1/create-release-in-jira.py
/env/bin/python /src/jenkins-jobs-scripts/step1/create-release-tasks-in-jira.py

#!/bin/bash

export JIRA_USERNAME="ctds.qa.automation"

pip install --upgrade pip
export CRYPTOGRAPHY_DONT_BUILD_RUST=1

/env/bin/python /src/jenkins-jobs-scripts/step1/create-release-in-jira.py

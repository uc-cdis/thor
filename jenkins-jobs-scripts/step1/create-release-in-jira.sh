#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

/env/bin/python /src/jenkins-jobs-scripts/step1/create-release-in-jira.py
/env/bin/python /src/jenkins-jobs-scripts/step1/create-release-tasks-in-jira.py

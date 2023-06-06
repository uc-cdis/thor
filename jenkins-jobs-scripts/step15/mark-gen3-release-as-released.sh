#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

/env/bin/python /src/jenkins-jobs-scripts/step15/mark-gen3-release-as-released.py

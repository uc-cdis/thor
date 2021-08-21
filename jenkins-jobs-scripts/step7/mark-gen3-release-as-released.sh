#!/bin/bash

export JIRA_SVC_ACCOUNT="ctds.qa.automation@gmail.com"

poetry install

poetry run python3 gen3release-sdk/update_jira_release.py

from jira import JIRA
import re
import os
import sys
import datetime

options = {"server": "https://ctds-planx.atlassian.net", "rest_api_version": "3"}
jira = JIRA(
    options, basic_auth=(os.environ["JIRA_SVC_ACCOUNT"], os.environ["JIRA_API_TOKEN"])
)

version = jira.get_project_version_by_name(
    os.environ["JIRA_PROJECT"], os.environ["RELEASE_VERSION"]
)
if version:
    version.update(released=True)
    print("Release marked as RELEASED successfully!")
else:
    print("version not found :(")
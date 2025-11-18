from atlassian import Jira
import os

jira = Jira(
    url="https://ctds-planx.atlassian.net",
    username=os.environ["JIRA_SVC_ACCOUNT"].strip(),
    password=os.environ["JIRA_API_TOKEN"].strip(),
    cloud=True,
)

version = jira.get_project_version_by_name(
    os.environ["JIRA_PROJECT"], os.environ["RELEASE_VERSION"]
)
if version:
    version.update(released=True)
    print("Release marked as RELEASED successfully!")
else:
    print("version not found :(")

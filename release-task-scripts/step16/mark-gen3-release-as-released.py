from atlassian import Jira
import os

jira = Jira(
    url="https://ctds-planx.atlassian.net",
    username=os.environ["JIRA_SVC_ACCOUNT"].strip(),
    password=os.environ["JIRA_API_TOKEN"].strip(),
    cloud=True,
)

versions = jira.get_project_versions(key=os.environ["JIRA_PROJECT"])
version = next((v for v in versions if v["name"] == os.environ["RELEASE_VERSION"]), None)

if version:
    version_id = version.get("id", None)

if version_id:
    jira.update_version(version=version_id, is_released=True)
else:
    print("version not found :(")

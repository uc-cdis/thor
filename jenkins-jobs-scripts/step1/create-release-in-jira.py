from jira import JIRA
import re
import os
import sys
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json

# options = {"server": "https://ctds-planx.atlassian.net"}
# jira = JIRA(
#     options, basic_auth=(os.environ["JIRA_SVC_ACCOUNT"].strip(), os.environ["JIRA_API_TOKEN"].strip())
# )

monthinteger = int(os.environ["RELEASE_VERSION"].split(".")[1])
month = datetime.date(1900, monthinteger, 1).strftime("%B")
year = os.environ["RELEASE_VERSION"].split(".")[0]

# result = jira.create_version(
#     "{}".format(os.environ["RELEASE_VERSION"]),
#     os.environ["JIRA_PROJECT"],
#     description="[Thor] Gen3 Release - {} {}".format(month, year),
#     releaseDate=None,
#     startDate=None,
#     archived=False,
#     released=False,
# )
url = "https://ctds-planx.atlassian.net//rest/api/3/version"
auth = HTTPBasicAuth(os.environ["JIRA_SVC_ACCOUNT"].strip(), os.environ["JIRA_API_TOKEN"].strip())
headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}
payload = json.dumps( {
    "archived": False,
    "releaseDate": None,
    "name": os.environ["RELEASE_VERSION"],
    "description": "[Thor] Gen3 Release - {}".format(month),
    "projectId": os.environ["JIRA_PROJECT"],
    "released": True
} )
res = requests.post(
    url,
    data=payload,
    headers=headers,
    auth=auth
)

print(json.dumps(json.loads(res.text), sort_keys=True, indent=4, separators=(",", ": ")))

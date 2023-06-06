import os
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json

monthinteger = int(os.environ["RELEASE_VERSION"].split(".")[1])
month = datetime.date(1900, monthinteger, 1).strftime("%B")
year = os.environ["RELEASE_VERSION"].split(".")[0]

url = "https://ctds-planx.atlassian.net//rest/api/3/version"
auth = HTTPBasicAuth(
    os.environ["JIRA_SVC_ACCOUNT"].strip(), os.environ["JIRA_API_TOKEN"].strip()
)
headers = {"Accept": "application/json", "Content-Type": "application/json"}
payload = json.dumps(
    {
        "archived": False,
        "releaseDate": None,
        "name": os.environ["RELEASE_VERSION"],
        "description": "Gen3 Monthly Release - {}".format(month),
        "project": os.environ["JIRA_PROJECT"],
        "released": False,
    }
)
print(payload)
res = requests.post(url, data=payload, headers=headers, auth=auth)
print(
    json.dumps(json.loads(res.text), sort_keys=True, indent=4, separators=(",", ": "))
)

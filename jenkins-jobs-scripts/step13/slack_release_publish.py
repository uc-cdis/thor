import requests
import os

# Variables needed in code
csv_file_path = os.path.join('..', '..', 'release_names.csv')
release_version = os.environ["RELEASE_VERSION"]
release_url = f"https://github.com/uc-cdis/cdis-manifest/blob/master/releases/{release_version.replace('.', '/')}/gen3-release-notes.md"
github_url = "https://api.github.com/repos/uc-cdis/gen3-summary/actions/workflows/send_message.yaml/dispatches"

# Read release_names.csv and get the RELEASE_TITLE based on RELEASE_VERSION
with open(csv_file_path, 'r') as infile:
    for line in infile.readlines():
        if release_version in line:
            release_title = line.strip().split(',')[-1]

# Headers for API Call
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f'Bearer {os.environ["GITHUB_TOKEN"]}',
    "X-GitHub-Api-Version": "2022-11-28",
}

# Data to post for API Call
data = {
    "ref": "master",
    "inputs": {
        "slack_urls": "https://hooks.slack.com/services/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",
        "title": f":tada: Gen3 Release {release_version} ({release_title}) is out :tada:",
        "message": f"Please find the release notes here - {release_url}"
    }
}

# Perform the API Call request
response = requests.post(url=github_url,
                         headers=headers,
                         json=data)

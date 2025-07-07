import requests
import os

# Variables needed in code
release_version = os.environ["RELEASE_VERSION"]
github_url = "https://api.github.com/repos/uc-cdis/gen3-code-vigil/actions/workflows/load_tests.yaml/dispatches"

# Headers for API Call
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f'Bearer {os.environ["GITHUB_TOKEN"].strip()}',
    "X-GitHub-Api-Version": "2022-11-28",
}

# Data to post for API Call
data = {
    "ref": "master",
    "inputs": {
        "RELEASE_VERSION": release_version
    }
}

# Perform the API Call request
response = requests.post(url=github_url,
                         headers=headers,
                         json=data)

assert response.status_code == 204, f"Expected status code 204, but got {response.status_code}.\n{response.content}"

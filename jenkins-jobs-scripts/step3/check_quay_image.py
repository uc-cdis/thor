import requests
import json
import os
import sys
from datetime import datetime

release = os.environ["INTEGRATION_BRANCH"]
failed_list = []


# function to get quay images using thr quay api call
def get_image():
    print(f"### Services : {services.strip()}")
    url = f"https://quay.io/api/v1/repository/cdis/{services}/tag/"
    print(url)
    res = requests.get(url)
    quay_result = json.loads(res.text)
    tags = quay_result["tags"]

    for tag in tags:
        if tag["name"] == release:
            print(f"{release} of {services} modified at {tag['last_modified']}")
            print(f"{release} of {services} exists")
            return
    failed_list.append(services)


# here
# key : github repo name
# value : quay image build name
repo_dict = {
    "pelican": "pelican-export",
    "docker-nginx": "nginx",
    "gen3-fuse": "gen3fuse-sidecar",
    "cloud-automation": "awshelper",
    "ACCESS-backend": "access-backend",
    "cdis-data-client": "gen3-client",
}

print("Check if the Quay Images are ready")
with open("../../repo_list.txt") as repoList:
    for repo in repoList:
        repo = repo.strip()
        services = repo
        if repo in repo_dict:
            services = repo_dict[repo]
            get_image()
            continue
        elif repo == "sower-jobs":
            print("Iterating through the list of images for sower-jobs")
            sower_jobs = [
                "metadata-manifest-ingestion",
                "get-dbgap-metadata",
                "manifest-indexing",
                "download-indexd-manifest",
                "batch-export",
            ]
            for sowerjob in sower_jobs:
                services = sowerjob.strip()
                get_image()
                continue
        get_image()

print(f"List of repos that failed the check : {failed_list}")
# if the failed_list contains any repo name
# then the job should fail and print the list
if len(failed_list) > 0:
    raise Exception(f"The following services do not have the quay image for {release}: {failed_list}")

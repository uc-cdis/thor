import os
import subprocess
# import boto3

release = os.environ.get("RELEASE_VERSION")
failed_list = []

subprocess.run(['git', 'clone', 'https://github.com/uc-cdis/cloud-automation.git'])

# Source gen3setup.sh script
subprocess.run(['source', './cloud-automation/gen3/gen3setup.sh'], shell=True, executable='/bin/bash')

# ecr = boto3.client('ecr')

def get_ecr_image(services):
    # command to run gen3 ecr check
    print("--------------------------------")
    print(f"Checking ECR image for {services}...")
    get_image_command = ['gen3', 'ecr', 'describe-image', services, release]
    try: 
        image = subprocess.run(get_image_command, capture_output=True, text=True)
        if image.returncode == 0:
            print(f"Image {release} exists in repository {services}")
            print(f"Image Details : {image.stdout}")
    except subprocess.CalledProcessError:
        print(f"ECR image with tag '{release}' does not exist in ECR repository '{services}'")
        failed_list.append(services)
    # try:
    #     response = ecr.describe_images(
    #         repositoryName='gen3/{services}', ## cant accept '/' only accepts '-' or '_'
    #         imageIds=[{'imageTag': release}]
    #     )
    #     image_info = response['imageDetails'][0]
    #     print(f"ECR image with tag '{release}' exists in repository 'gen3/{services}")
    #     print(f"Image Tag: (image_info['imageTags'])")
    #     return True
    # except ecr.exceptions.ImageNotFoundException:
    #     print(f"ECR image with tag '{release}' does not exist in repository 'gen3/{services}")
    #     return False

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
        if repo in repo_dict:
            services = repo_dict[repo]
            get_ecr_image(services)
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
                get_ecr_image(services)
                continue
    else:
        services = repo
        get_ecr_image(services)

print(f"List of repos that failed the check : {failed_list}")
# if the failed_list contains any repo name
# then the job should fail and print the list
if failed_list:
    raise Exception(f"The following services do not have the ECR image for {release}: {failed_list}")
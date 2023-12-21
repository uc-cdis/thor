import os
import boto3

release = os.environ.get("RELEASE_VERSION")
failed_list = []

ecr = boto3.client('ecr')

def get_ecr_image(services):
    # command to run gen3 ecr check
    try:
        response = ecr.describe_images(
            repositoryName=f'gen3/{services}',
            imageIds=[{'imageTag': release}]
        )
        image_info = response['imageDetails'][0]
        print(f"ECR image with tag '{release}' exists in repository 'gen3/{services}")
        print(f"Image Tag: '{image_info['imageTags']}") 
    except ecr.exceptions.ImageNotFoundException:
        print(f"ECR image with tag '{release}' does not exist in repository 'gen3/{services}")
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
            for sower_job in sower_jobs:
                services = sower_job.strip()
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
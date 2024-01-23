import os
import boto3

release = os.environ.get("INTEGRATION_BRANCH")
failed_list = []

ecr = boto3.client('ecr')

def delete_ecr_image(services):
    try:
        # check if the image exists in ECR
        print("--------------------------------")
        print(f"Checking branch {release} for repository gen3/{services} ...")
        check_image = ecr.describe_images(
            repositoryName=f'gen3/{services}',
            imageIds=[{'imageTag': release}]
        )
        image = check_image['imageDetails'][0]
        print(f"Image '{release}' exists in repository 'gen3/{services}")
        # if the image is present, delete the image
        print(f"Deleting the image '{release}' ...")
        ecr.batch_delete_image(
            repositoryName=f'gen3/{services}',
            imageIds=[{'imageTag': release}]
        )
        print(f"Image {release} has been deleted from repository gen3/{services}")
    except ecr.exceptions.ImageNotFoundException:
        print(f"Image '{release}' doesn't not exist in repository 'gen3/{services}', so cannot delete the image '{release}'")
        failed_list.append(services)
    except Exception as e:
        print(f"Error: {e}")

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

with open("../../repo_list.txt") as repoList:
    for repo in repoList:
        repo = repo.strip()
        if repo in repo_dict:
            services = repo_dict[repo]
            delete_ecr_image(services)
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
                delete_ecr_image(services)
                continue
        else:
            services = repo
            delete_ecr_image(services)

print(f"List of repos that failed the check : {failed_list}")
# if the failed_list contains any repo name
# then the job should fail and print the list
if failed_list:
    raise Exception(f"Couldn't delete Image {release} for repository: {failed_list}")

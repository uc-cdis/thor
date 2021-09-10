import requests
from git import Repo
import random
from random import randint
import json
import time
import sys
import os
import shutil
from datetime import datetime
from datetime import timedelta


def create_and_merge_a_pr(GITHUB_USERNAME, useremail, repo, GITHUB_TOKEN, pr_description, merge_datetime_str):
    # clone repo
    print(f"### ##cloning {repo}...")
    git_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{repo}.git"
    saved_path = f"workspace/{repo.split('/')[1]}"
    cloned_repo = Repo.clone_from(git_url, saved_path)
    # config writer
    cloned_repo.config_writer().set_value("user", "name", GITHUB_USERNAME).release()
    cloned_repo.config_writer().set_value("user", "email", useremail).release()
    # create a new branch
    pr_head = f"{pr_description.replace(' ', '')}_{time.time_ns()}"
    cloned_repo.git.checkout('-b', pr_head)
    print(f"### ##created a new branch: {pr_head}")
    # create a new file
    filename = f"{pr_head}.txt"
    completeName = os.path.join(saved_path, filename)
    newfile = open(completeName, "w")
    newfile.write(pr_description)
    newfile.close()
    print(f"### ##created a new file {filename}")
    # commit change
    cloned_repo.git.add(filename)
    cloned_repo.index.commit(f"add {pr_description}")
    print(f"### ##committed new change by {GITHUB_USERNAME}")
    # push change
    origin = cloned_repo.remote(name="origin")
    cloned_repo.create_head(pr_head)
    origin.push(pr_head)
    print("### ##pushed new change")

    
    # post request to create a pr
    request_url = f"https://api.github.com/repos/{repo}/pulls"
    headers = {"Authorization":f"token {GITHUB_TOKEN}", "Accept":"application/vnd.github.v3+json"}
    payload_data = {"head":pr_head,"base":"main", "title":pr_head,"body":pr_description}

    try:
        response = requests.post(request_url,
                                headers = headers,
                                json = payload_data)

        if (response.status_code == 201):
            # get pr link
            pr_url = json.loads(response.text)['html_url']
            pr_num = json.loads(response.text)['number']
            print(f"### ##Pull request created. Check here: {pr_url}")
        else:
            print(f"Pull request failed with {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    # post request to merge the pr
    time.sleep(10)
    request_url = f"https://api.github.com/repos/{repo}/pulls/{pr_num}/merge"
    headers = {"Authorization":f"token {GITHUB_TOKEN}", "Accept":"application/vnd.github.v3+json"}
    payload_data = {"commit_title":pr_head}

    try:
        response = requests.post(request_url,
                                headers = headers,
                                json = payload_data)

        if (response.status_code == 200):
            # get pr link
            pr_commit_sha = json.loads(response.text)['sha']
            print(f"### ##Pull request {pr_head} merged. sha: {pr_commit_sha}")
        else:
            print(f"Pull request can't be merged because {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    # change the commit time of merging pr
    # checkout to main branch and pull
    cloned_repo.git.checkout('main')
    origin.pull()
    os.chdir(saved_path)
    os.system(f"GIT_COMMITTER_DATE=\"{merge_datetime_str}\" git commit --amend --no-edit --date \"{merge_datetime_str}\"")

    # delete cloned repo folder
    try:
        shutil.rmtree(saved_path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def simulate_prs(repo_list, dev_dictionary, description_list, nums_of_pr_to_create, merge_date_for_test):    
    for i in range(0, nums_of_pr_to_create):
        select_repo = random.choice(repo_list)
        select_username, select_useremail = random.choice(list(dev_dictionary.items()))
        GITHUB_TOKEN = os.environ[f"{select_username}_GITHUB_TOKEN"]
        select_description = random.choice(description_list)
        # for half of the prs, merge them before the test date
        # for the other half, merge them after the test date
        if i < nums_of_pr_to_create/2:
            merge_datetime = datetime.strptime(merge_date_for_test, "%d %b %y %z") - timedelta(hours=randint(0,48))
        else:
            merge_datetime = datetime.strptime(merge_date_for_test, "%d %b %y %z") + timedelta(hours=randint(0,48))
        # convert datetime to string
        merge_datetime_str = datetime.strftime(merge_datetime, "%a %d %b %Y %H:%M:%S %z")
        create_and_merge_a_pr(select_username, select_useremail, select_repo, GITHUB_TOKEN, select_description, merge_datetime_str)
        # sleep 20 seconds after each pr created and merged
        if i < nums_of_pr_to_create - 1:
            time.sleep(20)

def convert_parameters(parameter):
    if('{' in parameter):
        return json.loads(parameter)
    else:
        return list(parameter.split(','))
    
def main():
    repo_list = convert_parameters(os.environ["repo_list"])
    dev_dictionary = convert_parameters(os.environ["dev_dictionary"])
    description_list = convert_parameters(os.environ["description_list"])
    nums_of_pr_to_create = int(os.environ["nums_of_pr_to_create"])
    merge_date_for_test = os.environ["merge_date_for_test"]
    simulate_prs(repo_list, dev_dictionary, description_list, nums_of_pr_to_create, merge_date_for_test)

if __name__ == "__main__":
    main()

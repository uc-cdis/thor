# the aim of this script
# go through the list of jobs and get the parameters
# store the job name as key and parameter as value in a dictionary

import requests
import json
import os
import logging

jenkins_user = os.environ["JENKINS_USERNAME"].strip()
jenkins_pass = os.environ["JENKINS_API_TOKEN"].strip()

job_dict = {}


def get_parameters(jobname):
    logging.info(f"for job {jobname}")
    parameter_list = []
    jenkins_url = (
        f"https://jenkins2.planx-pla.net/view/thor-jobs/job/{jobname}/api/json"
    )
    print(jenkins_url)
    req = requests.get(jenkins_url, auth=(jenkins_user, jenkins_pass))
    try:
        metadata = json.loads(req.text)
        for action in metadata["actions"]:
            if "parameterDefinitions" in action:
                for parameter in action["parameterDefinitions"]:
                    parameter_list.append(parameter["name"])
                print("Parameters : ", parameter_list)
        job_dict[jobname] = parameter_list
    except KeyError as e:
        print(e)


job_list = []
jobs = requests.get(
    "https://jenkins2.planx-pla.net/view/thor-jobs/api/json",
    auth=(jenkins_user, jenkins_pass),
)
joblist = json.loads(jobs.text)
for job_name in joblist["jobs"]:
    # print(jobname['name'])
    job_list.append(job_name["name"])

for name in job_list:
    print("--------")
    print(name)
    get_parameters(name)
print("####")
print("Jobs with Paramters:", job_dict)

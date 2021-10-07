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
    # getting the metadata from the job_name url and creating a parameter_list from it
    req = requests.get(jenkins_url, auth=(jenkins_user, jenkins_pass))
    try:
        metadata = json.loads(req.text)
        for action in metadata["actions"]:
            if "parameterDefinitions" in action:
                for parameter in action["parameterDefinitions"]:
                    parameter_list.append(parameter["name"])
                print("Parameters : ", parameter_list)
        # adding the jobname and the parameter list to the job_dict
        job_dict[jobname] = parameter_list
    except KeyError as e:
        print(e)


# def validate_params(metadata_file):


job_list = []
jobs = requests.get(
    "https://jenkins2.planx-pla.net/view/thor-jobs/api/json",
    auth=(jenkins_user, jenkins_pass),
)
joblist = json.loads(jobs.text)
# this is iterating through the joblist and deriving the name of the jobs
# and appending just the names to job_list
for job_name in joblist["jobs"]:
    job_list.append(job_name["name"])

# here, we are iterating through the job_list
# and calling get_parameter() on the name of the job
for name in job_list:
    print("--------")
    print(name)
    get_parameters(name)
print("#### Jobs with Paramters:", job_dict)
fp = open("metadata.json", "w")
json.dump(job_dict, fp, indent=4)
fp.close()

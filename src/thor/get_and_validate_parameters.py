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
config_dict = {}

# getting parameters from the the jenkins job list
def get_parameters(jobname):
    logging.info(f"for job {jobname}")
    parameter_list = []
    jenkins_url = (
        f"https://jenkins2.planx-pla.net/view/thor-jobs/job/{jobname}/api/json"
    )
    # print(jenkins_url)
    # getting the metadata from the job_name url and creating a parameter_list from it
    req = requests.get(jenkins_url, auth=(jenkins_user, jenkins_pass))
    try:
        metadata = json.loads(req.text)
        for action in metadata["actions"]:
            if "parameterDefinitions" in action:
                for parameter in action["parameterDefinitions"]:
                    parameter_list.append(parameter["name"])
                # print("Parameters : ", parameter_list)
        # adding the jobname and the parameter list to the job_dict
        job_dict[jobname] = parameter_list
    except KeyError as e:
        print(e)


# source of truth for comparision
# get config_dict from the thor_config file
def get_thor_config_dict():
    with open("thor_config.json", "r") as f:
        data = json.load(f)
        for step in data:
            params_list = []
            name = data[step]["job_name"]
            for params in data[step]["job_params"]:
                params_list.append(params)
            config_dict[data[step]["job_name"]] = params_list


# validating if the two dicts have same key-value pair
# if not
def validate_config(a, b):
    uncommon_key = {}
    for key in a:
        if (key in b) and (a[key] != b[key]):
            uncommon_key[key] = b[key]
    print("Uncommon:", uncommon_key)
    print("Length of uncommon key dict : ", len(uncommon_key))


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
    get_parameters(name)
# print("#### Jobs with Paramters:", job_dict)
get_thor_config_dict()
validate_config(config_dict, job_dict)

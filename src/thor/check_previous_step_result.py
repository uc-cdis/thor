import requests
import json
import os

'''
Parameters:
String paramter: base_jenkins_url
                eg. "jenkins.planx-pla.net"
String paramter: name_of_the_job
                eg. "push-gen3-monthly-release-images-to-aws-ecr"
String parameter: expected_release_version
                eg. 2021.05
String paramter: username          
String paramter: jenkins_api_token
'''

base_jenkins_url = os.environ["base_jenkins_url"]
name_of_the_job = os.environ["name_of_the_job"]
jenkins_api_token = os.environ["jenkins_api_token"]
username = os.environ["username"]
expected_release_version = os.environ["expected_release_version"]

def check_previous_step_result(base_jenkins_url, name_of_the_job, 
    jenkins_api_token, username, expected_release_version):
    release_version = "UNKNOWN"
    result = "UNKNOWN"

    url = f"https://{base_jenkins_url}/job/{name_of_the_job}/lastBuild/api/json"
    try:
        jsonOutput = requests.get(url, auth=(username,jenkins_api_token)).text
        # get release version
        for action in json.loads(jsonOutput)['actions']:
            if 'parameters' in action:
                for parameter in  action['parameters']:
                    if parameter['name'] == 'RELEASE_VERSION':
                        release_version = parameter['value']
        print(f"### ##The release version for the lasted build is {release_version}")
        #get result
        result = json.loads(jsonOutput)['result']
        print(f"### ##The result for the lasted build is {result}")
    except Exception as e:
        print(f"### ## Something went wrong: {e}")

    if release_version == expected_release_version:
        return result
    else:
        raise Exception(f"The release version of latest job is {release_version} while the expected version is {expected_release_version}")

    # TODO: store the task result to database

check_previous_step_result(base_jenkins_url, name_of_the_job, jenkins_api_token, username, expected_release_version)
import os
import logging
import requests
import json

# import jenkins

from thor.maestro.baton import JobManager

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class JenkinsJobManager(JobManager):
    def __init__(
        self, base_jenkins_url="https://jenkins2.planx-pla.net/job/say-hello/", **kwargs
    ):
        """
    Creates Jenkins Job Manager API client
    """
        # use parent default
        self.base_jenkins_url = base_jenkins_url
        self.jenkins_api_token = "****"
        self.jenkins_username = "***"
        if len(kwargs):
            # pass everything else to parent
            super().__init__(**kwargs)
        else:
            # use parent default
            super().__init__()

    def run_job(self, job_name, job_parameters, token):
        """This function takens in a job_name and job parameters to remotely trigger a Jenkins job.
            It further calls another function, assemble_url, that transforms the parameters dictionary 
            into a buildWithParameters URL. To acheive this, the function concatenates an empty string with
            the return value of assemble_url. An exception is raised if the concatenation fails."""
        print(f"running jenkins job {job_name}")
        print(f"parameters {job_parameters}")
        auth = (self.jenkins_username, self.jenkins_api_token)
        try:
            response = requests.post(self.base_jenkins_url, auth=auth)
            print(f"reponse status code: {response.status_code}")
            # Capture parameters by reading the metadata of the job_name and see if it matches the keys of the dict.
            parameterized_url = ""
            parameterized_url = parameterized_url + self.assemble_url(
                job_name, job_parameters, token
            )
            # Checks whether or not the url was assembled correctly
            if parameterized_url == "":
                raise Exception(f"The parametreized URL could not be assembled.")
            else:
                print(f"The parameterized url is: {parameterized_url}.")
        except Exception:
            # TODO:
            print("Failed to establish a connection.")
            print(Exception)
        if parameterized_url == "":
            print(f"The parametreized URL could not be assembled.")

        # TODO: write python code to execute something like this
        # curl -L -s -o /dev/null -w "%{http_code}" -u user:$JENKINS_API_TOKEN "http://localhost:6579/job/this-is-a-test/buildWithParameters?token=<your_job_secret_token>&THE_NAME=William&RELEASE_VERSION=2021.09"

    def assemble_url(self, job_name, job_parameters, token):
        """Takes in job_parameters to assemble a URL that transforms the parameters dictionary 
        into a buildWithParameters URL containing the sequence of parameter key and value."""
        url = ""
        dictionary = job_parameters
        keys_parameters = dictionary.keys()
        values_parameters = dictionary.values()
        keys_list = list(keys_parameters)
        values_list = list(values_parameters)
        # TODO: generalize for more keys and values
        for k in job_parameters:
            if k == "BRANCH_NAME":
                url = f"https://jenkins2.planx-pla.net/job/{job_name}/buildWithParameters?token={token}&{keys_list[0]}={values_list[0]}"
            elif k != "FORK_FROM":
                url = f"https://jenkins2.planx-pla.net/job/{job_name}/buildWithParameters?token={token}&{keys_list[0]}={values_list[0]}&{keys_list[1]}={values_list[1]}"
            else:
                url = f"https://jenkins2.planx-pla.net/job/{job_name}/buildWithParameters?token={token}&{keys_list[0]}={values_list[0]}"
        # print(f"assembled url is {url}")
        # Return statement is for when this function will be called elsewhere.
        return url

    def check_result_of_job(self, job_name, expected_release_version):
        release_version = "UNKNOWN"
        print(f"checking the results of the jenkins job {job_name}")
        url = f"https://{self.base_jenkins_url}/job/{job_name}/lastBuild/api/json"
        try:
            jsonOutput = requests.get(
                url, auth=(self.jenkins_username, self.jenkins_api_token)
            ).text
            # get release version
            for action in json.loads(jsonOutput)["actions"]:
                if "parameters" in action:
                    for parameter in action["parameters"]:
                        if parameter["name"] == "RELEASE_VERSION":
                            release_version = parameter["value"]
            print(
                f"### ##The release version for the lasted build is {release_version}"
            )
            # get result
            result = json.loads(jsonOutput)["result"]
            print(f"### ##The result for the lasted build is {result}")
        except Exception as e:
            print(f"response: {jsonOutput}")
            print(f"### ## Something went wrong: {e}")

        if release_version == expected_release_version:
            return result
        else:
            raise Exception(
                f"The release version of latest job is {release_version} while the expected version is {expected_release_version}"
            )

    # TODO: store the task result to database


"""#1 is to check for fork main"""
if __name__ == "__main__":
    jjm = JenkinsJobManager()
    paramsDict = {
        "RELEASE_VERSION": "2021.10",
        "FORK_FROM": "main",
    }

    jjm.run_job("say-hello", paramsDict, "***")

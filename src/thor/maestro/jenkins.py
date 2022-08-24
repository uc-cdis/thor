import os
import logging
import requests
import json
import datetime

from thor.maestro.baton import JobManager
from thor.dao.task_dao import create_task, lookup_task_key, update_task
from thor.dao.release_dao import release_id_lookup_class

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class JenkinsJobManager(JobManager):
    def __init__(self, jenkins_instance, **kwargs):
        """
    Creates Jenkins Job Manager API client
    """
        # use parent default
        self.base_jenkins_url = f"https://{jenkins_instance}.planx-pla.net/job"
        # Expects form "https://{jenkins_instance}.planx-pla.net/job"
        self.jenkins_api_token = os.environ["JENKINS_API_TOKEN"].strip()
        self.jenkins_username = os.environ["JENKINS_USERNAME"].strip()
        self.jenkins_job_token = os.environ["JENKINS_JOB_TOKEN"].strip()
        if len(kwargs):
            # pass everything else to parent
            super().__init__(**kwargs)
        else:
            # use parent default
            super().__init__()

    def recursive_run_job(self, step_deets, jobs_and_schedules):
        result = self.run_job(step_deets["job_name"], step_deets["job_params"])
        if "run_next" in step_deets:
            self.recursive_run_job(
                jobs_and_schedules[step_deets["run_next"]], jobs_and_schedules
            )
        else:
            log.warn(
                "this step does not have a 'run_next' property. So there is nothing left to do."
            )

    def run_job(self, job_name, job_parameters):
        """This function takens in a job_name and job parameters to remotely trigger a Jenkins job.
            It further calls another function, assemble_url, that transforms the parameters dictionary 
            into a buildWithParameters URL. To achieve this, the function concatenates an empty string with
            the return value of assemble_url. An exception is raised if the concatenation fails."""
        log.info(f"running jenkins job {job_name}")
        log.info(f"parameters {job_parameters}")
        auth = (self.jenkins_username, self.jenkins_api_token)
        try:
            # TODO: improve url assembly validation
            full_url = self.assemble_url(job_name, job_parameters)
            response = requests.post(full_url, auth=auth)
            # this request should operate like the curl command below
            # curl -L -s -o /dev/null -w "%{http_code}" -u user:$JENKINS_API_TOKEN "http://localhost:6579/job/this-is-a-test/buildWithParameters?token=<your_job_secret_token>&THE_NAME=William&RELEASE_VERSION=2021.09"
            log.debug(f"reponse status code: {response.status_code}")
            # Capture parameters by reading the metadata of the job_name and see if it matches the keys of the dict.

        except requests.exceptions.HTTPError as httperr:
            log.error(
                f"request to {self.base_jenkins_url}/{job_name} failed due to the following error: {e}"
            )

    def assemble_url(self, job_name, job_parameters):
        """Takes in job_parameters to assemble a URL that transforms the parameters dictionary 
        into a buildWithParameters URL containing the sequence of parameter key and value."""
        url = f"{self.base_jenkins_url}/{job_name}/buildWithParameters?token={self.jenkins_job_token}"
        for k, v in job_parameters.items():
            url += f"&{k}={v}"
        # omitting the token from the url
        sanitized_url = (
            url[0 : int(url.index("token"))] + url[url.index("&") : len(url)]
        )
        log.debug(f"the url has been assembled: {sanitized_url}")
        return url

    def check_result_of_job(self, job_name, expected_release_version):
        release_version = "UNKNOWN"
        print(f"checking the results of the jenkins job {job_name}")
        log.info(f"Checking results of jenkins job {job_name}. ")
        url = f"https://{self.base_jenkins_url}/job/{job_name}/lastBuild/api/json"
        jsonOutput = None
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
            log.info(
                f"Latest version of {job_name} is {release_version}, and the result is {result}. "
            )

        except Exception as e:
            print(f"response: {jsonOutput}")
            print(f"### ## Something went wrong: {e}")
            log.info(
                f"Encountered error when accessing {job_name}: \n \
                Exception: {e} \n \
                    Full response: {jsonOutput}. "
            )

        if release_version == expected_release_version:
            return result
        else:
            raise Exception(
                f"The release version of latest job is {release_version} while the expected version is {expected_release_version}"
            )

    def write_task_result(self, job_name, expected_release_version, step_num):
        """ Uses check_result_of_job to ... check the result of the job. 
        Uses parameters given above (self, str job_name, str expected_r_v. 
        Once result is gotten, uses task_dao's create_task and 
        release_dao's release_id_lookup to create an appropriate task. 
        
        Note: If a job with the same name and release_id already 
        exists within the database, we update the result in-place
        instead of creating a new Task. """

        result = self.check_result_of_job(job_name, expected_release_version)
        r_id_lookup_class = release_id_lookup_class()
        corresponding_release_id = r_id_lookup_class.release_id_lookup(
            expected_release_version
        )

        expected_key = lookup_task_key(job_name, corresponding_release_id)

        # If expected_key returns None, then there is no job with the
        # corresponding job_name and release_version.
        if expected_key:
            update_task(expected_key, "status", result)
        else:
            create_task(job_name, result, corresponding_release_id, step_num=step_num)


if __name__ == "__main__":
    jjm = JenkinsJobManager()
    # paramsDict = {
    #     "RELEASE_VERSION": "2021.09",
    #     "FORK_FROM": "main",
    # }
    # jjm.run_job("say-hello", paramsDict)
    # print("\nCHECKRESULT\n", jjm.check_result_of_job("say-hello", "2021.09"), "\n\n")

    test_task_name = "Update CI env with the latest integration branch"
    test_task_version = "2021.09"

    jjm.write_task_result(test_task_name, test_task_version)

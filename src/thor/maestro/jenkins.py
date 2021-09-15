import os
import logging
import requests
import json
import datetime

from thor.maestro.baton import JobManager
from thor.dao.task_dao import create_task
from thor.dao.release_dao import look_upper


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class JenkinsJobManager(JobManager):
    def __init__(self, base_jenkins_url="jenkins2.planx-pla.net", **kwargs):
        """
    Creates Jenkins Job Manager API client
    """
        # use parent default
        self.base_jenkins_url = base_jenkins_url
        self.jenkins_api_token = os.environ["JENKINS_API_TOKEN"].strip()
        self.jenkins_username = os.environ["JENKINS_USERNAME"].strip()
        if len(kwargs):
            # pass everything else to parent
            super().__init__(**kwargs)
        else:
            # use parent default
            super().__init__()

    def run_job(self, job_name, job_parameters):
        log.info(f"running jenkins job {job_name}")
        log.info(f"parameters {job_parameters}")
        log.info(f"job invoked at: {datetime.datetime.now()}")
        # TODO: Capture parameters by reading the metadata of the job_name and see if it matches the keys of the dict
        # TODO: write python code to execute something like this
        # curl -L -s -o /dev/null -w "%{http_code}" -u user:$JENKINS_API_TOKEN "http://localhost:6579/job/this-is-a-test/buildWithParameters?token=<your_job_secret_token>&THE_NAME=William&RELEASE_VERSION=2021.09"
        return f"result from {job_name}"

    def check_result_of_job(self, job_name, expected_release_version):
        release_version = "UNKNOWN"
        print(f"checking the results of the jenkins job {job_name}")
        log.info(f"Checking results of jenkins job {job_name}. ")
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

    def write_task_result(self, job_name, expected_release_version):
        """ Uses check_result_of_job to ... check the result of the job. 
        Uses parameters given above (self, str job_name, str expected_r_v. 
        Once result is gotten, uses task_dao's create_task and 
        release_dao's release_id_lookup to create an appropriate task. 
        Note: If a job with the same name and release_id already 
        exists within the database, we update the result in-place
        instead of creating a new Task. """

        result = self.check_result_of_job(job_name, expected_release_version)
        lu = look_upper()
        create_task(job_name, result, lu.release_id_lookup(expected_release_version))

        return True

    # TODO: store the task result to database


if __name__ == "__main__":
    jjm = JenkinsJobManager()
    paramsDict = {
        "RELEASE_VERSION": "2021.09",
        "FORK_FROM": "main",
    }
    jjm.run_job("say-hello", paramsDict)
    print("\nCHECKRESULT\n", jjm.check_result_of_job("say-hello", "2021.09"), "\n\n")

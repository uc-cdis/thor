import os
import logging
import requests
import json
from thor.maestro.baton import JobManager

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

    def run_job(self, job_name):
        print(f"running jenkins job {job_name}")
        # TODO: write python code to execute something like this
        # curl -L -s -o /dev/null -w "%{http_code}" -u user:$JENKINS_API_TOKEN "http://localhost:6579/job/this-is-a-test/buildWithParameters?token=<your_job_secret_token>&THE_NAME=William&RELEASE_VERSION=2021.09"
        pass

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


if __name__ == "__main__":
    jjm = JenkinsJobManager()
    jjm.run_job("say-hello")
    jjm.check_result_of_job("say-hello", "2020.12")

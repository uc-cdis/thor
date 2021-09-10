import os
import logging
from thor.maestro.baton import JobManager

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class JenkinsJobManager(JobManager):
    def __init__(self):
        """
    Creates Jenkins Job Manager API client
    """
        # use parent default
        super().__init__()

    def runJob(self, job_name):
        print(f"running jenkins job {job_name}")
        # TODO: write python code to execute something like this
        # curl -L -s -o /dev/null -w "%{http_code}" -u user:$JENKINS_API_TOKEN "http://localhost:6579/job/this-is-a-test/buildWithParameters?token=<your_job_secret_token>&THE_NAME=William&RELEASE_VERSION=2021.09"
        pass


if __name__ == "__main__":
    jjm = JenkinsJobManager()
    jjm.runJob("this-is-a-test")

from abc import ABC, abstractmethod
import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class JobManager(ABC):
    """
  Interface for building custom Job Managers.
  This interface should unify the functions used to orchestrate a release, with tasks such as:
    * Initialize release in ticketing systems
    * Interact with a source code management API (e.g., Github) to cut/merge branches and tag repos
    * Verify the results of CI tests and load tests
    * Generate Release notes
    * Verify builds/docker images
    * Publish release (by collaborating with a Notifications module -> Slack, Email, etc.)
  """

    # borg pattern -- sharing state throughout all instances
    _JOB_MANAGER_CONFIG = {}
    # default option but subject to override by subclasses (e.g., 'monthly', 'every3weeks', 'every2weeks', 'weekly')
    _JOB_MANAGER_CONFIG["release_cadence"] = "monthly"

    @abstractmethod
    def __init__(self, release_cadence=None):
        """
    Setup THOR's default config
    """
        self.release_cadence = (
            release_cadence
            if release_cadence
            else self._JOB_MANAGER_CONFIG["release_cadence"]
        )

    def do_polling(
        self,
        expected_result,
        number_of_attempts,
        sleep_cycle,
        function_to_repeat,
        *vargs,
    ):
        for i in range(0, number_of_attempts):
            result = function_to_repeat(vargs)
            if result == expected_result:
                log.info(f"The job finally returned {expected_result}. proceed.")
                return result
            else:
                log.info(
                    f"The job did not return {expected_result} yet. Sleeping for {sleep_cycle}..."
                )
                time.sleep(sleep_cycle)

        log.error(
            "Maximum number of attempts reached. The job did never returned the expected result."
        )
        return None

    @abstractmethod
    def run_job(self, job_name):
        print("super class run_job. Not implemented.")

    @abstractmethod
    def check_result_of_job(self, job_name):
        print("super class check_result_of_job. Not implemented.")

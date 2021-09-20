import os
import sys
import time
import asyncio
import logging
import json
import datetime as dt
from aiocron import crontab
from concurrent.futures import ThreadPoolExecutor, wait

from thor.time import say_hello_test
from thor.time import proto_executor

from thor.maestro.jenkins import JenkinsJobManager

# how an administrator might go about scheduling
# specific jobs at different times.

# script folder
thor_path = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, thor_config_file):
        """
    Creates Scheduler to kick off jobs at a given point in time
    """

        with open(thor_config_file, "r") as read_file:
            self.jobs_and_schedules = json.load(read_file)

    def initialize_scheduler(self):
        loop = asyncio.new_event_loop()
        futures = []

        jjm = JenkinsJobManager()

        # Replace following block with method to schedule only the jobs with
        # fixed cron schedule.

        for jk, jv in self.jobs_and_schedules.items():
            log.info(f"iterating through job {jk}")
            # debugging
            time.sleep(1)
            if jv["schedule"]:
                job_reference = jjm.run_job
                job_args = (jv["job_name"], jv["job_params"])
                cron_input = jv["schedule"]
                futures.append(
                    self.schedule_job_cron(job_reference, job_args, cron_input, loop)
                )
            else:
                log.info(
                    f"no schedule set for job {jk}, it must run immediately once the previous job is successful."
                )

        # Replace following code with methods to call the Jenkins job and
        # keep polling Jenkins until we get a successful run of the newest job.

        print("RUNNING LOUDLY")

        for f in futures:

            print("waiting until", f, "\n", dt.datetime.now())
            loop.run_until_complete(f)

            print(f)
            # jjm.check_result_of_job()

            if f.done():
                log.info(f"### ## job {str(f)} executed as per schedule.")

    def schedule_job_cron(self, job_reference, job_args, cron_input, loop):
        """ Schedules a job with a cron_input """

        # assemble job_name for logging purposes
        job_name = job_args[0]

        # snippet of code from
        # https://python.hotexamples.com/examples/aiocron/-/crontab/python-crontab-function-examples.html
        t = crontab(cron_input, func=job_reference, args=job_args, loop=loop)
        log.info(f"successfully scheduled job {job_name}.")

        future = asyncio.ensure_future(t.next(), loop=loop)
        return future


if __name__ == "__main__":
    sch = Scheduler("test_thor_config.json")
    sch.initialize_scheduler()

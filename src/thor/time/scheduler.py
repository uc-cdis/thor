import os
import sys
import time
import asyncio
import logging
import json
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

        for jk, jv in self.jobs_and_schedules.items():
            log.info(f"iterating through job {jk}")
            # debugging
            time.sleep(1)
            if jv["schedule"]:
                job_reference = JenkinsJobManager().run_job
                job_args = (jv["job_name"], jv["job_params"])
                cron_input = jv["schedule"]
                futures.append(
                    self.schedule_job_cron(job_reference, job_args, cron_input, loop)
                )
            else:
                log.info(
                    f"no schedule set for job {jk}, it must run immediately once the previous job is successful."
                )

        for f in futures:
            loop.run_until_complete(f)
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
    sch = Scheduler()
    sch.initialize_scheduler()

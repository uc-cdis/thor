import os
import sys
import time
import asyncio

import nest_asyncio

nest_asyncio.apply()

import logging
import json
import datetime
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
log.propagate = False


class Scheduler:
    def __init__(self, thor_config_file):
        """
    Creates Scheduler to kick off jobs at a given point in time
    """
        self.job_manager_instance = None
        with open(thor_config_file, "r") as read_file:
            self.jobs_and_schedules = json.load(read_file)

    def initialize_scheduler(self, jenkins_instance):
        loop = asyncio.new_event_loop()

        print("initialize_scheduler called")
        jjm = JenkinsJobManager(jenkins_instance)
        self.job_manager_instance = jjm

        # Replace following block with method to schedule only the jobs with
        # fixed cron schedule.

        futures_dict_verbose = {}
        for step, step_info_dict in self.jobs_and_schedules.items():
            # step is the first-level job name - step1, step2, etc.
            # info_dict is the dict that contains all the other interesting info
            # info_dict is like {job_name: , job_params:{ } , schedule: , run_next: }

            cron_input = step_info_dict["schedule"]

            if cron_input:
                future_job = self.schedule_job_cron(step_info_dict, loop)

                futures_dict_verbose[step] = {
                    "future_reference": future_job,
                    "step_info": step_info_dict,
                }

            else:
                log.info(f"No schedule for step {step}")

        # Now, we should have a complete futures_dict_verbose.
        # This file should contain all the info that we need for the next stage of the job.

        # Replace following code with methods to call the Jenkins job and
        # keep polling Jenkins until we get a successful run of the newest job.

        print("FDV created")
        for step_name, futures_dict_info in futures_dict_verbose.items():

            try:
                log.debug("time:", datetime.datetime.now())
            except TypeError:
                # this raises an error when we are faking the time, just ignore it
                pass

            loop.run_until_complete(futures_dict_info["future_reference"])

            print("### ### HERE!!! THE JOB WAS EXECUTED!!!")
            if "run_next" in futures_dict_info["step_info"]:
                next_step_key = futures_dict_info["step_info"]["run_next"]

                # only execute the next step if it actually exist in the jobs_and_schedules dict
                if next_step_key in self.jobs_and_schedules:
                    # example, after executing step 1
                    # we retrieve the run_next string from its step_info dictionary
                    # which will be step2, and then we use that as a lookup key
                    # to fetch the step_info of step2
                    print(f"### ## self.jobs_and_schedules: {self.jobs_and_schedules}")
                    jjm.recursive_run_job(
                        self.jobs_and_schedules[futures_dict_info["step_info"]["run_next"]],
                        self.jobs_and_schedules,
                    )

            log.debug(f"job step {step_name} is complete. ")
            job_name = futures_dict_info["step_info"]["job_name"]
            # expected_version = "2021.09"  # Temporary for testing purposes

            # while True:
            #     time.sleep(5)
            #     result = JenkinsJobManager().check_result_of_job(
            #         job_name, expected_version
            #     )

            # print(result)
        print("all done here in sched")

    def schedule_job_cron(self, step_info_dict, loop):
        """ Schedules a job with a cron_input """

        job_reference = self.job_manager_instance.run_job
        job_name = step_info_dict["job_name"]
        job_params = step_info_dict["job_params"]
        print("job_params", job_params)
        schedule = step_info_dict["schedule"]
        # assemble job_name for logging purposes

        job_args = (job_name, job_params)
        # snippet of code from
        # https://python.hotexamples.com/examples/aiocron/-/crontab/python-crontab-function-examples.html
        t = crontab(schedule, func=job_reference, args=job_args, loop=loop)
        log.info(f"successfully scheduled job {job_name}.")

        future = asyncio.ensure_future(t.next(), loop=loop)
        return future


if __name__ == "__main__":
    config_file = "thor_config.json"
    jenkins_instance = "jenkins"
    if "RUNNING_IN_QAPLANETV1" not in os.environ:
        config_file = f"test_{config_file}"
        jenkins_instance = "jenkins2"

    sch = Scheduler(config_file)
    sch.initialize_scheduler(jenkins_instance)

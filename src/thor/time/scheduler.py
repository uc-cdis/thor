import os
import sys
import asyncio
import logging
from aiocron import crontab
from concurrent.futures import ThreadPoolExecutor, wait

from thor.time import say_hello_test
from thor.time import proto_executor

# how an administrator might go about scheduling
# specific jobs at different times.

# script folder
thor_path = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)


class Scheduler:
    def __init__(
        self, feature_freeze_cycle="2nd_friday", code_freeze_cycle="4th_friday"
    ):
        """
    Creates Scheduler to kick off jobs at a given point in time
    """
        self.feature_freeze_cycle = feature_freeze_cycle
        self.code_freeze_cycle = code_freeze_cycle

    def schedule_job_cron(self, job_reference, cron_input):
        """ Schedules a job with a cron_input """

        # assemble job_name for logging purposes
        function_name = job_reference.__name__
        module_name = sys.modules[job_reference.__module__]
        job_name = f"{module_name}.{function_name}"

        # snippet of code from
        # https://python.hotexamples.com/examples/aiocron/-/crontab/python-crontab-function-examples.html
        loop = asyncio.new_event_loop()

        t = crontab(cron_input, func=job_reference, loop=loop)
        log.info(f"successfully scheduled job {job_name}.")

        future = asyncio.ensure_future(t.next(), loop=loop)
        loop.run_until_complete(future)

        if future.done():
            log.info(f"### ## job {job_name} executed as per schedule.")


if __name__ == "__main__":
    sch = Scheduler()
    every_minute = "* * * * *"
    sch.schedule_job_cron(say_hello_test.say_hello, every_minute)
    every_second_friday_of_the_month = "0 21 8-15 * 5"
    sch.schedule_job_cron(proto_executor.method1, every_second_friday_of_the_month)

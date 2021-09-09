# proto_schedule

# A primitive scheduler prototype.
# Works together with proto_executor to mock
# (with very limited functionality)
# how an administrator might go about scheduling
# specific jobs at different times.

from crontab import CronTab

import proto_executor

cron = CronTab(user="henry")  # note: this has to change for different machines
job = cron.new(command="echo hello_world")

job.minute.every(1)
cron.write()


def getattr_tester(in_string):
    """ Testing python's getattr method so that 
    we can pass in strings directly instead of 
    doing like 500 if comparisons. """

    method_to_call = getattr(proto_executor, in_string)
    bingity = method_to_call()


if __name__ == "__main__":
    getattr_tester("method2")

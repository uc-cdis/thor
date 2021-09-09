# proto_schedule

# A primitive scheduler prototype.
# Works together with proto_executor to mock
# (with very limited functionality)
# how an administrator might go about scheduling
# specific jobs at different times.
import datetime as dt

from crontab import CronTab

import proto_executor

thor_path = proto_executor.save_path

cron = CronTab(user="henry")  # note: this has to change for different machines


# pe_call = "python " + thor_path + "/proto_executor.py"
# pe_job = cron.new(command=pe_call)


def schedule_job_once(job_name, schedule_time):
    """ Given the name of a python job which should be run, 
    and the time at which it should be scheduled for, uses 
    python-crontab's capabilities to schedule the job for 
    that time. 
    The python job is expected to be another python file, 
    in the form job_name.py. Do not enter the .py as part of the 
    job_name. 
    Expects job_name as string, and schedule_time as DateTime object. 
    Currently looks within thor_path for job_name. """

    new_job_call = "python " + thor_path + "/" + job_name + ".py"
    new_job = cron.new(command=new_job_call)

    new_job.setall(schedule_time)
    cron.write()


def schedule_job_repeating(job_name, schedule_time, interval):
    """ Performs the same job as schedule_job_once, 
    but works with the crontab to ensure that the job is 
    scheduled for as many times as necessary. 
    interval is expected to be a string, as one of the following:
    %hourly, %daily, %weekly, %biweekly, %monthly, %yearly. 
    """

    return True


def schedule_job_cron(job_name, cron_input):
    """ Schedules a job, using the same conventions 
    as in schedule_job_once, but takes a cron_input 
    instead of a DateTime. """

    return True


if __name__ == "__main__":
    in_five_min = dt.datetime.now() + dt.timedelta(minutes=5)

    schedule_job_once("proto_executor", in_five_min)

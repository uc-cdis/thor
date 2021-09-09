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
    @hourly, @daily, @weekly, @monthly, @yearly. 
    Will execute at the same time each hour/day/week/month/year.

    hour preserves minutes, day preserves h/m, week preserves weekday/h/m, 
    monthly preserves day-of-month and h/m, yearly preserves date and h/m. 

    TODO: Add biweekly / thor-centric option to fit needs. 

    Additional Notes:
    Relies on schedule_job_cron. Only builds the cron string in-house. 
    Possible sources of bugs / misinterpretations:
        If a job date is specified that is more than 1 period from 
        the current date, cron will execute the job in the next period
        as well as in the one thereafter, earlier than expected. 
        e.g.
            Today is Wednesday, and a weekly job is scheduled with 
            a start date of the Friday after next. 
            This method will unintuitively cause cron to run the job
            on this Friday as well as next Friday, potentially breaking things. 
                For concreteness:
                Today (Wed) is 09/08/21, Friday is 09/10/21. 
                The desired start date is 09/17/21, but cron will 
                run the job on 09/10/21 as well as 09/17/21. 
        Fixing this would involve a moderate amount of circumlocution. 
        Likely would involve calling an external job to build the weekly job 
        just before it starts, instead of immediately as is done here. 
                To follow the concrete example, a job would be called 
                next Thursday (09/16/21), causing the weekly jobs to be 
                scheduled for 09/17/21 and thereafter. 
    """

    formatted_sch_time_list = schedule_time.strftime("%m %d %H %M").split()
    [sch_mon, sch_day, sch_hr, sch_min] = formatted_sch_time_list

    cron_string_list = ["*", "*", "*", "*", "*"]

    wkday_num = schedule_time.weekday()  # convention is monday = 0

    wkday_num = (wkday_num + 1) % 7
    # necessary to adjust because cron has the convention Sunday = 0

    # suggestions to improve this welcome
    # Note: in Python 3.10, switch statements should make this less painful
    if interval == "@hourly":
        cron_string_list[0] = sch_min
    elif interval == "@daily":
        cron_string_list[0] = sch_min
        cron_string_list[1] = sch_hr
    elif interval == "@weekly":
        cron_string_list[0] = sch_min
        cron_string_list[1] = sch_hr
        cron_string_list[4] = wkday_num
    elif interval == "@monthly":
        cron_string_list[0] = sch_min
        cron_string_list[1] = sch_hr
        cron_string_list[2] = sch_day
    elif interval == "@yearly":
        cron_string_list[0] = sch_min
        cron_string_list[1] = sch_hr
        cron_string_list[2] = sch_day
        cron_string_list[3] = sch_mon

    cron_string = " ".join(cron_string_list)  # joins with space separator
    schedule_job_cron(job_name, cron_string)


def schedule_job_cron(job_name, cron_input):
    """ Schedules a job, using the same conventions 
    as in schedule_job_once, but takes a cron_input 
    instead of a DateTime. 
    
    Special note: Due to how python-crontab's setall
    works, cron_inputs can be input into schedule_job_once
    and work as expected (at least by the person using cron). 
    This behavior is unintuitive and opaque, so typechecking 
    should probably be implemented to get users to use 
    schedule_job_cron when they want to do cron things. """

    new_job_call = "python " + thor_path + "/" + job_name + ".py"
    new_job = cron.new(command=new_job_call)

    new_job.setall(cron_input)
    cron.write()


if __name__ == "__main__":
    in_five_min = dt.datetime.now() + dt.timedelta(minutes=5)
    sample_cron_text = "6 12 9 9 *"
    # schedule_job_once("proto_executor", in_five_min)
    # schedule_job_cron("proto_executor", sample_cron_text)
    schedule_job_repeating("proto_executor", in_five_min, "@hourly")

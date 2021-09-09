# proto_executor.py

# Provides sample methods for proto_schedule to
# work with and call.
# Will try to execute python read/write to sample files.

# Cygwin notes:
# "python" call works just fine with either full name (/usr/bin/python)
# or just "python". However, as crontab works from root, full name of
# the thor directory (seen here in save_path for my machine) needs to
# be specified.

import os.path

import datetime as dt

save_path = "/cygdrive/c/users/@USER/work/thor/thor/src/thor"
# !!! NOTE: PROVIDE @USER BEFORE RUNNING. save_path must also be modified
# depending on how you are running this, as well as your directory structure.
# This should eventually be passed in via environment variable,
# config file or similar.

log_file_name = "proto_log.csv"

log_file_absolute_path = os.path.join(save_path, log_file_name)


def method1():
    """when called, will write-append mode to log_file. 
    Will print out the current DateTime, along with 
    the string 'Method 1 called.' """

    log_file = open(log_file_absolute_path, "a")

    current_time = dt.datetime.now()
    out_string = str(current_time) + "  Method 1 called. \n"

    log_file.write(out_string)
    log_file.close()


def method2():
    """when called, will write-append mode to log_file. 
    Will print out the current DateTime, along with 
    the string 'Method 1 called.' 
    NOTE: Differs from method1 in that it uses 
    the local filename instead of the absolute path, 
    so I can test this in VSCode instead of in cygwin 
    because that's messier and more of a pain. """

    log_file = open(log_file_name, "a")

    current_time = dt.datetime.now()
    out_string = str(current_time) + "  Method 2 called. \n"

    log_file.write(out_string)
    log_file.close()


if __name__ == "__main__":
    method1()

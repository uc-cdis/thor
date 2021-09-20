# proto_executor.py

# Provides sample methods for scheduler to
# work with and call.
# Will try to execute python read/write to sample files.

import os
import os.path

import datetime as dt

log_file_name = "proto_log.csv"
log_file_absolute_path = os.path.join(os.getcwd(), log_file_name)


def method1():
    """when called, will write-append mode to log_file. 
    Will print out the current DateTime, along with 
    the string 'Method 1 called.' """

    log_file = open(log_file_absolute_path, "a")

    current_time = dt.datetime.now()
    out_string = str(current_time) + "  Method 1 called. \n"

    log_file.write(out_string)
    log_file.close()


if __name__ == "__main__":
    method1()

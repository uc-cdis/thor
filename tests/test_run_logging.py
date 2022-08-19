# test_run_logging.py
from requests import request
import pytest
import json
import os
from thor.maestro.bash import BashJobManager

import os.path

def test_run_shell_logging():
    """
    Tests the BashJobManager's run_shell to ensure that it writes to the proper logfile. 
    """

    bjm = BashJobManager("arbitrary")
    print(os.getcwd())
    os.chdir("tests/test_files")
    bjm.run_shell("test_run_shell_script.sh")

    # Check baseline file to make sure that the shell script was run correctly.
    result_file_name = "expected_result_for_run_shell_logging.txt"
    result_absolute_path = os.path.join(os.getcwd(), result_file_name)
    with open(result_absolute_path, "r") as read_target_file:
        log_file_name = "logfile.txt"
        log_absolute_path = os.path.join(os.getcwd(), log_file_name)
        with open(log_absolute_path, "r") as read_log_file:
            assert read_target_file.read() == read_log_file.read()
    
    os.remove(log_absolute_path)
    os.chdir("..")


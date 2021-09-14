# test_jjm_write_task_result.py
import pytest
import json
import os

import os.path

from thor.dao.task_dao import read_task
from thor.tests.clear_tables_reseed import reseed
from thor.maestro.jenkins import write_task_result

## Test writing result when there is no prior value


def test_write_no_prior():
    """ For the purposes of this test, we use an object with completely 
    novel values for each variable. This prevents any chance of overlap
    with the known values already in the database. 
    Feels bad hardcoding it, but it's a test anyway. 
    job_name should be 'liek_mudkip.lol' and version should be '-1'. """
    reseed()

    return True


## Test writing result when ther eis a prior value
## In this case, the method switches to modify-in-place value

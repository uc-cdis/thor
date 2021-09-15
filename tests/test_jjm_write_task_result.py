import pytest
import mock
import os

import os.path

from thor.maestro.jenkins import JenkinsJobManager
from thor.dao.task_dao import read_task, get_task_num
from thor.dao.clear_tables_reseed import reseed

from thor.dao.release_dao import look_upper
from thor.dao.models import Task


def returnSuccess(self, input1, input2):
    """ Returns 'success' to mock check_result_of_job. """
    return "success"


def returnThree(self, input1):
    """ Returns int 3 to mock result of release_id_lookup. """
    return 3


## Test writing result when there is no prior value
@mock.patch.object(JenkinsJobManager, "check_result_of_job", returnSuccess)
@mock.patch.object(look_upper, "release_id_lookup", returnThree)
def test_write_no_prior():
    """ For the purposes of this test, we use an object with known
    values for each variable. write_task_result expects to use 
    check_result_of_job to find its 'status' parameter, and 
    release_id_lookup to find its 'release_id' parameter. 
    
    We mock both check_result_of_job and release_id_lookup to 
    guarantee that the results will be 'success' and int(4), respectively. 
    Then, we call write_task_result with job_name 'test_job_42' and 
    expected_release_version '2002.09', which should definitely not 
    be in the table. Afterwards, we check the task with ID 0, which should
    be the task we want. We compare this task to the known task, and 
    assert that they are the same. """
    reseed()

    test_jjm = JenkinsJobManager()

    test_task_id = 0
    test_task_name = "test_job_42"
    test_task_status = "success"
    test_release_id = 3
    test_task_version = "2002.09"

    test_jjm.write_task_result(test_task_name, test_task_version)

    written_task = read_task(0)

    assert written_task.task_id == test_task_id
    assert written_task.task_name == test_task_name
    assert written_task.status == test_task_status
    assert written_task.release_id == test_release_id
    assert type(written_task) == Task


## Test writing result when there is a prior value
## In this case, the method switches to modify-in-place value


@mock.patch.object(JenkinsJobManager, "check_result_of_job", returnSuccess)
def test_write_while_prior():
    """ The objective of this test is to ensure write_task_result
    overwrites the status of a task instead of creating a new task
    when another task with the same name and release_id exists 
    within the Tasks database. 
    
    The target of this test is the Task with ID 10:
        ID: '10', Name: 'Update CI env with the latest integration branch', 
        Status: 'in progress', Release ID: '3'

        The corresponding version for Release ID is 2021.09. 
    The write_task_result should simply overwrite the status of this Task
    and change its value to "success". 
    """
    reseed()

    test_task_name = "Update CI env with the latest integration branch"
    test_task_version = "2021.09"

    test_jjm = JenkinsJobManager()
    test_jjm.write_task_result(test_task_name, test_task_version)

    # checking to make sure we've altered instead of inserting
    assert get_task_num() == 10

    written_task = read_task(10)
    assert written_task.status == "success"


if __name__ == "__main__":
    test_write_no_prior()

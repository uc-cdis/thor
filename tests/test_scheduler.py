import pytest
from freezegun import freeze_time
import mock
import platform

from thor.maestro.jenkins import JenkinsJobManager
from thor.time.scheduler import Scheduler

# TODO: This only works on Ubuntu
# for some mysterious reason, freezegun does not keep UTC while running on Mac OS X


@mock.patch(
    "thor.maestro.jenkins.JenkinsJobManager.check_result_of_job",
    mock.MagicMock(return_value="success"),
)
@mock.patch.object(JenkinsJobManager, "run_job")
def test_scheduler_triggers_jenkins_job_on_2nd_friday_of_the_month(
    mock_jenkins_run_job,
):
    # 5 seconds before the expected cron schedule 0 21 8-15 * (9 pm on the 2nd Friday)
    fake_timestamp = "2021-09-10 20:59:55"

    # setting +6hs due to strange behavior with freezegun on Mac OS X
    if platform.system() == "Darwin":
        fake_timestamp = "2021-09-11 01:59:55"

    freezer = freeze_time(fake_timestamp, tick=True)
    freezer.start()

    sch = Scheduler("test_thor_config.json")

    # We just need step1 for this test, deleting the others from the dict
    del sch.jobs_and_schedules["step2"]
    del sch.jobs_and_schedules["step3"]
    del sch.jobs_and_schedules["step4"]
    del sch.jobs_and_schedules["step5"]

    print("scheduler not yet initialized")
    sch.initialize_scheduler("jenkins2")
    print("scheduler initialized")
    # assertion with expected job_name and empty parameters
    mock_jenkins_run_job.assert_called_once_with(
        "thor-test-step1", {"release_version": "2021.09"}
    )

    # TODO: assert on database entry related to successfully executed task
    # assert task_dao result == success


@mock.patch(
    "thor.maestro.jenkins.JenkinsJobManager.check_result_of_job",
    mock.MagicMock(return_value="success"),
)
@mock.patch.object(JenkinsJobManager, "run_job")
def test_scheduler_triggers_jenkins_job_on_4th_friday_of_the_month(
    mock_jenkins_run_job,
):
    # 5 seconds before the expected cron schedule 0 22 22-28 * 5 (10 pm on the 4th Friday)
    fake_timestamp = "2021-09-25 21:59:55"

    # setting +6hs due to strange behavior with freezegun on Mac OS X
    if platform.system() == "Darwin":
        fake_timestamp = "2021-09-26 02:59:55"

    freezer = freeze_time(fake_timestamp, tick=True)
    freezer.start()

    sch = Scheduler("test_thor_config.json")

    # We just need step5 for this test, deleting the others from the dict
    del sch.jobs_and_schedules["step1"]
    del sch.jobs_and_schedules["step2"]
    del sch.jobs_and_schedules["step3"]
    del sch.jobs_and_schedules["step4"]

    sch.initialize_scheduler("jenkins2")

    # assertion with expected job_name and empty parameters
    mock_jenkins_run_job.assert_called_once_with("thor-test-step5", {'release_version': '2021.09'})

    # TODO: assert on database entry related to successfully executed task
    # assert task_dao result == success

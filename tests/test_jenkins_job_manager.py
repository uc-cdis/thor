import pytest
import json

from thor.maestro.jenkins import JenkinsJobManager

expected_url = "https://jenkins2.planx-pla.net/job/this-is-a-test/buildWithParameters?token=whatever_token&THE_NAME=William&RELEASE_VERSION=2021.09"


def test_assemble_url():
    jjm = JenkinsJobManager("jenkins2")
    job_params_dict = {
        "THE_NAME": "William",
        "RELEASE_VERSION": "2021.09",
    }
    returned_url = jjm.assemble_url("this-is-a-test", job_params_dict)
    assert returned_url == expected_url

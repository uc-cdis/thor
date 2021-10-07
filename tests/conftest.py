import os


def pytest_generate_tests(metafunc):
    os.environ["JENKINS_USERNAME"] = "whatever"
    os.environ["JENKINS_API_TOKEN"] = "whatever"
    os.environ["JENKINS_JOB_TOKEN"] = "whatever_token"
import os


def pytest_generate_tests(metafunc):
    os.environ["JENKINS_USERNAME"] = "whatever"
    os.environ["JENKINS_API_TOKEN"] = "whatever"

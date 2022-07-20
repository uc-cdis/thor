import os
import logging

def pytest_generate_tests(metafunc):
    os.environ["JENKINS_USERNAME"] = "whatever"
    os.environ["JENKINS_API_TOKEN"] = "whatever"
    os.environ["JENKINS_JOB_TOKEN"] = "whatever_token"

def pytest_addoption(parser):
    """Add a command line option to disable logger."""
    parser.addoption(
        "--log-disable", action="append", default=[], help="disable specific loggers"
    )

def pytest_configure(config):
    """Disable the loggers."""
    for name in config.getoption("--log-disable", default=[]):
        logger = logging.getLogger(name)
        logger.propagate = False
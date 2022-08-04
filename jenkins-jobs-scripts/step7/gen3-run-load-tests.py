import os
import time
import logging

from thor.maestro.jenkins import JenkinsJobManager

log = logging.getLogger(__name__)

jjm = JenkinsJobManager("https://jenkins.planx-pla.net/") 

jjm.run_job(job_name = "gen3-run-load-tests", \
    job_parameters = {
        "TARGET_ENVIRONMENT":os.environ["TARGET_ENVIRONMENT"],
        "LOAD_TEST_DESCRIPTOR":os.environ["LOAD_TEST_DESCRIPTOR"], 
        "PRESIGNED_URL_ACL_FILTER":os.environ["PRESIGNED_URL_ACL_FILTER"], 
        "SHEEPDOG_NUM_OF_RECORDS_TO_IMPORT":os.environ["SHEEPDOG_NUM_OF_RECORDS_TO_IMPORT"],
        "DESIRED_NUMBER_OF_FENCE_PODS":os.environ["DESIRED_NUMBER_OF_FENCE_PODS"],
        "RELEASE_VERSION":os.environ["RELEASE_VERSION"],
        "INDEXD_NUM_OF_RECORDS_TO_CREATE":os.environ["INDEXD_NUM_OF_RECORDS_TO_CREATE"],
        "SIGNED_URL_PROTOCOL":os.environ["SIGNED_URL_PROTOCOL"],
        "SQS_URL":os.environ["SQS_URL"]
    })

result_returned = False
while not result_returned:
    time.wait(10)
    try:
        job_result = jjm.check_result_of_job("gen3-run-load-tests", os.environ["RELEASE_VERSION"])
    except Exception as e:
        log.error(f"error checking job result: {e}")
        continue
    else:
        # JJM throws the exceptions when the job is not yet complete, 
        # So now we can expect that the job is done. 
        result_returned = True

import os
import time
import logging

from thor.maestro.jenkins import JenkinsJobManager

log = logging.getLogger(__name__)

jjm = JenkinsJobManager("https://jenkins.planx-pla.net/") 

jjm.run_job(job_name = "gen3-run-all-load-tests-for-release-testing", \
    job_parameters = {
        "LIST_OF_LOAD_TEST_SCENARIOS":"fence-presigned-url,sheepdog-import-clinical-metada,metadata-service-create-and-query,metadata-service-filter-large-database,metadata-service-create-and-delete,metadata-service-create-mds-record,drs-endpoint,ga4gh-drs-performance,create-indexd-records",
        "RELEASE_VERSION":os.environ["RELEASE_VERSION"]
    })

result_returned = False
while not result_returned:
    time.wait(1800)
    try:
        job_result = jjm.check_result_of_job("gen3-run-all-load-tests-for-release-testing", os.environ["RELEASE_VERSION"])
    except Exception as e:
        log.error(f"error checking job result: {e}")
        continue
    else:
        # JJM throws the exceptions when the job is not yet complete, 
        # So now we can expect that the job is done. 
        result_returned = True

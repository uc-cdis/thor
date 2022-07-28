# #!/bin/bash -x  
#################################################
# Standing issues: 
# No credentials for Github and running tests
#   Specifically: 
#       Github
#       Fence-Google-App
#       CI-Env-1
#       QA-NIAID
# Inability to archive test artifacts
# Many variables exported - where do they go?
# Anything related to functionality of sh commands. 
#################################################


# checkout cloud-automation
git clone https://github.com/uc-cdis/cloud-automation.git

# checkout gen3-qa
git clone https://github.com/uc-cdis/gen3-qa.git

# create test data (TODO)
mkdir -p testData

# """#!/bin/bash
export KUBECTL_NAMESPACE="$TARGET_ENVIRONMENT"
# setup gen3 CLI
export GEN3_HOME=\$WORKSPACE/cloud-automation
source \$GEN3_HOME/gen3/gen3setup.sh

if [ "$LOAD_TEST_DESCRIPTOR" == "audit-presigned-url" ]; then
  echo "Populating audit-service SQS with presigned-url messages"
  bash gen3-qa/load-testing/audit-service/sendPresignedURLMessages.sh $SQS_URL
elif [ "$LOAD_TEST_DESCRIPTOR" == "audit-login" ]; then
  echo "Populating audit-service SQS with login messages"
  bash gen3-qa/load-testing/audit-service/sendLoginMessages.sh $SQS_URL
elif [ "$LOAD_TEST_DESCRIPTOR" == "fence-presigned-url" ]; then
  # This is not working
  # We should use "gen3 gitops configmaps scaling && gen3 scaling apply all" instead.
  # gen3 replicas presigned-url-fence $DESIRED_NUMBER_OF_FENCE_PODS
  # sleep 60
  g3kubectl get pods | grep fence
else
  echo "Presigned URL test was not selected. Skipping auto-scaling changes..."
fi
                  
# run tests
withCredentials
file(credentialsId: 'fence-google-app-creds-secret', variable: 'GOOGLE_APP_CREDS_JSON'),
file(credentialsId: 'ci-env-1-credentials-json', variable: 'CI_ENV_1_CREDS_JSON'),
file(credentialsId: 'QA-NIAID-CRED', variable: 'QA_NIAID_CREDS')
# Eventually we'll have to tackle the credentials problem, this note stays here until then

cd gen3-qa

selectedLoadTestDescriptor = $LOAD_TEST_DESCRIPTOR

# #!/bin/bash -x  
export GEN3_HOME=../cloud-automation
export TEST_DATA_PATH=../testData
export GEN3_SKIP_PROJ_SETUP=true
export RUNNING_LOCAL=false

mv "$CI_ENV_1_CREDS_JSON" credentials.json

npm install

SELECTED_LOAD_TEST_DESCRIPTOR=""

# case statement to use one of the load test descriptor JSON files
case $selectedLoadTestDescriptor in
fence-presigned-url)
    echo "Selected presigned url"
    # FOR PRESIGNED URLS
    sed -i 's/"indexd_record_acl": "phs000178",/"indexd_record_acl": "$PRESIGNED_URL_ACL_FILTER",/' load-testing/sample-descriptors/load-test-presigned-url-bottleneck-sample.json
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-presigned-url-bottleneck-sample.json random-guids"
    ;;
fence-presigned-url-stress-test)
    echo "Selected presigned url stress test"
    # FOR PRESIGNED URLS
    sed -i 's/"indexd_record_acl": "phs000178",/"indexd_record_acl": "$PRESIGNED_URL_ACL_FILTER",/' load-testing/sample-descriptors/presigned-url-stress-test.json
    SELECTED_LOAD_TEST_DESCRIPTOR="presigned-url-stress-test.json random-guids"
    ;;
drs-endpoint)
    echo "Selected drs-endpoint"
    # FOR INDEXD DRDS ENDPOINTS
    sed -i 's/"indexd_record_acl": "phs000178",/"indexd_record_acl": "$PRESIGNED_URL_ACL_FILTER",/' load-testing/sample-descriptors/load-test-drs-endpoint-bottleneck-sample.json
    sed -i 's/"presigned_url_protocol": "phs000178",/"indexd_record_acl": "SIGNED_URL_PROTOCOL",/' load-testing/sample-descriptors/load-test-drs-endpoint-bottleneck-sample.json
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-drs-endpoint-bottleneck-sample.json random-guids"
    ;;
sheepdog-import-clinical-metada)
    echo "Selected Sheepdog import clinical metadata"
    # FOR SHEEPDOG IMPORT
    sed -i 's/"num_of_records": 1000,/"num_of_records": $SHEEPDOG_NUM_OF_RECORDS_TO_IMPORT,/' load-testing/sample-descriptors/load-test-sheepdog-import-clinical-metadata.json
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-sheepdog-import-clinical-metadata.json"
    ;;
metadata-service-create-and-query)
    echo "Selected Metadata Service create and query test"
    # FOR MDS create and query
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-metadata-service-create-and-query-sample.json"
    ;;
metadata-service-filter-large-database)
    echo "Selected Metadata Service filter large database test"
    # FOR MDS soak test
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-metadata-service-large-database-sample.json"
    ;;
study-viewer)
    echo "Selected Study Viewer test"
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-study-viewer.json"
    sed -i 's/"override_access_token": "<place_access_token_here>",/"override_access_token": "$QA_NIAID_CREDS",/' load-testing/sample-descriptors/load-test-study-viewer.json
    ;;
audit-presigned-url)
    echo "Selected Audit Service Presigned URL test"
    mv "$QA_NIAID_CREDS" credentials.json
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-audit-presigned-urls-sample.json"
    ;;
audit-login)
    echo "Selected Audit Service Login test"
    mv "$QA_NIAID_CREDS" credentials.json
    SELECTED_LOAD_TEST_DESCRIPTOR="load-test-audit-login-sample.json"
    ;;    
esac

node load-testing/loadTestRunner.js credentials.json load-testing/sample-descriptors/\$SELECTED_LOAD_TEST_DESCRIPTOR

echo "done"

# stage('upload results') 

# #!/bin/bash -x    
echo "uploading results..."
aws s3 cp ./gen3-qa/result.json "s3://qaplanetv2-data-bucket/\$RELEASE_VERSION/\$LOAD_TEST_DESCRIPTOR/result_\$(date +%s).json"
                        
# archiveArtifacts artifacts: 'gen3-qa/result.json'
# Unsure how to archive artifacts, so this is commented out

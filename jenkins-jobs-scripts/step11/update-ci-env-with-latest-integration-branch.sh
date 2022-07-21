#!/bin/bash +x
#################################################
# Standing issues: 
# No Git authentication for checkouts
# General credentials issue (Github UN and Token)
#################################################

# stage('Initial setup')

# manifest repo
git clone https://github.com/uc-cdis/${REPO_NAME}
# This is "gitops-qa" being loaded in

# gen3-release-utils
git clone https://github.com/uc-cdis/gen3-release-utils.git

# stage('Update CI environment')
withCredentials([usernamePassword(credentialsId: 'PlanXCyborgUserJenkins', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')])
# This credentials issue needs to be fixed, as before. 
cd gen3-release-utils

cd gen3release-sdk
poetry install
poetry run gen3release apply -v $INTEGRATION_BRANCH -e $(pwd)/${REPO_NAME}/${TARGET_ENVIRONMENT} -pr "${PR_TITLE} ${INTEGRATION_BRANCH} ${TARGET_ENVIRONMENT} $(date +%s)"

#################################################
# Standing issues: 
# No Git authentication for checkouts
# Unsure which repo to use for "manifest repo"
# General credentials issue
# What to use for $WORKSPACE?
#################################################

# stage('Initial setup')

# manifest repo
git clone https://github.com/uc-cdis/${REPO_NAME}
# Which Repo?

# gen3-release-utils
git clone https://github.com/uc-cdis/gen3-release-utils.git

# stage('Update CI environment')
withCredentials([usernamePassword(credentialsId: 'PlanXCyborgUserJenkins', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')])
# This credentials issue needs to be fixed, as before. 
cd gen3-release-utils

cd gen3release-sdk
poetry install
poetry run gen3release apply -v $INTEGRATION_BRANCH -e ${WORKSPACE}/${REPO_NAME}/${TARGET_ENVIRONMENT} -pr "${PR_TITLE} ${INTEGRATION_BRANCH} ${TARGET_ENVIRONMENT} $(date +%s)"

# #!/bin/bash -x  
#################################################
# Standing Issues:
# No credentials for Github
# No specification for $WORKSPACE
# General functionality of gen3release unknown - must test
##################################################


git clone https://github.com/uc-cdis/gen3-release-utils.git
# Checkout manifest?

cd gen3-release-utils/gen3release-sdk
poetry install
poetry run gen3release apply -v $INTEGRATION_BRANCH -e ${WORKSPACE}/${REPO_NAME}/${TARGET_ENVIRONMENT} -pr "${PR_TITLE} ${INTEGRATION_BRANCH} ${TARGET_ENVIRONMENT} $(date +%s)"
# What to specify for $WORKSPACE? $PR_TITLE?
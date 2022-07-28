# #!/bin/bash -x  
#################################################
# Standing Issues:
# No credentials for Github - pulling $GITHUB_USERNAME and $GITHUB_PASSWORD from env
# General functionality of gen3release unknown - must test
##################################################


git clone https://$GITHUB_USERNAME:$GITHUB_PASSWORD@github.com/uc-cdis/gen3-release-utils.git
# Checkout manifest?

cd gen3-release-utils/gen3release-sdk
poetry install
poetry run gen3release apply -v $INTEGRATION_BRANCH -e $(pwd)/${REPO_NAME}/${TARGET_ENVIRONMENT} -pr "${PR_TITLE} ${INTEGRATION_BRANCH} ${TARGET_ENVIRONMENT} $(date +%s)"
# What to specify for $WORKSPACE?
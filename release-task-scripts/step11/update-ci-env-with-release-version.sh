#!/bin/bash
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}

git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gen3-release-utils.git"
git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gitops-qa.git"

cd gen3-release-utils/gen3release-sdk
pip install -U pip
pip install poetry
poetry install

IFS=';' read -ra ENVS <<< "$TARGET_ENVIRONMENTS"
for ENV in "${ENVS[@]}"; do
  GITHUB_TOKEN="$GITHUB_TOKEN" poetry run gen3release apply -v $RELEASE_VERSION -e ../../gitops-qa/${ENV} -pr "${PR_TITLE} ${RELEASE_VERSION} ${ENV} $(date +%s)" -l "gen3-release"
done

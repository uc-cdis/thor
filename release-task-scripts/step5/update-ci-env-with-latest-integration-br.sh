#!/bin/bash
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}
export GEN3_GITOPS_PATH="$(pwd)/$REPO_NAME"
export GEN3_HELM_PATH="$(pwd)/gen3-helm"

git config --global user.name "${GITHUB_USERNAME}"
git config --global user.email "cdis@uchicago.edu"
git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/${REPO_NAME}"
git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gen3-helm"

pip install -U pip
pip install poetry
poetry install

IFS=';' read -ra ENVS <<< "$TARGET_ENVIRONMENTS"
for ENV in "${ENVS[@]}"; do
  export TARGET_ENV=$ENV
  export REPO_LIST_PATH="/src/repo_list.txt"
  TIMESTAMP=$(date +%s)
  PR_NAME="${PR_TITLE} ${IMAGE_TAG_VERSION} ${ENV} ${TIMESTAMP}"
  SANITIZED_ENV="${TARGET_ENV//\//_}"
  BRANCH_NAME="chore/apply_${IMAGE_TAG_VERSION}_to_${SANITIZED_ENV}_${TIMESTAMP}"
  COMMIT_MSG="Updating $TARGET_ENV with $IMAGE_TAG_VERSION"
  REPO_OWNER="uc-cdis"
  BASE_BRANCH="master"

  # PERFORM GIT OPERATIONS TO SWITCH TO NEW BRANCH and navigate to target env folder
  cd $GEN3_GITOPS_PATH
  pwd
  git switch master
  git fetch origin
  git checkout -b "$BRANCH_NAME"
  cd "${TARGET_ENV}/values/"

  # Update the yaml files
  poetry run python /src/src/scripts/update-values-yaml-with-release-version.py

  # PUSH in the branch and create a PR
  git add .
  git commit -m "${COMMIT_MSG}"
  git push origin "$BRANCH_NAME"

  curl -u "$GITHUB_USERNAME:$GITHUB_TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/pulls" \
  -d "$(jq -n \
    --arg title "$PR_NAME" \
    --arg head "$BRANCH_NAME" \
    --arg base "$BASE_BRANCH" \
    '{title: $title, head: $head, base: $base}')"
done

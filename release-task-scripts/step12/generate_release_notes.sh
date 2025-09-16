#!/bin/bash

set -e
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}
org="uc-cdis"
REPO_NAME="cdis-manifest"
YEAR="${RELEASE_VERSION%%.*}" 
MONTH="${RELEASE_VERSION#*.}"
CDIS_MANIFEST_PATH="$(pwd)/$REPO_NAME"
PR_TITLE="doc(qa) adding release notes for $RELEASE_VERSION"
TIMESTAMP=$(date +%s)
BRANCH_NAME="doc/release_artifacts_$TIMESTAMP"
BASE_BRANCH="master"
COMMIT_MSG="Storing release artifacts for version $RELEASE_VERSION"

# Generate the release notes
poetry run python /src/release-task-scripts/step12/generate_release_notes.py

# Set git config and download cdis-manifest folder
git config --global user.name "${GITHUB_USERNAME}"
git config --global user.email "cdis@uchicago.edu"
git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/${REPO_NAME}"

# PERFORM GIT OPERATIONS TO SWITCH TO NEW BRANCH and navigate to releases folder
cd $CDIS_MANIFEST_PATH
git switch master
git fetch origin
git checkout -b "$BRANCH_NAME"
cd releases

# Create YEAR and Month folder as needed
DIR=$YEAR
if [ ! -d "$DIR" ]; then
    mkdir -p "$DIR"
    echo "Created directory: $DIR"
else
    echo "Directory already exists: $DIR"
fi
cd $DIR
mkdir $MONTH
cd $MONTH

cp /src/release-task-scripts/step12/gen3-release-notes.md .

# PUSH in the branch and create a PR
git add .
git commit -m "${COMMIT_MSG}"
git push origin "$BRANCH_NAME"

curl -u "$GITHUB_USERNAME:$GITHUB_TOKEN" \
-X POST \
-H "Accept: application/vnd.github+json" \
-H "Content-Type: application/json" \
"https://api.github.com/repos/$org/$REPO_NAME/pulls" \
-d "$(jq -n \
  --arg title "$PR_TITLE" \
  --arg head "$BRANCH_NAME" \
  --arg base "$BASE_BRANCH" \
  '{title: $title, head: $head, base: $base}')"

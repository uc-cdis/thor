#!/bin/bash

set -e
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}
org="uc-cdis"

poetry run python /src/release-task-scripts/step12/generate_release_notes.py

if [ -d gen3-release-utils ]; then
  echo "Removing exisitng gen3-release-utils directory ..."
  rm -rf gen3-release-utils
fi

echo "---- Installing gen3-release-sdk ----"
git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gen3-release-utils.git"
cd gen3-release-utils/gen3release-sdk
pip install -U pip
pip install poetry
poetry install

echo "---- Publishing the release notes ----"
cp ../../gen3-release-notes.md .
cp ../../manifest.json .
GITHUB_TOKEN="$GITHUB_TOKEN" poetry run gen3release notes -v $RELEASE_VERSION -f gen3-release-notes.md manifest.json
echo "---- Done ----"
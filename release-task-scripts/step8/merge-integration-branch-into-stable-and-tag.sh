#!/bin/bash

export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'}

urlPrefix="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/"
sourceBranchName=$INTEGRATION_BRANCH
tagName=$RELEASE_VERSION
targetBranchName="stable"

if find . -name "gen3-integration" -type d; then
  echo "Deleting existing gen3-integration folder"
  rm -rf gen3-integration
fi
if mkdir gen3-integration; then
  cd gen3-integration || exit 1
else
  echo "Failed to create the gen3-integration folder. Exiting"
  exit 1
fi

git config --global user.name "${GITHUB_USERNAME}"
git config --global user.email "cdis@uchicago.edu"
repo_list="/src/repo_list.txt"
while IFS= read -r repo; do
  echo "### Pulling ${targetBranchName} branch into the stable branch for repo ${repo} ###"
  git clone "${urlPrefix}${repo}"
  cd "${repo}" || exit 1
  git ls-remote --heads ${urlPrefix}${repo} ${targetBranchName} | grep ${targetBranchName} > /dev/null
  if [ "$?" == "0" ]; then
    echo "Remote stable branch exists, checking it out"
    git checkout -b "${targetBranchName}" "origin/${targetBranchName}"
  else
    echo "Remote stable branch does not exist, creating a branch out of integration branch"
    git checkout "${sourceBranchName}"
    git checkout -b "${targetBranchName}" "${sourceBranchName}"
  fi
  git pull origin "${targetBranchName}"
  result=$(result=$(git pull --no-rebase -s recursive -Xtheirs origin "${sourceBranchName}"))
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  result=$(git push origin "${targetBranchName}")
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  result=$(git tag "${tagName}" -a -m "Gen3 Core Release ${tagName}" 2>&1)
  if [[ "$result" == *"already exists"* ]]; then
    echo "meh. Tag ${tagName} already exists for repo ${repo}... skipping it."
    continue
  fi

  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  result=$(git push origin --tags)
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  cd ..
done < "$repo_list"

cd ..
echo "### Cleaning up folder gen3-integration ###"
rm -rf gen3-integration
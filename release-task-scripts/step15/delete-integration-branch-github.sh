#!/bin/bash
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}

urlPrefix="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/"
targetBranchName=$INTEGRATION_BRANCH

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

repo_list="/src/repo_list.txt"
while IFS= read -r repo; do
  echo "### Cloning repo ${repo} ###"
  git clone "${urlPrefix}${repo}"
  echo "### stepping into ${repo} directory ..."
  cd ${repo} || exit 1
  echo "Deleting ${targetBranchName} branch on ${repo}"
  result=$(git push origin --delete "$targetBranchName" 2>&1)
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

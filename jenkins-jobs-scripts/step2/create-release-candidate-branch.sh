#!/bin/bash
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}

urlPrefix="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/"
sourceBranchName=$FORK_FROM
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
  echo "### Cutting ${targetBranchName} branch for repo ${repo} ###"
  git clone "${urlPrefix}${repo}"
  repo_folder=$(echo $repo | awk -F'/' '{print $2}')
  echo "### stepping into ${repo_folder}..."
  cd "${repo_folder}" || exit 1
  git fetch
  git checkout "${sourceBranchName}"
  result=$(git checkout -b "${targetBranchName}")
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
  cd ..
done < "$repo_list"

cd ..
echo "### Cleaning up folder gen3-integration ###"
rm -rf gen3-integration

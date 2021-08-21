#!/bin/bash

BRANCH_NAME=""
if [[ $RELEASE_VERSION =~ [0-9]{4}\.([0-9]{2}) ]]; then
  echo "match"
  CONVERTED_MONHT_STR_TO_NUMBER=$(expr ${BASH_REMATCH[1]} + 0)
  BRANCH_NAME=$(printf "%02d\n" $CONVERTED_MONHT_STR_TO_NUMBER)
  echo "creating branch integration2021${BRANCH_NAME}..."
else
  echo "not match. Skip branch creation."
  exit 1
fi

urlPrefix="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/"
sourceBranchName="master"
targetBranchName="integration2021${BRANCH_NAME}"

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

repo_list="../repo_list.txt"
while IFS= read -r repo; do
  echo "### Cutting ${targetBranchName} branch for repo ${repo} ###"
  git clone "${urlPrefix}${repo}"
  cd "${repo}" || exit 1
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

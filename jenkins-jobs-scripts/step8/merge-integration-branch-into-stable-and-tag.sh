#!/bin/bash

BRANCH_NAME=""
YEAR_STR=""
BRANCH_NAME=""
if [[ $RELEASE_VERSION =~ ([0-9]{4})\.([0-9]{2}) ]]; then
  echo "match"
  YEAR_STR="${BASH_REMATCH[1]}"
  CONVERTED_MONTH_STR_TO_NUMBER=$(expr ${BASH_REMATCH[2]} + 0)
  BRANCH_NAME=$(printf "%02d\n" $CONVERTED_MONTH_STR_TO_NUMBER)
  echo "creating branch integration${YEAR_STR}${BRANCH_NAME}..."
else
  echo "not match. Skip branch creation."
  exit 1
fi

urlPrefix="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/"
sourceBranchName=$BRANCH_NAME
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

repo_list="/src/repo_list.txt"
while IFS= read -r repo; do
  echo "### Pulling ${targetBranchName} branch into the stable branch for repo ${repo} ###"
  git clone "${urlPrefix}${repo}"
  cd "${repo}" || exit 1
  git ls-remote --heads ${urlPrefix}${repo} ${targetBranchName} | grep ${BRANCH} >/dev/null
  if [ "$?" == "0" ]; then
    git checkout "${targetBranchName}"
  else
    git checkout "${sourceBranchName}"
    git checkout -b "${targetBranchName}" "${sourceBranchName}"
  fi
  git config user.name "${GITHUB_USERNAME}"
  result=$(git pull origin "${sourceBranchName}" -s recursive -Xtheirs)
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  git pull origin "${targetBranchName}"
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
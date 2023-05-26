#!/bin/bash
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}

pip install -U pip --user
pip install --editable git+https://github.com/uc-cdis/release-helper.git@gen3release#egg=gen3git --user

START_DATE=`date --date="41 day ago" +%Y-%m-%d`
END_DATE=`date --date="14 day ago" +%Y-%m-%d`
RELEASE_NAME="Core Gen3 Release $RELEASE_VERSION"

echo "### Generating Release Notes ###"
repoOwner="uc-cdis"
echo "### startDate is ${START_DATE} ###"
echo "### endDate is ${END_DATE} ###"
echo "### releaseName is ${RELEASE_NAME} ###"

if find . -name "release_notes.md" -type f; then
  echo "Deleting existing release notes"
  rm -f gen3_release_notes.md
fi

touch gen3_release_notes.md
echo "# $RELEASE_NAME" >> gen3_release_notes.md
echo >> gen3_release_notes.md

repo_list="../../repo_list.txt"
while IFS= read -r repo; do
  echo "### Getting the release notes for repo ${repo} ###"
  result=$(gen3git --repo "${repoOwner}/${repo}" --github-access-token "${GITHUB_TOKEN}" --from-date "${START_DATE}" gen --to-date "${END_DATE}" --file-name "${repo}_release_notes" --markdown)
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  if [[ $(wc -l < "${repo}_release_notes.md") -ge 3 ]]; then
    cat "${repo}_release_notes.md"
    cat "${repo}_release_notes.md" >> gen3_release_notes.md
  fi
done < "$repo_list"

YEAR=$(echo $RELEASE_VERSION | cut -d"." -f 1)
MONTH=$(echo $RELEASE_VERSION | cut -d"." -f 2)
CURR_YEAR=$(date +%Y)
CURR_MONTH=$(date +%m)

# Get the manifest from the previous monthly release
curl "https://raw.githubusercontent.com/uc-cdis/cdis-manifest/master/releases/${CURR_YEAR}/${CURR_MONTH}/manifest.json" -o manifest.json

# replace versions (TODO: Improve this logic to pick up new services from repos_list.txt)
sed -i "s/${CURR_YEAR}.${CURR_MONTH}/${YEAR}.${MONTH}/" manifest.json

git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gen3-release-utils.git"
cd gen3-release-utils/gen3release-sdk
pip install poetry
poetry install
gen3release notes -v ${RELEASE_VERSION} -f gen3_release_notes.md manifest.json
#!/bin/bash

export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}
org="uc-cdis"

git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gen3-release-utils.git"

pip3 install -U pip --user
pip3 install --editable git+https://github.com/uc-cdis/release-helper.git@gen3release#egg=gen3git --user

echo "------------------------------------------------------------------------------"
echo "Figuring out the time frame that comprises the CODE FREEZE dates"
echo "------------------------------------------------------------------------------"

# START_DATE=${date -d "$(date +'%Y-%m-01') -1 month +2 Saturdays" +%Y-%m-%d}
# END_DATE=${date -d "$(date +'%Y-%m-01') +2 Fridays" +%Y-%m-%d}
START_DATE=`date --date="2023-07-28 41 day ago" +%Y-%m-%d`
END_DATE=`date --date="2023-07-28 14 day ago" +%Y-%m-%d`

echo "------------------------------------------------------------------------------"
echo " Iterating through repos in repos_list.txt and fetch release notes"
echo "------------------------------------------------------------------------------"

# Utilize gen3git (aka: release-helper) to fetch bullet points from PR descriptions

startDate="$START_DATE"
echo "### startDate is ${startDate} ###"
endDate="$END_DATE"
echo "### endDate is ${endDate} ###"


if find . -name "release_notes.md" -type f; then
  echo "Deleting existing release notes"
  rm -f gen3_release_notes.md
fi

# Get release name
release_names="../../release_names.csv"
name=$(awk -F "," -v release="$RELEASE_VERSION" '$1 == release { print $2 }' "$release_names")
echo "# Release name : $name"

RELEASE="Core Gen3 Release $RELEASE_VERSION ($name)"

touch gen3_release_notes.md
echo "# $RELEASE" >> gen3_release_notes.md
echo >> gen3_release_notes.md

repo_list="../../repo_list.txt"
while IFS= read -r repo; do
  echo "### Getting the release notes for repo ${repo} ###"
  result=$(gen3git --repo "${org}/${repo}" --github-access-token "${GITHUB_TOKEN}" --from-date "${startDate}" gen --to-date "${endDate}" --file-name "${repo}_release_notes" --markdown)
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

echo "------------------------------------------------------------------------------"
echo " Replacing the manifest.json file with the latest release versions "
echo "------------------------------------------------------------------------------"

YEAR=$(echo $RELEASE_VERSION | cut -d"." -f 1)
MONTH=$(echo $RELEASE_VERSION | cut -d"." -f 2)
CURR_YEAR=$(date +%Y)
CURR_MONTH=$(date +%m)

# Get the manifest from the previous monthly release
curl "https://raw.githubusercontent.com/uc-cdis/cdis-manifest/master/releases/${CURR_YEAR}/${CURR_MONTH}/manifest.json" -o manifest.json

# replace versions
sed -i "s/${CURR_YEAR}.${CURR_MONTH}/${YEAR}.${MONTH}/" manifest.json

echo "------------------------------------------------------------------------------"
echo " Create a pull request to publish all release notes and manifest json file"
echo "------------------------------------------------------------------------------"

cd gen3-release-utils/gen3release-sdk
pip install -U pip
pip install poetry
poetry install

GITHUB_TOKEN="$GITHUB_TOKEN" poetry run gen3release notes -v ${RELEASE_VERSION} -f gen3-release_notes.md manifest.json

echo "done"

#!/bin/bash

echo "------------------------------------------------------------------------------"
echo "Figuring out the time frame that comprises the CODE FREEZE dates"
echo "------------------------------------------------------------------------------"

#--from-date and --to-tag of gen3git are inclusive

# Currently, the start date is the 2nd Saturday of last month
# Currently, the end date is the 2nd Friday of this month
# TODO: Refactor this to facilitate the change of the release frequency

FIRST_DAY_OF_LAST_MONTH=$(date --date="$(date +'%Y-%m-01') -1 month" +%Y-%m-%d)
LAST_DAY_OF_LAST_MONTH=$(date --date="$(date +'%Y-%m-01') -1 day" +%Y-%m-%d)
echo START_DATE=`python3.7 -c "import pandas as pd; import datetime; first=\"$FIRST_DAY_OF_LAST_MONTH\"; last=\"$LAST_DAY_OF_LAST_MONTH\"; second_saturday_timestamp=pd.date_range(first, last,freq='WOM-2SAT'); print(second_saturday_timestamp[0])" | cut -d " " -f 1` > var.STARTDATE

FIRST_DAY_OF_THE_CURRENT_MONTH=$(date --date="$(date +'%Y-%m-01')" +%Y-%m-%d)
LAST_DAY_OF_THE_CURRENT_MONTH=$(date --date="$(date +'%Y-%m-01') +1 month -1 day" +%Y-%m-%d)

echo END_DATE=`python3.7 -c "import pandas as pd; import datetime; first=\"$FIRST_DAY_OF_THE_CURRENT_MONTH\"; last=\"$LAST_DAY_OF_THE_CURRENT_MONTH\"; second_saturday_current_month_timestamp=pd.date_range(first, last,freq='WOM-2SAT'); print(second_saturday_current_month_timestamp[0])" | cut -d " " -f 1`

echo RELEASE_VERSION=`date --date="$END_DATE +1 month" +%Y.%m` > var.RELEASEVERSION
echo RELEASE_NAME="Core Gen3 Release $RELEASE_VERSION" > var.RELEASENAME

echo "------------------------------------------------------------------------------"
echo " Iterating through repos in repos_list.txt and fetch release notes"
echo "------------------------------------------------------------------------------"

# Utilize gen3git (aka: release-helper) to fetch bullet points from PR descriptions
# this CLI utility is installed through poetry
poetry install

startDate="$START_DATE"
echo "### startDate is ${startDate} ###"
endDate="$END_DATE"
echo "### endDate is ${endDate} ###"
githubAccessToken=$GITHUB_TOKEN

if find . -name "release_notes.md" -type f; then
  echo "Deleting existing release notes"
  rm -f gen3_release_notes.md
fi

touch gen3_release_notes.md
echo "# $RELEASE_NAME" >> gen3_release_notes.md
echo >> gen3_release_notes.md

repo_list="repo_list.txt"
while IFS= read -r repo; do
  echo "### Getting the release notes for repo ${repo} ###"
  result=$(poetry run gen3git --repo "${repo}" --github-access-token "${githubAccessToken}" --from-date "${startDate}" gen --to-date "${endDate}" --markdown)
  echo "$result"
  RC=$?
  if [ $RC -ne 0 ]; then
    echo "$result"
    exit 1
  fi
  if [[ $(wc -l < release_notes.md) -ge 3 ]]; then
    cat release_notes.md
    cat release_notes.md >> gen3_release_notes.md
  fi
done < "$repo_list"

echo "------------------------------------------------------------------------------"
echo " Create a pull request to publish all release notes"
echo "------------------------------------------------------------------------------"

# TODO: Make gen3release-sdk parameterizable so it will create the experimental release notes in gitops-qa-v2 instead of cdis-manifest

echo "done"

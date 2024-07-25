#!/bin/bash
export RELEASE_URL="https://github.com/uc-cdis/cdis-manifest/blob/master/releases/${RELEASE_VERSION//./\/}/gen3-release-notes.md"

# Get the Release title based on release version from release_names.csv file
csv_file="../../release_names.csv"
line=$(awk -v name="$RELEASE_VERSION" -F',' 'FNR > 1 && $1 == name { print }' "$csv_file")
export RELEASE_TITLE=$(echo "$line" | awk -F',' '{print $NF}')

# Split the variable by comma into an array
IFS=',' read -ra ITEMS <<< "$RELEASE_NOTIFICATION_WEBHOOK"

for ITEM in "${ITEMS[@]}"
do
    # Perform slack operation using $ITEM
    curl -X POST "$ITEM" \
    -H 'Content-Type: application/json' \
    -d "{'text':'*:tada: Gen3 Release "$RELEASE_VERSION" ("$RELEASE_TITLE") is out :tada:*\nPlease find the release notes here - "$RELEASE_URL"'}"
done
#!/bin/bash
export GITHUB_USERNAME="PlanXCyborg"
export GITHUB_TOKEN=${GITHUB_TOKEN//$'\n'/}
git config --global user.name "${GITHUB_USERNAME}"
git config --global user.email "cdis@uchicago.edu"

git clone "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/uc-cdis/gen3-gitops.git"

pip install -U pip
pip install poetry
poetry install

cd "gen3-gitops"
GEN3_GITOPS_PATH=$(pwd)
IFS=';' read -ra ENVS <<< "$TARGET_ENVIRONMENTS"
for ENV in "${ENVS[@]}"; do
  TARGET_VERSION=$INTEGRATION_BRANCH
  TARGET_ENV=$ENV
  PR_NAME="${PR_TITLE} ${INTEGRATION_BRANCH} ${ENV} $(date +%s)"
  repo_list="/src/repo_list.txt"
  values_yaml="values.yaml"
  svcs_to_slip_list="/src/svcs_to_skip_list.txt"
  SANITIZED_ENV="${TARGET_ENV//\//_}"
  TIMESTAMP=$(date +%s)
  BRANCH_NAME="chore/apply_${INTEGRATION_BRANCH}_to_${SANITIZED_ENV}_${TIMESTAMP}"
  COMMIT_MSG="Applying version {$INTEGRATION_BRANCH} to {$TARGET_ENV}"
  REPO_OWNER="uc-cdis"
  REPO_NAME="gen3-gitops"
  BASE_BRANCH="master"

  # PERFORM GIT OPERATIONS TO SWITCH TO NEW BRANCH and navigate to target env folder
  cd $GEN3_GITOPS_PATH
  echo $GEN3_GITOPS_PATH
  git switch master
  git fetch origin
  git checkout -b "$BRANCH_NAME"
  cd "${TARGET_ENV}/values/"

  # CHECK each file under values folder to check service block and update the image with TARGET_VERSION
  while IFS= read -r service_name || [[ -n "$service_name" ]]; do
    # Skip empty lines
    [[ -z "$service_name" ]] && continue
    # Skip services in the skip list
    if grep -Fx "$service_name" "$svcs_to_slip_list"; then
      echo "Skipping $service_name (in skip list)"
      continue
    fi
    service_file="${service_name}.yaml"
    # Check if a service_file exists and update it
    if [[ -f "$service_file" ]]; then
      echo "Updating $service_file for $service_name"
      yq '.' "$service_file" | jq ".${service_name}.image.tag = \"${TARGET_VERSION}\"" | yq -y > tmp.yaml && mv tmp.yaml "$service_file"
    else
      # Check if a service block is available in values.yaml
      if yq '.' "$values_yaml" | jq -e --arg name "$service_name" 'has($name)' > /dev/null; then
        echo "Updating $values_yaml for $service_name"
        yq '.' "$values_yaml" | jq ".${service_name}.image.tag = \"${TARGET_VERSION}\"" | yq -y > tmp.yaml && mv tmp.yaml "$values_yaml"
      else
        echo "$service_name not found in values.yaml, skipping...."
      fi
    fi
  done < "$repo_list"

  # PUSH in the branch and create a PR
  git add .
  git commit -m "${COMMIT_MSG} for $ENV"
  git push origin "$BRANCH_NAME"

  curl -u "$GITHUB_USERNAME:$GITHUB_TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/pulls" \
  -d "$(jq -n \
    --arg title "$PR_NAME" \
    --arg head "$BRANCH_NAME" \
    --arg base "$BASE_BRANCH" \
    '{title: $title, head: $head, base: $base}')"

done

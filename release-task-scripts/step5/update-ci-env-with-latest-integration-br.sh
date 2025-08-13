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
  # Mapping for service name normalization
  normalize_service_name() {
    case "$1" in
      audit-service) echo "audit" ;;
      metadata-service) echo "metadata" ;;
      data-portal) echo "portal" ;;
      *) echo "$1" ;;
    esac
  }

  # Check if a service is in the skip list
  is_skipped() {
    grep -Fxq "$1" "$svcs_to_slip_list"
  }

  # Update service YAML file
  update_service_file() {
    local name="$1"
    local file="${name}.yaml"
    if [[ -f "$file" ]]; then
      echo "Updating $file for $name"
      yq '.' "$file" | jq --arg tag "$TARGET_VERSION" --arg name "$name" \
        '.[$name].image.tag = $tag' | yq -y > tmp.yaml && mv tmp.yaml "$file"
      return 0
    fi
    return 1
  }

  # Update values.yaml
  update_values_yaml() {
    local name="$1"
    local tag="$2"
    if yq '.' "$values_yaml" | jq -e --arg name "$name" 'has($name)' > /dev/null; then
      echo "Updating $values_yaml for $name"
      yq '.' "$values_yaml" | jq --arg name "$name" --arg tag "$tag" \
        '.[$name].image.tag = $tag' | yq -y > tmp.yaml && mv tmp.yaml "$values_yaml"
    else
      echo "$name not found in $values_yaml, skipping...."
    fi
  }

  # Special handler for indexs3client
  handle_indexs3client() {
    local full_tag="quay.io/cdis/indexs3client:$TARGET_VERSION"
    if [[ -f "ssjdispatcher.yaml" ]]; then
      echo "Updating ssjdispatcher.yaml for indexs3client"
      yq '.' ssjdispatcher.yaml | jq --arg tag "$full_tag" \
        '.ssjdispatcher.indexing = $tag' | yq -y > tmp.yaml && mv tmp.yaml ssjdispatcher.yaml
    else
      update_values_yaml "ssjdispatcher" "$full_tag"
    fi
  }

  while IFS= read -r raw_name || [[ -n "$raw_name" ]]; do
    [[ -z "$raw_name" ]] && continue
    service_name=$(normalize_service_name "$raw_name")
    if is_skipped "$service_name"; then
      echo "Skipping $service_name (in skip list)"
      continue
    fi
    if [[ "$service_name" == "indexs3client" ]]; then
      handle_indexs3client
      continue
    fi
    if ! update_service_file "$service_name"; then
      update_values_yaml "$service_name" "$TARGET_VERSION"
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

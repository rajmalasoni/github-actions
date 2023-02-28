#!/bin/bash

STALE_DAYS=$STALE_DAYS
CLOSE_DAYS=$CLOSE_DAYS

# for curl API
token="$GITHUB_TOKEN"
BASE_URI="https://api.github.com"
owner="$REPO_OWNER"
repo="$REPO_NAME"
pull_number="$PR_NUMBER"
issue_number="$ISSUE_NUMBER"

# Stale Pull Request

pr_number=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls | jq -r '.[].url')

pr_created_at=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls/$pull_number | jq -r '.created_at')
pr_updated_at=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls/$pull_number | jq -r '.updated_at')
issue_updated_at=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls/$issue_number | jq -r '.updated_at')

label_created_at=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/issues/$issue_number/events | jq -r '.[-1] | select(.event == "labeled") | select( .label.name == "Stale") | .created_at')


live_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
convert_live_date=$(date -u -d "$live_date" +%s)
convert_pr_updated_at=$(date -u -d "$pr_updated_at" +%s)
convert_issue_updated_at=$(date -u -d "$issue_updated_at" +%s)
convert_label_created_at=$(date -u -d "$label_created_at" +%s)

PrUpdatedTime=$((convert_live_date - convert_pr_updated_at))
IssueUpdatedTime=$((convert_live_date - convert_issue_updated_at))
LabelTime=$((convert_live_date - convert_label_created_at))

#time

onemin=60


echo "pull_number: $pull_number"
echo "issue_number: $issue_number"
echo "pr created at: $pr_created_at"
echo "pr updated at: $pr_updated_at"
echo "issue updated at: $issue_updated_at"
echo "label created at: $label_created_at"
echo "--------------------"
echo "live date: $live_date"
echo "convert live date: $convert_live_date"
echo "convert pr updated at: $convert_pr_updated_at" 
echo "convert issue updated at: $convert_issue_updated_at" 
echo "convert label created at: $convert_label_created_at"  

# pull_request updated
prupdate()
{
if [ $PrUpdatedTime -lt $onemin ]
then
  echo "PR updated. Remove stale label"
  curl -X DELETE -u $owner:$token $BASE_URI/repos/$repo/issues/$pull_number/labels \
  -d '{ "labels":["Stale"] }'
fi
}

# PR updated on comments
comments()
{
if [ $IssueUpdatedTime -lt $onemin ]
then
  echo "PR upadted by comments. Remove stale label"
  curl -X DELETE -u $owner:$token $BASE_URI/repos/$repo/issues/$issue_number/labels \
  -d '{ "labels":["Stale"] }'
fi
}

"$@"
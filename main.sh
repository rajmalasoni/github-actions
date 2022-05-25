#!/bin/bash

MERGE_PR="$MERGE_PR"
CLOSE_PR="$CLOSE_PR"
PR_BODY="$PR_BODY"
BASE="$BASE_REF"
HEAD="$HEAD_REF"
SEP="&&"

# for curl API
token="$GITHUB_TOKEN"
BASE_URI="https://api.github.com"
owner="$REPO_OWNER"
repo="$REPO_NAME"
pull_number="$PR_NUMBER"

#date and time of PR
latest_commit_date=$(curl -X GET -u $owner:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number/commits | jq -r '.[-1].commit.committer.date')

live_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
convert_live_date=$(date -u -d "$live_date" +%s)
convert_latest_commit_date=$(date -u -d "$latest_commit_date" +%s)
DIFFERENCE=$((convert_live_date - convert_latest_commit_date))

echo "latest commit date: $latest_commit_date"
echo "live date: $live_date"
echo "convert live date: $convert_live_date"
echo "convert latest commit date: $convert_latest_commit_date"
echo "difference time: $DIFFERENCE"

#time
aday=86400 #24 hrs
two_weeks=1209600 # 14 days

# Stale Pull Request
if [ $DIFFERENCE -lt $two_weeks ]
then
   echo "This PR is active, Don't Close"
elif [ $DIFFERENCE -gt $two_weeks ]
then
   echo "This PR is stale and close because it has been open from 14 days with no activity."
   curl -X POST -u $owner:$token $BASE_URI/repos/$owner/$repo/issues/$pull_number/labels \
  -d '{"labels":["Stale"]}'
   curl -X PATCH -u $owner:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number \
  -d '{ "state": "closed" }'
  curl -X POST -u $owner:$token $BASE_URI/repos/$owner/$repo/issues/$pull_number/comments \
  -d '{"body":"This PR was closed because it has been stalled for 14 days with no activity."}'
else
   echo "None of the condition met"
fi

# Issue comments
case "${MERGE_PR}" in
  "true") 
  echo "PR has Approved."
  curl -X PUT -u $owner:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number/merge \
  -d '{ "merged": true }'
  curl -X POST -u $owner:$token $BASE_URI/repos/$owner/$repo/issues/$pull_number/comments \
  -d '{"body":"Pull Request Merged!"}'
    ;;
  "false") 
    echo "PR hasn't Approved yet.";;
esac

case "${CLOSE_PR}" in
  "true") 
  echo "PR has Closed manually by comments."
  curl -X PATCH -u $owner:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number \
  -d '{ "state": "closed" }'
  curl -X POST -u $owner:$token $BASE_URI/repos/$owner/$repo/issues/$pull_number/comments \
  -d '{"body":"Pull Request Closed!"}'
    ;;
  "false") 
    echo "PR hasn't Closed manually.";;
esac

# Pull_request target master
case "${BASE}${SEP}${HEAD}" in
  "true${SEP}true") 
    echo "should not close PR target from release branch to master";;
  "false${SEP}false") 
    echo "Should not close PR from feature branches";;
  "true${SEP}false") 
    curl -X PATCH -u $owner:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number \
  -d '{ "state": "closed" }'
    curl -X POST -u $owner:$token $BASE_URI/repos/$owner/$repo/issues/$pull_number/comments \
  -d '{"body":"PR from feature branch to master wont accept"}'
    ;;
esac

# Description
if [[ ! $PR_BODY ]]; then
  echo "PR has No valied description" 
  curl -X POST -u $owner:$token $BASE_URI/repos/$owner/$repo/issues/$pull_number/comments \
  -d '{"body":"No Description on PR body. Please add valid description."}'
  curl -X PATCH -u $owner:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number \
  -d '{ "state": "closed" }'
else
  echo "PR has valid Description"
fi
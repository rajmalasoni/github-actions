#!/bin/bash

echo $PR_NUMBER
COMMENT="$COMMENT_BODY"
DESCRIPTION="$PR_BODY"
BASE="$BASE_REF"
HEAD="$HEAD_REF"
SEP="&&"

# for stale actions
PR_URL="$PR_URL"
token="$GITHUB_TOKEN"
BASE_URI="https://api.github.com"
owner="$REPO_OWNER"
repo="$REPO_NAME"
pull_number="$PR_NUMBER"

#date and time of PR
latest_commit_date=$(curl -X GET -u devops-ibs:$token $BASE_URI/repos/$owner/$repo/pulls/$pull_number/commits | jq -r '.[-1].commit.committer.date')

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

if [ $DIFFERENCE -lt $two_weeks ]
then
   echo "This PR is active, Don't Close"
elif [ $DIFFERENCE -gt $two_weeks ]
then
   echo "This PR is stale and close because it has been open from 14 days with no activity."
   gh pr edit $PR_URL --add-label "Stale" 
   gh pr close $PR_URL
   gh pr comment $PR_URL --body "This PR was closed because it has been stalled for 14 days with no activity."
else
   echo "None of the condition met"
fi

# Issue comments
case $COMMENT in
 /Close)
 gh pr close $PR_URL
 gh pr comment $PR_URL --body "Pull Request Closed!"
 ;;
 /Approved)
 gh pr merge $PR_URL -m
 gh pr comment $PR_URL --body "Pull Request Merged!"
 ;;
 *)
 echo "For manually approve or close PR use slash-comments on PR body with /Approved or /Close"
 ;;
esac

# Pull_request target master
case "${BASE}${SEP}${HEAD}" in
  "true${SEP}true") 
    echo "should not close PR target from release branch to master";;
  "false${SEP}false") 
    echo "Should not close PR from feature branches";;
  "true${SEP}false") 
    gh pr close $PR_URL
    gh pr comment $PR_URL --body "PR from feature branch to master won't accept";;
esac

# Description
if [[ ! $DESCRIPTION ]]; then
  echo "PR has No valied description"
  gh pr close $PR_URL
  gh pr comment $PR_URL --body "No Description on PR body. Please add valied description."  
else
  echo "PR has valied Description"
fi
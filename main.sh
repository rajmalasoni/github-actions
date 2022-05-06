# !/bin/bash

PR_URL="$PR_URL"
token="$GITHUB_TOKEN"
owner="$REPO_OWNER"
repo="$REPO_NAME"
pull_number="$PR_NUMBER"

#time
req_time=864000 #10 days
aday=86400 #24 hrs

#date and time of PR

latest_commit_date=$(curl -X GET -u devops-ibs:$token https://api.github.com/repos/$owner/$repo/pulls/$pull_number/commits | jq -r '.[-1].commit.committer.date')
live_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
convert_live_date=$(date -u -d "$live_date" +%s)
convert_latest_commit_date=$(date -u -d "$latest_commit_date" +%s)
DIFFERENCE=$((convert_live_date - convert_latest_commit_date))

echo "latest commit date: $latest_commit_date"
echo "live date: $live_date"
echo "convert live date: $convert_live_date"
echo "convert latest commit date: $convert_latest_commit_date"
echo "difference time: $DIFFERENCE"

if [ $DIFFERENCE -lt $aday ]
then
   echo "This PR is active. Don't close PR"
elif [ $DIFFERENCE -gt $aday ]
then
   echo "This PR is stale becacuse no activity. Close PR"
   # gh pr close $PR_URL
   # gh pr comment $PR_URL --body "Pull Request is stale"
else
   echo "None of the condition met"
fi
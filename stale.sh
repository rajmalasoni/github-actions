#!/bin/bash

STALE_DAYS=$STALE_DAYS
CLOSE_DAYS=$CLOSE_DAYS

# for curl API
token="$GITHUB_TOKEN"
BASE_URI="https://api.github.com"
owner="$REPO_OWNER"
repo="$REPO_NAME"
pull_number="$PR_NUMBER"

# Stale Pull Request
stale() {

pr_updated_at=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls | jq -r '.[-1].updated_at')

pr_number=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls | jq -r '.[-1].url')
issue_number=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/issues | jq -r '.[-1].url')
comments_url=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/pulls | jq -r '.[-1].comments_url')
label=$(curl -X GET -u $owner:$token $BASE_URI/repos/$repo/issues | jq -r '.[-1].url')

live_date=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
convert_live_date=$(date -u -d "$live_date" +%s)
convert_pr_updated_at=$(date -u -d "$pr_updated_at" +%s)
DIFFERENCE=$((convert_live_date - convert_pr_updated_at))
SECONDSPERDAY=86400
STALE_LABEL=$(( STALE_DAYS * SECONDSPERDAY ))
STALE_CLOSE=$(( CLOSE_DAYS * SECONDSPERDAY ))
# STALE_LABEL=15
# STALE_CLOSE=5
#time
aday=86400 #24 hrs
five_days=100
fifteen_days=150
sixteen_days=864000

echo "live date: $live_date"
echo "convert live date: $convert_live_date"
echo "pr updated at: $pr_updated_at"
echo "convert pr updated date: $convert_pr_updated_at"  
echo "difference time: $DIFFERENCE"
echo "pr number: $pr_number"
echo "Days Before Stale in seconds: $STALE_LABEL"
echo "Days Before Close in seconds: $STALE_CLOSE"

if [ $DIFFERENCE -lt $fifteen_days ]
then
   echo "This PR is active. Don't close PR"

else [ $DIFFERENCE -gt $fifteen_days ]
   echo "This PR is stale because it has been open 15 days with no activity."
   curl -X POST -u $owner:$token $label \
  -d '{ "labels":["Stale"] }'

  curl -X POST -u $owner:$token $comments_url \
  -d '{"body":"This PR is stale because it has been open 15 days with no activity. Remove stale label or comment or this will be closed in 5 days."}' 

fi

# case $((
# (DIFFERENCE < fifteen_days) * 1 +
# (DIFFERENCE > fifteen_days && DIFFERENCE < sixteen_days) * 2)) in
# (1) echo "This PR is active."
#   # curl -X DELETE -u $owner:$token $issue_number/labels/stale
# ;;
# (2) echo "This PR is Stale."
#   curl -X POST -u $owner:$token $label \
#   -d '{ "labels":["Stale"] }'

#   curl -X POST -u $owner:$token $comments_url \
#   -d '{"body":"This PR is stale because it has been open 15 days with no activity. Remove stale label or comment or this will be closed in 2 days."}' 
# ;;

# esac  

}

"$@"
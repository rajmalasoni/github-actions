#!/bin/bash

echo $PR_NUMBER
COMMENT="$COMMENT_BODY"
DESCRIPTION="$PR_BODY"
BASE="$BASE_REF"
HEAD="$HEAD_REF"
SEP="&&"

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
  echo "For manually approve or close PR use slash-comments on body with /Approved or /Close"
  ;;
esac

# target master
case "${BASE}${SEP}${HEAD}" in
  "true${SEP}true") 
    echo "should not close PR target from release branch to master";;
  "false${SEP}false") 
    echo "Should not close PR from other branch";;
  "true${SEP}false") 
    gh pr close $PR_URL
    gh pr comment $PR_URL --body "PR from feature branch to master won't accept";;
esac

# Description
if [[ ! $DESCRIPTION ]]; then
  gh pr close $PR_URL
  gh pr comment $PR_URL --body "No Description on PR body. Please add valied description."  
else
  echo "PR has valied Description"
fi
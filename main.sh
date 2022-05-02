#!/bin/bash

echo "Target & Description Checker"
PR_URL="$PR_URL"
DESCRIPTION="$PR_BODY"
BASE="$BASE_REF"
HEAD="$HEAD_REF"
SEP="&&"

# target master
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
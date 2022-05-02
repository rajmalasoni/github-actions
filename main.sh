#!/bin/bash

echo "Merge and Close PR"
echo $PR_NUMBER
COMMENT="$COMMENT_BODY"

case $COMMENT in
 /Close)
 gh pr close $PR_NUMBER
 gh pr comment $PR_NUMBER --body "Pull Request Closed!"
 ;;
 /Approved)
 gh pr merge $PR_NUMBER -m
 gh pr comment $PR_NUMBER --body "Pull Request Merged!"
 ;;
 *)
 echo "For manually approve or close PR use slash-comments on body with /Approved or /Close"
 ;;
esac


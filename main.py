import os
from github import Github
from datetime import datetime, timedelta
import requests

# env values
g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo(os.environ['REPO_NAME'])
pulls = repo.get_pulls(state='open')
MERGE_PR = os.environ.get("MERGE_PR")
CLOSE_PR = os.environ.get("CLOSE_PR")
VERSION_FILE = os.environ.get("VERSION_FILE")
EVENT = os.environ['EVENT']
GCHAT_WEBHOOK_URL = os.environ['WEBHOOK']

# Global variables
# 2 stale PR
stale_days = 15
# 3.close staled PR if 2 days of no activity
stale_close_days = 2

#MESSAGES
# 2 stale PR 
msg_job2 = 'This PR is stale because it has been open 15 days with no activity. Remove stale label or comment/update PR otherwise this will be closed in next 2 days.'
# 3.close staled PR if 2 days of no activity
msg_job3 = 'This PR was closed because it has been stalled for 2 days with no activity.'
# 4.Check if the pull request targets the master branch directly
msg_job4 = 'Do not accept PR target from feature branch to master branch.'
# 5.Check if the pull request has a description
msg_job5 = 'No Description on PR body. Please add valid description.'
# 6_1 Check if the Approved comment in the pull request comments
commit_message_job6 = 'Pull Request Approved and Merged!'
msg_job6_1 = 'This pull request was approved and merged because of a slash command.'
# 6_2 Check if the Close comment in the pull request comments
msg_job6_2 = 'This pull request was closed because of a slash command.'
# 7. Check All the files and see if there is a file named "VERSION"
msg_job7_success = 'The VERSION file exists. All ohk'
msg_job7_reject = "The VERSION file does not exist. Closing this pull request."
# 8. Check if version name from "VERSION" already exists as tag  
msg_job8_success = "The VERSION didnt matched with tag. All ok"
msg_job8_reject = "The tag from VERSION file already exists. Please update the VERSION file."

print("repo:",repo)
print("pulls:",pulls)

# 1.Check if there are any open pull requests
if pulls.totalCount == 0:
    print('No open pull requests, exiting...')
    exit()

# 2.Add "Stale" label to the PR if no active from 15 days
now = datetime.now()
for pr in pulls:
    try:
        time_diff = now - pr.updated_at
        # check if the time difference is greater than the stale_days
        if time_diff > timedelta(days=stale_days):
            print(f"Pull request: {pr.number} is stale!")
            pr.create_issue_comment(msg_job2)
            pr.add_to_labels('Stale')
    except Exception as e:
        print(f"Error occurred while processing pull request: {pr.number}")
        print(f"Error: {str(e)}")

# 3.close staled PR if 2 days of no activity
for pr in pulls:
    # check if the Stale label is applied on PR
    if "Stale" in [label.name for label in pr.labels]:
        try:
            time_diff = now - pr.updated_at
            # check if the time difference is greater than the stale_close_days
            if time_diff > timedelta(days=stale_close_days):
                print(f"Pull request: {pr.number} is stale and closed!")
                pr.edit(state="closed")
                pr.create_issue_comment(msg_job3)
                print(msg_job3)
        except Exception as e:
            print(f"Error occurred while closing pull request: {pr.number} ")
            print(f"Error: {str(e)}")

print(f"pr_updated_at: {pr.updated_at}")

# 4.Check if the pull request targets the master branch directly
for pull in pulls:
    if pull.base.ref == 'master' and not pull.head.ref.startswith('release/'):
        try:
            print(f"Pull request: {pull.number} was targeted to master")
            pull.edit(state='closed')
            pull.create_issue_comment(msg_job4)
            print(msg_job4)
        except Exception as e:
            print(f"Error occurred while processing pull request: {pull.number} ")
            print(f"Error:  {e} ")

# 5.Check if the pull request has a description
for pull in pulls:
    if not pull.body:
        try:
            print(f"Pull request: {pull.number} has no description" )
            pull.edit(state='closed')
            pull.create_issue_comment(msg_job5)
            print(msg_job5)
        except Exception as e:
            print(f"Error occurred while processing pull request: {pull.number} ")
            print(f"Error:  {e} ")

# 6_1 Check if the Approved comment in the pull request comments
def merge():
    if 'PR_NUMBER' in os.environ:
        pr_number = int(os.environ['PR_NUMBER'])
        pr = repo.get_pull(pr_number)
        print("pr_number:", pr_number)
        print("pr:", pr)
        try:
            pr.merge(merge_method = 'merge', commit_message = commit_message_job6)
            pr.create_issue_comment(msg_job6_1)
            print(msg_job6_1)
        except Exception as e:
            print(f"Failed to merge PR: {str(e)}")
            exit()
# 6_2 Check if the Close comment in the pull request comments
def close():
    if 'PR_NUMBER' in os.environ:
        pr_number = int(os.environ['PR_NUMBER'])
        pr = repo.get_pull(pr_number)
        print(f"pr_number: {pr_number}")
        print(f"pr: {pr}")
        try:
            pr.edit(state="closed")
            pr.create_issue_comment(msg_job6_2)
            print(msg_job6_2)
        except Exception as e:
            print(f"Failed to close PR: {str(e)}")
            exit()

# 7. Check All the files and see if there is a file named "VERSION"
if 'PR_NUMBER' in os.environ:
    try:
        pr_number = int(os.environ['PR_NUMBER'])
        pr = repo.get_pull(pr_number)
        print(f"pr_number: {pr_number}")
        print(f"pr: {pr}")
        files = pr.get_files()
        print(files)
        version_file_exist = False
        for file in files:
            if file.filename == 'VERSION':
                print(f"file : {file}")
                version_file_exist = True
                break
        if version_file_exist:
            print(msg_job7_success)
        else:
            pr.create_issue_comment(msg_job7_reject)
            print(msg_job7_reject)
            pr.edit(state='closed')
        
    except Exception as e:
        print(f"Failed to check VERSION file : {str(e)}")
        print(f"PR_NUMBER : {os.environ['PR_NUMBER']}" )
     
# 8. Check if version name from "VERSION" already exists as tag   
if 'PR_NUMBER' in os.environ:
    try:
        pr_number = int(os.environ['PR_NUMBER'])
        pr = repo.get_pull(pr_number)
        print(f"pr_number: {pr_number}")
        print(f"pr: {pr}")
        print(f"version from VERSION_FILE : {VERSION_FILE}")
        tags = repo.get_tags()
        tag_exist = False
        for tag in tags:
            if tag.name == VERSION_FILE:
                print(f"tag : {tag.name}")
                tag_exist = True
                break

        if not tag_exist:
            print(msg_job8_success)
        else:
            pr.create_issue_comment(msg_job8_reject)
            print(msg_job8_reject)
            pr.edit(state='closed')

    except Exception as e:
        print(f"Failed to compare version from VERSION  with tag: {str(e)}")
        print(f"PR_NUMBER : {os.environ['PR_NUMBER']}")

# 9. Google chat integration with github
if 'EVENT' in os.environ:
    try:
        pr_number = int(os.environ['PR_NUMBER'])
        pr = repo.get_pull(pr_number)
        message = f"An Event is created on PR:\nTitle: {pr.title}\nURL: {pr.html_url}"

        set_message = {
            "opened": f"New Pull Request:\nTitle: {pr.title}\nURL: {pr.html_url}",
            "edited": f"Pull Request Edited:\nTitle: {pr.title}\nURL: {pr.html_url}",
            "closed": f"Pull Request Closed:\nTitle: {pr.title}\nURL: {pr.html_url}",
            "reopened": f"Pull Request Reopened:\nTitle: {pr.title}\nURL: {pr.html_url}",
            # Add more cases as needed
        }

        message = set_message.get(EVENT, message)

        payload = {
            "text" : message
        }

        response = requests.post(GCHAT_WEBHOOK_URL, json=payload)
        print(response)
        print(EVENT)

    except Exception as e:
        print(f"Failed to send notification on google chat: {str(e)}")
        print(f"PR_NUMBER : {os.environ['PR_NUMBER']}")

if __name__ == '__main__':
    print('start')
    if MERGE_PR.__eq__('true'):
        merge()  
    if CLOSE_PR.__eq__('true'):
        close()   
    print('end')      
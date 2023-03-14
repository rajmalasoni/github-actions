import os
from github import Github
from datetime import datetime, timedelta

# env values
g = Github(os.environ["GITHUB_TOKEN"])
repo_name = os.environ.get("REPO_NAME")
pull_number = int(os.environ.get("PR_NUMBER"))
MERGE_PR = os.environ.get("MERGE_PR")
CLOSE_PR = os.environ.get("CLOSE_PR")
PR_DESCRIPTION = os.environ.get("PR_DESCRIPTION")
BASE = os.environ.get("BASE_REF")
HEAD = os.environ.get("HEAD_REF")

repo = g.get_repo(repo_name)
pr = repo.get_pull(pull_number)
pulls = repo.get_pulls(state='open')

print("repo_name_wf:",repo_name)
print("pr-num-wf:",pull_number)
print("repo_name:",repo)
print("pr_number:",pr.number)
print("pulls:",pulls)

# Add "Stale" label to the PR if no active from 15 days
stale_days = 15
now = datetime.now()
for pr in pulls:
    time_diff = now - pr.updated_at
    # check if the time difference is greater than the stale days
    if time_diff > timedelta(days=stale_days):
        print("Pull request", pr.number, "is stale!")
        pr.create_issue_comment('This PR is stale because it has been open 15 days with no activity. Remove stale label or comment or this will be closed in 2 days.')
        pr.add_to_labels('Stale')

# close staled PR if 2 days of no activity
stale_close_days = 2
for pr in pulls:
    # check if the stale label is applied on PR
    if "Stale" in [label.name for label in pr.labels]:
        time_diff = now - pr.updated_at
        # check if the time difference is greater than the stale close days
        if time_diff > timedelta(days=stale_close_days):
            print("Pull request", pr.number, "is stale and closed!")
            pr.edit(state="closed")
            pr.create_issue_comment('This PR was closed because it has been stalled for 2 days with no activity.')

print("pr_updated_at:",pr.updated_at)
print("pr_labels:",pr.labels)

def merge():
    print("PR has Approved.")
    # merge API
    pr.merge(merge_method = 'merge', commit_message ='Pull Request Approved and Merged!')
    #  merge API comment
    pr.create_issue_comment('Pull Request Approved and Merged!')

def close():
    print("PR has Closed manually by comments.")
    # closed API
    pr.edit(state='closed')
    # closed API comment
    pr.create_issue_comment('Pull Request Closed!')

def target():
    # API comment
    pr.create_issue_comment('Do not accept PR target from feature branch to master branch.')
    # closed API
    pr.edit(state='closed')


def description():
    # API comment
    pr.create_issue_comment('No Description on PR body. Please add valid description.')
    # closed API
    pr.edit(state='closed')

if __name__ == '__main__':
    print('start')
    if MERGE_PR.__eq__('true'):
        merge()  
    if CLOSE_PR.__eq__('true'):
        close()  
    if BASE.__eq__('true') and  HEAD.__eq__('false'):
        target() 
    if PR_DESCRIPTION.__eq__('true'):
        description() 
    print('end')

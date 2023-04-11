import os
from github import Github
from datetime import datetime, timedelta

# env values
g = Github(os.environ["GITHUB_TOKEN"])
repo_name = os.environ.get("REPO_NAME")
repo = g.get_repo(repo_name)
pulls = repo.get_pulls(state='open')

# Check if there are any open pull requests
if pulls.totalCount == 0:
    print('No open pull requests, exiting...')
    exit()


# # Get the pull request number from the environment variable
# pull_number_str = os.environ.get('PR_NUMBER')
# print(f"PR_NUMBER: {pull_number_str}")

# # Parse the pull request number as an integer
# pull_number = int(pull_number_str)
# print("pull_number:",pull_number)

# # Get the pull request object
# pull_request = repo.get_pull(pull_number)
# print("pull_request:",pull_request)
# pr = repo.get_pull(pull_number)
# print("pr:",pr)
# pull_number = int(os.environ.get("PR_NUMBER"))
pull_number = os.environ.get('PR_NUMBER')
print("pull_number:",pull_number)

pr = repo.get_pull(int(pull_number))
print("pull_request:",pr)

MERGE_PR = os.environ.get("MERGE_PR")
CLOSE_PR = os.environ.get("CLOSE_PR")
PR_DESCRIPTION = os.environ.get("PR_DESCRIPTION")
BASE = os.environ.get("BASE_REF")
HEAD = os.environ.get("HEAD_REF")



# print("pr:",pr)
# print("repo_name_wf:",repo_name)
# print("pr-num-wf:",pull_number)
# print("repo_name:",repo)
# print("pr_number:",pr.number)
# print("pulls:",pulls)

# Add "Stale" label to the PR if no active from 15 days
stale_days = 15
now = datetime.now()
for pr in pulls:
    time_diff = now - pr.updated_at
    # check if the time difference is greater than the stale days
    if time_diff > timedelta(days=stale_days):
        print("Pull request", pr.number, "is stale!")
        pr.create_issue_comment('This PR is stale because it has been open 15 days with no activity. Remove stale label or comment/update PR otherwise this will be closed in next 2 days.')
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
    for pull in pulls:
        # Check if the comment trigger is in the pull request comments
        for comment in pull.get_issue_comments():
            if comment.body.startswith('/Approved'):
                # Merge the pull request
                pull.merge()
                pull.create_issue_comment('Pull Request is Approved and Merged!')

    print("PR has Approved.")
    # merge API
    pr.merge(merge_method = 'merge', commit_message ='Pull Request Approved and Merged!')
    #  merge API comment
    pr.create_issue_comment('Pull Request Approved and Merged!')

def close():
    for pull in pulls:
        # Check if the comment trigger is in the pull request comments
        for comment in pull.get_issue_comments():
            if comment.body.startswith('/Close'):
                # Close the pull request
                pull.edit(state='closed')
                pull.create_issue_comment('Pull Request Closed!') 
    # print("PR has Closed manually by comments.")
    # # closed API
    # pr.edit(state='closed')
    # # closed API comment
    # pr.create_issue_comment('Pull Request Closed!')

# Check if the pull request targets the master branch directly
for pull in pulls:
    # Check if the pull request targets the master branch directly
    if pull.base.ref == 'master' and not pull.head.ref.startswith('release/'):
        pull.edit(state='closed')
        pull.create_issue_comment('Do not accept PR target from feature branch to master branch.')

# Check if the pull request has a description
for pull in pulls:
    if not pull.body:
        pull.edit(state='closed')
        pull.create_issue_comment('No Description on PR body. Please add valid description.')
# def target():
#     # API comment
#     pr.create_issue_comment('Do not accept PR target from feature branch to master branch.')
#     # closed API
#     pr.edit(state='closed')


# def description():
#     # API comment
#     pr.create_issue_comment('No Description on PR body. Please add valid description.')
#     # closed API
#     pr.edit(state='closed')

if __name__ == '__main__':
    print('start')
    if MERGE_PR.__eq__('true'):
        merge()  
    if CLOSE_PR.__eq__('true'):
        close()  
    # if BASE.__eq__('true') and  HEAD.__eq__('false'):
    #     target() 
    # if PR_DESCRIPTION.__eq__('true'):
    #     description() 
    print('end')
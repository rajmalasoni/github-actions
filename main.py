import requests
import json
import os
from github import Github

access_token = os.environ.get("GITHUB_TOKEN")
g = Github(access_token)
repo_name = os.environ.get("REPO_NAME")
pull_number = int(os.environ.get("PR_NUMBER"))

repo = g.get_repo(repo_name)
pr = repo.get_pull(pull_number)

# values
MERGE_PR = os.environ.get("MERGE_PR")
CLOSE_PR = os.environ.get("CLOSE_PR")
PR_DESCRIPTION = os.environ.get("PR_DESCRIPTION")
BASE = os.environ.get("BASE_REF")
HEAD = os.environ.get("HEAD_REF")

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

import os
from github import Github
from datetime import datetime, timedelta
import requests

try:
    # env values
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ['REPO_NAME'])
    pulls = repo.get_pulls(state='open')

    pr_number = int(os.environ['PR_NUMBER']) if ( os.environ['PR_NUMBER'] ) else None
    pr = repo.get_pull(pr_number) if(pr_number) else None    

    MERGE_PR = os.environ.get("MERGE_PR")
    CLOSE_PR = os.environ.get("CLOSE_PR")
    VERSION_FILE = os.environ.get("VERSION_FILE")
    EVENT = os.environ['EVENT']
    GCHAT_WEBHOOK_URL = os.environ['WEBHOOK']

    msg = {
        # 1 stale PR 
        "stale_label" : 'This PR is stale because it has been open 15 days with no activity. Remove stale label or comment/update PR otherwise this will be closed in next 2 days.' ,
        "stale_days" : 15,
        "stale_close_days" : 2,
        # 2.close staled PR if 2 days of no activity
        "staled_PR_closing" : 'This PR was closed because it has been stalled for 2 days with no activity.' ,
        # 3.Check if the pull request targets the master branch directly
        "check_PR_target" : 'Do not accept PR target from feature branch to master branch.' ,
        # 4.Check if the pull request has a description
        "check_description" : 'No Description on PR body. Please add valid description.' ,
        # 5_1 Check if the Approved comment in the pull request comments
        "approve_merge" : 'Pull Request Approved and Merged!' ,
        "approve_comment" : 'This pull request was approved and merged because of a slash command.' ,
        # 5_2 Check if the Close comment in the pull request comments
        "closing_comment" : 'This pull request was closed because of a slash command.' ,
        # 6. Check All the files and see if there is a file named "VERSION"
        "check_version_file" : 'The VERSION file exists. All ohk' ,
        "version_file_inexistence" : "The VERSION file does not exist. Closing this pull request." ,
        # 7. Check if version name from "VERSION" already exists as tag  
        "tagcheck_success" : "The VERSION didnt matched with tag. All ok" ,
        "tagcheck_reject" : "The tag from VERSION file already exists. Please update the VERSION file.",
        # 8. Close the PR having DO NOT MERGE LABEL
        "label" : "Please remove DO NOT MERGE LABEL",
        # 9. message need to be placed here
    }
    if pr:
        msg["default"] = f"An Event is created on PR:\nTitle: {pr.title}\nURL: {pr.html_url}"
        msg["opened"] = f"New Pull Request Created by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}"
        msg["edited"] = f"Pull Request Edited by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}"
        msg["closed"] = f"Pull Request Closed by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}"
        msg["reopened"] = f"Pull Request Reopened by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}"


    print("repo:",repo)
    print("pulls:",pulls)

    # 1.Add "Stale" label to the PR if no active from 15 days
    now = datetime.now()

    for pull in pulls:
        time_diff = now - pull.updated_at
        # 1. Check if the time difference is greater than the stale_days
        if time_diff > timedelta(days=msg.get("stale_days")):
            print(f"Pull request: {pull.number} is stale!")
            pull.create_issue_comment( msg.get("stale_label") )
            pull.add_to_labels('Stale')

        # 2. Close staled PR if 2 days of no activity
        if "Stale" in [label.name for label in pull.labels]:
            # check if the time difference is greater than the stale_close_days
            if time_diff > timedelta(days=msg.get("stale_close_days")):
                print(f"Pull request: {pull.number} is stale and closed!")
                print(msg.get("staled_PR_closing"))
                pull.edit(state="closed")
                pull.create_issue_comment(msg.get("staled_PR_closing") )

        # 3.Check if the pull request targets the master branch directly
        if pull.base.ref == 'master' and not pull.head.ref.startswith('release/'):
            print(f"Pull request: {pull.number} was targeted to master")
            print(msg.get("check_PR_target"))
            pull.edit(state='closed')
            pull.create_issue_comment(msg.get("check_PR_target") )

        # 4.Check if the pull request has a description
        if not pull.body:
            print(f"Pull request: {pull.number} has no description" )
            pull.edit(state='closed')
            pull.create_issue_comment(msg.get("check_description"))
            print(msg.get("check_description"))

    # 5_1 Check if the Approved comment in the pull request comments
    if MERGE_PR.__eq__('true'):
        if pr:    
            pr.merge(merge_method = 'merge', commit_message = msg.get("approve_merge"))
            pr.create_issue_comment(msg.get("approve_comment"))
            print(msg.get("approve_comment"))

    # 5_2 Check if the Close comment in the pull request comments
    if CLOSE_PR.__eq__('true'):
        if pr:            
            pr.edit(state="closed")
            pr.create_issue_comment(msg.get("closing_comment"))
            print(msg.get("closing_comment"))

    # 6. Check All the files and see if there is a file named "VERSION"
    if pr:        
        files = pr.get_files()
        print(files)
        version_file_exist = False
        for file in files:
            if file.filename == 'VERSION':
                print(f"file : {file}")
                version_file_exist = True
                break
        if version_file_exist:
            print(msg.get("check_version_file") )
        else:
            pr.create_issue_comment(msg.get("version_file_inexistence") )
            print(msg.get("version_file_inexistence"))
            pr.edit(state='closed')

    # 7. Check if version name from "VERSION" already exists as tag   
    if pr and VERSION_FILE:    
        print(f"version from VERSION_FILE : {VERSION_FILE}")
        tags = repo.get_tags()
        tag_exist = False
        for tag in tags:
            if tag.name == VERSION_FILE:
                print(f"tag : {tag.name}")
                tag_exist = True
                break
        if not tag_exist:
            print(msg.get("tagcheck_success") )
        else:
            pr.create_issue_comment(msg.get("tagcheck_reject") )
            print(msg.get("tagcheck_reject") )
            pr.edit(state='closed')

    # 8. Do not merge PR message and close the PR
    if pr:
        labels = pr.get_labels()
        print(pr)
        print(pr_number)
        print(labels)
        if "DO NOT MERGE" in [label.name for label in labels]:
            pr.edit(state='closed')
            pr.create_issue_comment(msg.get("label"))
            print(msg.get("label"))        

    # 9. Google chat integration with github
    if EVENT and GCHAT_WEBHOOK_URL:
        message = msg.get("default")
        message = msg.get(EVENT, message)

        payload = {
            "text" : message
        }

        response = requests.post(GCHAT_WEBHOOK_URL, json=payload)
        print(response)
        print(EVENT)

except Exception as e:
    print(f"Failed to run the job. exception: {str(e)}")      
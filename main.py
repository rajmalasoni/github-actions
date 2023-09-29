import os
from github import Github
from datetime import datetime, timedelta
import requests

try:
    # env values
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ['REPO_NAME'])
    pulls = repo.get_pulls(state='open')

    pr_number = int(os.environ['PR_NUMBER']) if ( os.environ['PR_NUMBER'] ) else None;
    pr = repo.get_pull(pr_number) if(pr_number) else None;
    labels = pr.get_labels()
    
    

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

    msg = {
        # 2 stale PR 
        "job2" : 'This PR is stale because it has been open 15 days with no activity. Remove stale label or comment/update PR otherwise this will be closed in next 2 days.' ,
        # 3.close staled PR if 2 days of no activity
        "job3" : 'This PR was closed because it has been stalled for 2 days with no activity.' ,
        # 4.Check if the pull request targets the master branch directly
        "job4" : 'Do not accept PR target from feature branch to master branch.' ,
        # 5.Check if the pull request has a description
        "job5" : 'No Description on PR body. Please add valid description.' ,
        # 6_1 Check if the Approved comment in the pull request comments
        "job6_commit_message" : 'Pull Request Approved and Merged!' ,
        "job6_1" : 'This pull request was approved and merged because of a slash command.' ,
        # 6_2 Check if the Close comment in the pull request comments
        "job6_2" : 'This pull request was closed because of a slash command.' ,
        # 7. Check All the files and see if there is a file named "VERSION"
        "job7_success" : 'The VERSION file exists. All ohk' ,
        "job7_reject" : "The VERSION file does not exist. Closing this pull request." ,
        # 8. Check if version name from "VERSION" already exists as tag  
        "job8_success" : "The VERSION didnt matched with tag. All ok" ,
        "job8_reject" : "The tag from VERSION file already exists. Please update the VERSION file."
    }

    #MESSAGES
    # 9. message need to be placed here
    if(pr):
        msg_job9_opened = f"New Pull Request Created by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}";
        msg_job9_edited = f"Pull Request Edited by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}";
        msg_job9_closed = f"Pull Request Closed by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}";
        msg_job9_reopened = f"Pull Request Reopened by {pr.user.login}:\nTitle: {pr.title}\nURL: {pr.html_url}";

    print("repo:",repo)
    print("pulls:",pulls)

    # 1.Add "Stale" label to the PR if no active from 15 days
    now = datetime.now()
    for pr in pulls:
        time_diff = now - pr.updated_at
        # check if the time difference is greater than the stale_days
        if time_diff > timedelta(days=stale_days):
            print(f"Pull request: {pr.number} is stale!")
            pr.create_issue_comment( msg.get("job2") )
            pr.add_to_labels('Stale')

    # 2.close staled PR if 2 days of no activity
    if pulls.totalCount != 0:
        for pr in pulls:
            # check if the Stale label is applied on PR
            if "Stale" in [label.name for label in pr.labels]:
                time_diff = now - pr.updated_at
                # check if the time difference is greater than the stale_close_days
                if time_diff > timedelta(days=stale_close_days):
                    print(f"Pull request: {pr.number} is stale and closed!")
                    pr.edit(state="closed")
                    pr.create_issue_comment(msg.get("job3") )
                    print(msg.get("job3"))
        print(f"pr_updated_at: {pr.updated_at}")

    # 3.Check if the pull request targets the master branch directly
    for pull in pulls:
        if pull.base.ref == 'master' and not pull.head.ref.startswith('release/'):
            print(f"Pull request: {pull.number} was targeted to master")
            pull.edit(state='closed')
            pull.create_issue_comment(msg.get("job4") )
            print(msg.get("job4"))

    # 4.Check if the pull request has a description
    for pull in pulls:
        if not pull.body:
            print(f"Pull request: {pull.number} has no description" )
            pull.edit(state='closed')
            pull.create_issue_comment(msg.get("job5"))
            print(msg.get("job5"))

    # 5_1 Check if the Approved comment in the pull request comments
    if MERGE_PR.__eq__('true'):
        if 'PR_NUMBER' in os.environ:
            pr_number = int(os.environ['PR_NUMBER'])
            pr = repo.get_pull(pr_number)
            print("pr_number:", pr_number)
            print("pr:", pr)
            pr.merge(merge_method = 'merge', commit_message = msg.get("job6_commit_message"))
            pr.create_issue_comment(msg.get("job6_1"))
            print(msg.get("job6_1"))

    # 5_2 Check if the Close comment in the pull request comments
    if CLOSE_PR.__eq__('true'):
        if 'PR_NUMBER' in os.environ:
            pr_number = int(os.environ['PR_NUMBER'])
            pr = repo.get_pull(pr_number)
            print(f"pr_number: {pr_number}")
            print(f"pr: {pr}")
            pr.edit(state="closed")
            pr.create_issue_comment(msg.get("job6_2"))
            print(msg.get("job6_2"))

    # 6. Check All the files and see if there is a file named "VERSION"
    if 'PR_NUMBER' in os.environ:
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
            print(msg.get("job7_success") )
        else:
            pr.create_issue_comment(msg.get("job7_reject") )
            print(msg.get("job7_reject"))
            pr.edit(state='closed')

    # 7. Check if version name from "VERSION" already exists as tag   
    if 'PR_NUMBER' in os.environ:
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
            print(msg.get("job8_success") )
        else:
            pr.create_issue_comment(msg.get("job8_reject") )
            print(msg.get("job8_reject") )
            pr.edit(state='closed')

    # 8. Google chat integration with github
    if 'EVENT' in os.environ:
        pr_number = int(os.environ['PR_NUMBER'])
        pr = repo.get_pull(pr_number)
        message = f"An Event is created on PR:\nTitle: {pr.title}\nURL: {pr.html_url}"
        set_message = {
            "opened": msg_job9_opened,
            "edited": msg_job9_edited,
            "closed": msg_job9_closed,
            "reopened": msg_job9_reopened,
        }

    # 9. Do not merge PR message and close the PR
    for label in labels:
    # print(label.name)
        if label.name == "DO NOT MERGE":
            pr.edit(state='closed')
            pr.create_issue_comment("Please remove DO NOT MERGE LABEL")
            message = set_message.get(EVENT, message)

        payload = {
            "text" : message
        }

        response = requests.post(GCHAT_WEBHOOK_URL, json=payload)
        print(response)
        print(EVENT)

except Exception as e:
    print(f"Failed to run the job. exception: {str(e)}")      
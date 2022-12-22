import requests
import json
import os

# API
BASE_URI = "https://api.github.com"
owner = os.environ.get("REPO_OWNER")
repo = os.environ.get("REPO_NAME")
token = os.environ.get("GITHUB_TOKEN")
pull_number = os.environ.get("PR_NUMBER")

# values
MERGE_PR = os.environ.get("MERGE_PR")
CLOSE_PR = os.environ.get("CLOSE_PR")
PR_DESCRIPTION = os.environ.get("PR_DESCRIPTION")
BASE = os.environ.get("BASE_REF")
HEAD = os.environ.get("HEAD_REF")

def merge():
    print("PR has Approved.")
    # merge API
    url = BASE_URI+"/repos/" + repo + "/pulls/" + str(pull_number) + "/merge"
    data = json.dumps({"merged": True})
    headers = {'Authorization': 'token '+token}
    res = requests.put(url, data, headers=headers)
    print("merge API status code: {}".format(res.status_code) )

    #  merge API comment
    url = BASE_URI+"/repos/" + repo + "/issues/" + str(pull_number) + "/comments"
    data = json.dumps({"body": "Pull Request Merged!"})
    res = requests.post(url, data, headers=headers)
    print("merge API comment status code: {}".format(res.status_code))


def close():
    print("PR has Closed manually by comments.")
    # closed API
    url = BASE_URI + "/repos/" + repo + "/pulls/" + str(pull_number)
    data = json.dumps({ "state": "closed" })
    headers = {'Authorization': 'token ' + token}
    res = requests.patch(url, data, headers=headers)
    print("Close API status code: {}".format(res.status_code))

    # closed API comment
    url = BASE_URI + "/repos/" + repo + "/issues/" + str(pull_number) + "/comments"
    data = json.dumps({"body":"Pull Request Closed!"})
    res = requests.post(url, data, headers=headers)
    print("close API comment status code: {}".format(res.status_code))


def target():
    url = BASE_URI + "/repos/" + repo + "/pulls/" + str(pull_number)
    data = json.dumps({"state": "closed"})
    headers = {'Authorization': 'token ' + token}
    res = requests.patch(url, data, headers=headers)
    print("target API status code: {}".format(res.status_code))

    url = BASE_URI + "/repos/" + repo + "/issues/" + str(pull_number) + "/comments"
    data = json.dumps({"body": "Do not accept PR target from feature branch to master branch."})
    res = requests.post(url, data, headers=headers)
    print("target API comment status code: {}".format(res.status_code))


def description():
    url = BASE_URI + "/repos/" + repo + "/pulls/" + str(pull_number)
    data = json.dumps({"state": "closed"})
    headers = {'Authorization': 'token ' + token}
    res = requests.patch(url, data, headers=headers)
    print("description API status code: {}".format(res.status_code))

    url = BASE_URI + "/repos/" + repo + "/issues/" + str(pull_number) + "/comments"
    data = json.dumps({"body": "No Description on PR body. Please add valid description."})
    res = requests.post(url, data, headers=headers)
    print("description API comment status code: {}".format(res.status_code))


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
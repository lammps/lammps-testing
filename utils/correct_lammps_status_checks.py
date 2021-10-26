#!/bin/env python3
# requires PyGithub and a GH API token with status API access
from github import Github
import urllib.request
import json
import os
import sys

def get_jenkins_result(target_url):
    parts = target_url.split('/')
    api_url = '/'.join(parts[:-2] + ['api', 'json'])
    request = urllib.request.Request(api_url)
    response = urllib.request.urlopen(request).read()
    content = json.loads(response.decode('utf-8'))
    return content["result"]

def correct_ci_statuses(commit):
    status = commit.get_statuses()
    query = {}

    for s in status:
        if s.context.startswith("dev") and (s.context not in query or s.id > query[s.context]['id']):
             query[s.context] = {'state': s.state, 'target_url': s.target_url, 'id': s.id}

    for context, values in query.items():
        jenkins_result = get_jenkins_result(values['target_url'])
        if values['state'] == 'pending' and jenkins_result == "SUCCESS":
            print("Updating", context)
            commit.create_status(state='success', target_url=values['target_url'], description="build successful!", context=context)
        elif values['state'] == 'pending' and jenkins_result == "FAILURE":
            print("Updating", context)
            commit.create_status(state='failure', target_url=values['target_url'], description="build failed!", context=context)

token = os.getenv("GITHUB_API_TOKEN")

if token is None:
  print("GITHUB_API_TOKEN not defined!")
  sys.exit(-1)

g = Github(token)
repo = g.get_repo("lammps/lammps")

branch = repo.get_branch("develop")

correct_ci_statuses(branch.commit)

pulls = repo.get_pulls(state='open', sort='created', base='develop')

for pr in pulls:
    commits = pr.get_commits()
    head = commits[commits.totalCount-1]
    print(pr.number, head)
    correct_ci_statuses(head)

pulls = repo.get_pulls(state='open', sort='created', base='stable')

for pr in pulls:
    commits = pr.get_commits()
    head = commits[commits.totalCount-1]
    print(pr.number, head)
    correct_ci_statuses(head)

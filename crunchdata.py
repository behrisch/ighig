#!/usr/bin/env python3

import os
import sys
import json
import csv
import re

root = sys.argv[1] if len(sys.argv) > 1 else "github-backup/repositories/sumo/"
with open('issues.csv', 'w') as out:
    print('issue,time,closed,by,label,assignee', file=out)
    writer = csv.writer(out)
    for issueFile in os.listdir(os.path.join(root, "issues")):
        issue = json.load(open(os.path.join(root, "issues", issueFile)))
        closed = issue["closed_at"] if issue["closed_at"] else "2222-01-01T00:00:00Z"
        for comment in issue["comment_data"]:
            if re.search('changed status from .* to "closed"', comment["body"]):
                closed = comment["created_at"]
        for label in issue.get("labels") or [{}]:
            for assignee in issue.get("assignees") or [{}]:
                writer.writerow((issue["number"], issue["created_at"], closed, issue["user"]["login"], label.get("name"), assignee.get("login")))
with open('labels.csv', 'w') as out:
    print('label,color', file=out)
    writer = csv.writer(out)
    for label in json.load(open(os.path.join(root, "labels", "labels.json"))):
        writer.writerow((label["name"], '#' + label["color"]))
with open('milestones.csv', 'w') as out:
    print('milestone,due', file=out)
    writer = csv.writer(out)
    for milestoneFile in os.listdir(os.path.join(root, "milestones")):
        milestone = json.load(open(os.path.join(root, "milestones", milestoneFile)))
        due = milestone["closed_at"] if milestone["closed_at"] else milestone["due_on"]
        writer.writerow((milestone["title"], due))

#!/usr/bin/env python3

import os
import sys
import json
import pandas as pd
import csv
import re

columns = ['number', 'time', 'closed', 'by', 'label', 'label_color', 'assignee']
root = sys.argv[1] if len(sys.argv) > 1 else "github-backup/repositories/sumo/issues"
with open('out.csv', 'w') as out:
    print(','.join(columns), file=out)
    writer = csv.writer(out)
    for issueFile in os.listdir(root):
        issue = json.load(open(os.path.join(root, issueFile)))
        closed = issue["closed_at"] if issue["closed_at"] else "2222-01-01T00:00:00Z"
        for comment in issue["comment_data"]:
            if re.search('changed status from .* to "closed"', comment["body"]):
                closed = comment["created_at"]
        for label in issue.get("labels") or [{}]:
            for assignee in issue.get("assignees") or [{}]:
                writer.writerow((issue["number"], issue["created_at"], closed, issue["user"]["login"], label.get("name"), label.get("color"), assignee.get("login")))

#!/usr/bin/env python3

import os
import sys
import argparse
import json
import csv
import re


def parse_args():
    parser = argparse.ArgumentParser(description='Retrieve github issue data for dash graph')
    parser.add_argument('repo', help='local directory or github repo name')
    parser.add_argument('-u', '--username', help='username for basic auth')
    parser.add_argument('-p', '--password', help='password for basic auth. '
                             'If a username is given but not a password, the '
                             'password will be prompted for.')
    parser.add_argument('-t', '--token', help='personal access or OAuth token')
    parser.add_argument('-r', '--close-regex', default='changed status from .* to "closed"',
                        help='regular expression to have a comment as closing event')
    parser.add_argument('-e', '--creator-regex', default=r'"reporter": "(\w*)"',
                        help='regular expression to have a comment as closing event')
    parser.add_argument('-o', '--output-directory', default='.',
                        help='directory at which to write the issue data')
    return parser.parse_args()

def write_labels(outdir, labels):
    with open(os.path.join(outdir, 'labels.csv'), 'w') as out:
        print('label,color', file=out)
        writer = csv.writer(out)
        for label in labels:
            writer.writerow((label["name"], '#' + label["color"]))

def write_milestones(outdir, milestones):
    with open(os.path.join(outdir, 'milestones.csv'), 'w') as out:
        print('milestone,due', file=out)
        writer = csv.writer(out)
        for milestone in milestones:
            due = milestone["closed_at"] if milestone["closed_at"] else milestone["due_on"]
            writer.writerow((milestone["title"], due))

def read_json(root, options):
    with open(os.path.join(options.output_directory, 'issues.csv'), 'w') as out:
        print('issue,time,closed,creator,label,assignee', file=out)
        writer = csv.writer(out)
        for issueFile in os.listdir(os.path.join(root, "issues")):
            issue = json.load(open(os.path.join(root, "issues", issueFile)))
            closed = issue["closed_at"] if issue["closed_at"] else "2222-01-01T00:00:00Z"
            if options.close_regex:
                for comment in issue["comment_data"]:
                    if re.search(options.close_regex, comment["body"]):
                        closed = comment["created_at"]
            creator = issue["user"]["login"]
            if options.creator_regex:
                creator_match = re.search(options.creator_regex, issue["body"])
                if creator_match:
                    creator = creator_match.group(1)
            for label in issue.get("labels") or [{}]:
                for assignee in issue.get("assignees") or [{}]:
                    writer.writerow((issue["number"], issue["created_at"], closed, creator, label.get("name"), assignee.get("login")))
    write_labels(options.output_directory, json.load(open(os.path.join(root, "labels", "labels.json"))))
    milestones = []
    for milestoneFile in os.listdir(os.path.join(root, "milestones")):
        milestones.append(json.load(open(os.path.join(root, "milestones", milestoneFile))))
    write_milestones(options.output_directory, milestones)

def read_github_api(repo, options):
    with open(os.path.join(options.output_directory, 'issues.csv'), 'w') as out:
        print('issue,time,closed,creator,label,assignee', file=out)
        writer = csv.writer(out)
        for issue in repo.get_issues(state="all"):
            # print(issue.raw_data)
            closed = issue.raw_data["closed_at"] if issue.closed_at else "2222-01-01T00:00:00Z"
            if options.close_regex:
                for comment in issue.get_comments():
                    if re.search(options.close_regex, comment.body):
                        closed = comment.raw_data["created_at"]
            for label in [label.name for label in issue.get_labels()] or [None]:
                for assignee in [a.login for a in issue.assignees] or [None]:
                    writer.writerow((issue.number, issue.raw_data["created_at"], closed, issue.user.login, label, assignee))
    write_labels(options.output_directory, [label.raw_data for label in repo.get_labels()])
    write_milestones(options.output_directory, [milestone.raw_data for milestone in repo.get_milestones()])

def main():
    args = parse_args()
    output_directory = os.path.realpath(args.output_directory)
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    if args.token or args.username:
        from github import Github
        if args.username:
            g = Github(args.username, args.password)
        else:
            g = Github(args.token)
        read_github_api(g.get_repo(args.repo), args)
    else:
        read_json(args.repo, args)


if __name__ == '__main__':
    main()

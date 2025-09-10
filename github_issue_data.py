#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys

import pandas as pd
import requests


def parse_args():
    parser = argparse.ArgumentParser(description='Retrieve github issue data for dash graph')
    parser.add_argument('repo', help='local directory or github repo name')
    parser.add_argument('-t', '--token', help='personal access or OAuth token')
    parser.add_argument('-r', '--close-regex', default=r'"changetime": "([^"]*)"',
                        help='regular expression to find close time in the issue body (for trac legacy)')
    parser.add_argument('-e', '--creator-regex', default=r'"reporter": "([^"]*)"',
                        help='regular expression to find creator in the issue body (for trac legacy)')
    parser.add_argument('-o', '--output-directory', default='.',
                        help='directory at which to write the issue data')
    parser.add_argument('--csv', action="store_true", default=False, help='generate Parquet output')
    return parser.parse_args()


def write_df(df, outdir, prefix, csv):
    if csv:
        df.to_csv(os.path.join(outdir, prefix + '.csv'), index=False)
    else:
        df.to_parquet(os.path.join(outdir, prefix + '.parquet'), index=False)


def write_labels(outdir, labels, csv):
    df = pd.DataFrame(columns=('label', 'color'))
    for label in labels:
        df.loc[len(df)] = (label["name"], '#' + label["color"])
    write_df(df, outdir, 'labels', csv)


def write_milestones(outdir, milestones, csv):
    df = pd.DataFrame(columns=('milestone', 'due'))
    for milestone in milestones:
        if milestone["due_on"] and milestone["closed_at"] == milestone["created_at"]:
            due = milestone["due_on"]
        else:
            due = milestone["closed_at"]
        df.loc[len(df)] = (milestone["title"], due)
    write_df(df, outdir, 'milestones', csv)


def write_issue(df, issue, options):
    closed = issue["closed_at"] if issue["closed_at"] else "2222-01-01T00:00:00Z"
    if options.close_regex:
        closed_match = re.search(options.close_regex, issue["body"] or "")
        if closed_match:
            closed = closed_match.group(1)
    creator = issue["user"]["login"]
    if options.creator_regex:
        creator_match = re.search(options.creator_regex, issue["body"] or "")
        if creator_match:
            creator = creator_match.group(1)
    issue_type = issue.get("type") or {}
    for label in issue.get("labels") or [{}]:
        for assignee in issue.get("assignees") or [{}]:
            df.loc[len(df)] = (issue["number"], issue["created_at"], closed, creator,
                               issue_type.get("name"), label.get("name"), assignee.get("login"))


def read_json(root, options):
    df = pd.DataFrame(columns=('issue', 'time', 'closed', 'creator', 'type', 'label', 'assignee'))
    for issueFile in os.listdir(os.path.join(root, "issues")):
        issue = json.load(open(os.path.join(root, "issues", issueFile)))
        write_issue(df, issue, options)
    write_df(df, options.output_directory, 'issues', options.csv)
    write_labels(options.output_directory, json.load(open(os.path.join(root, "labels", "labels.json"))), options.csv)
    milestones = []
    for milestoneFile in os.listdir(os.path.join(root, "milestones")):
        milestones.append(json.load(open(os.path.join(root, "milestones", milestoneFile))))
    write_milestones(options.output_directory, milestones, options.csv)


def get_all(s, url):
    r = s.get(url)
    result = r.json()
    while "Link" in r.headers and 'rel="next"' in r.headers["Link"]:
        for link in r.headers["Link"].split(","):
            url, rel = link.split(";")
            if rel.strip() == 'rel="next"':
                url = url.strip()[1:-1]
                break
        r = s.get(url)
        result += r.json()
    return result


def read_github_api(token, options):
    base = "https://api.github.com/repos/" + options.repo 
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json",
                      "Authorization": f"token {token}",
                      "X-GitHub-Api-Version": "2022-11-28"})
    url = base + "/issues?per_page=100&state=all"
    df = pd.DataFrame(columns=('issue', 'time', 'closed', 'creator', 'type', 'label', 'assignee'))
    for issue in get_all(s, url):
        write_issue(df, issue, options)
    write_df(df, options.output_directory, 'issues', options.csv)
    write_labels(options.output_directory, get_all(s, base + "/labels"), options.csv)
    write_milestones(options.output_directory, get_all(s, base + "/milestones?state=all"), options.csv)


def main():
    args = parse_args()
    output_directory = os.path.realpath(args.output_directory)
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    if args.token or not os.path.isdir(args.repo):
        token = args.token
        if not token:
            for cred_path in (".", os.path.dirname(__file__), os.path.expanduser("~")):
                if os.path.exists(os.path.join(cred_path, ".git-credentials")):
                    with open(os.path.join(cred_path, ".git-credentials")) as f:
                        token = f.read().split(":")[-1].split("@")[0]
                        break
        if not token:
            sys.exit("no authentication token found, please use the option --token or provide a .git-credentials file")
        read_github_api(token, args)
    else:
        read_json(args.repo, args)


if __name__ == '__main__':
    main()

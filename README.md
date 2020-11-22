# Interactive GitHub Issue Graphs (ighig)
Plotting github issue statistics with plotly and dash

Plotting issue data is a two step process.
1. Retrieve the data from GitHub
2. Generate the graph

## Retrieving data
The first step is done using github_issue_data.py. It can either use the GitHub API directly
(with the help of [PyGithub](https://github.com/PyGithub/PyGithub/)) or parse the output of
the backup tool [github-backup](https://github.com/josegonzalez/python-github-backup/).

The second method is preferred because backups are always a great idea and github-backup can 
do an incremental backup which makes it easier to work around the query limitations of the 
GitHub API (currently 5000 requests per hour).

For the first method you need to authenticate yourself using a token or user/password. 
If you give either on the command line the script assumes you want the direct API access:
```
./github_issue_data.py -t THiS_IS_A_TOKEN user/my_repo
```
will retrieve the data from https://github.com/user/my_repo/.

The second method only needs the root directory of the backup:
```
./github_issue_data.py github-backup/repositories/my_repo/
```
Both methods generate three csv files in the output directory given by `-o` (default is the current directory).

## Plotting locally
Configure the locations of your input files and the labels you want to show in ighig_config.py.

To test everything locally you need to run `./github_issue_graph.py`. It requires dash, plotly and pandas.
It opens a local webserver and you can browse to http://localhost:8050 to see the results.

## Deploying on Apache
1. Copy at least github_issue_graph.py, ighig.wsgi and ighig_config.py together with your generated data files
to your web server, for instance to /srv/www/ighig.

2. Add something like this to your /etc/apache2/sites-available/000-default.conf
 (or wherever your Apache configuration lives). Adapt IP restrictions to the numbers you want to allow.
```
WSGIScriptAlias /ighig /srv/www/ighig/ighig.wsgi
<Directory /srv/www/ighig>
    WSGIApplicationGroup %{GLOBAL}
    <RequireAll>
        Require all granted
        Require ip  ip.to.be.allowed
    </RequireAll>
</Directory>
```
The first parameter to WSGIScriptAlias defines the last part of the URL to find the results. 

3. Adapt your ighig_config.py, especially make sure that requests_pathname_prefix
 is the same as your WSGIScriptAlias.

## Similar projects
There are other projects analysing GitHub issues:
* https://github.com/nafpliot/github-issue-stats-py (similar approach to ighig but no timelines and no processing of downloaded data)
* https://github.com/cucumber/github-issue-stats (offline plotting using gnuplot)
* https://github.com/markitx/issue-graph (visualize issue relations)


## Disclaimer
All scripts are very much work in progress.

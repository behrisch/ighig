# gh-issue-dash
Plotting github issue statistics with plotly and dash

Plotting issue data is a two step process.
1. Retrieve the data from github
2. Generate the graph

## Retrieving data
The first step is done using crunchdata.py. It can either us the GitHub API directly
(with the help of [PyGithub](https://github.com/PyGithub/PyGithub/)) or parse the output of
the backup tool [github-backup](https://github.com/josegonzalez/python-github-backup/).

The second method is preferred because backups are always a great idea and github-backup can 
do an incremental backup which makes it easier to work around the query limitations of the 
GitHub API (currently 5000 requests per hour).

For the first method you need to authenticate yourself using a token or user/password. 
If you give either on the command line the script assumes you want the direct API access:
```
./crunchdata.py -t THiS_IS_A_TOKEN user/my_repo
```
will retrieve the data from https://github.com/user/my_repo/.

The second method only needs the root directory of the backup:
```
./crunchdata.py github-backup/repositories/my_repo/
```
Both methods generate three csv files in the output directory given by `-o` (default is the current directory).

## Plotting
Currently you need to run `./dashgraph.py`. It requires dash, plotly and pandas.
It opens a local webserver and you can browse to http://localhost:8050 to see the results.

Both scripts are currently very much work in progress.

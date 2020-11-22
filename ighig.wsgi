import os
import sys

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

# this is mainly needed if the server complains about non writeable cache dir
os.environ['PYTHON_EGG_CACHE'] = os.path.join(THIS_DIR, '.python-eggs')

sys.path.insert(0, THIS_DIR)
from github_issue_graph import app

application = app.server

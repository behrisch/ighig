import os

root = os.path.dirname(__file__)

issue_file = os.path.join(root, 'issues.csv')
label_file = os.path.join(root, 'labels.csv')
milestone_file = os.path.join(root, 'milestones.csv')

stacked_labels=['bug', 'enhancement', 'question']
default_labels=stacked_labels[:1]

requests_pathname_prefix=None
# requests_pathname_prefix='/ghis/'

import os

root = os.path.dirname(__file__)

issue_file = os.path.join(root, 'issues.csv')
label_file = os.path.join(root, 'labels.csv')
milestone_file = os.path.join(root, 'milestones.csv')

stacked_labels=['bug', 'enhancement', 'question']
default_labels=stacked_labels[:1]

requests_pathname_prefix=None
# requests_pathname_prefix='/ghis/'


def get_label_filters(labels):
    app_label = []
    the_rest = []
    for label in labels:
        if label.startswith("a:"):
            app_label.append(label)
        else:
            the_rest.append(label)
    return app_label, the_rest

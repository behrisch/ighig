import os

root = os.path.dirname(__file__)

issue_file = os.path.join(root, 'issues.parquet')
label_file = os.path.join(root, 'labels.parquet')
milestone_file = os.path.join(root, 'milestones.parquet')

categories=['Bug', 'Feature', 'Question']
# categories=['bug', 'enhancement', 'question']
selected_categories=categories[:1]
use_types=True

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

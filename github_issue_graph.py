#!/usr/bin/env python3

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import ighig_config

if ighig_config.issue_file.endswith(".parquet"):
    issues = pd.read_parquet(ighig_config.issue_file)
    label_colors = pd.read_parquet(ighig_config.label_file).set_index('label').to_dict()['color']
    milestones = pd.read_parquet(ighig_config.milestone_file)
else:
    issues = pd.read_csv(ighig_config.issue_file)
    label_colors = pd.read_csv(ighig_config.label_file).set_index('label').to_dict()['color']
    milestones = pd.read_csv(ighig_config.milestone_file, parse_dates=['due'])
creators = issues[['issue', 'creator']].drop_duplicates().groupby('creator').count()
top_creators = creators.sort_values('issue', ascending=False).index[:10]
milestone_lines = []
for milestone in milestones.values:
    if not pd.isnull(milestone[1]):
        milestone_lines.append(dict(
            type='line', yref='paper', y0=0, y1=1,
            xref='x', x0=milestone[1], x1=milestone[1]
        ))

app = dash.Dash(__name__, requests_pathname_prefix=ighig_config.requests_pathname_prefix)
filter_dropdowns = []
filter_inputs = []
for idx, label_filter in enumerate(ighig_config.get_label_filters(label_colors)):
    filter_dropdowns.append(dcc.Dropdown(
        id='label-dropdown%s' % idx,
        options=[{'label': label, 'value': label} for label in label_filter],
        value=[],
        multi=True
    ))
    filter_inputs.append(Input('label-dropdown%s' % idx, 'value'))

app.layout = html.Div([
    dcc.Graph(id='graph-with-selector'),
    html.Label("Issue categories to plot"),
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': category, 'value': category} for category in ighig_config.categories],
        value=ighig_config.selected_categories,
        multi=True
    ),
    html.Label("Creator filter"),
    dcc.Dropdown(
        id='creator-dropdown',
        options=[{'label': creator, 'value': creator} for creator in top_creators],
        value=[],
        multi=True
    ),
    html.Label("Label filters")
    ] + filter_dropdowns + [
    dcc.Checklist(
        id='options-checklist',
        options=[
            {'label': 'Include open issues', 'value': 'open'},
            {'label': 'Include closed issues', 'value': 'closed'},
            {'label': 'Show milestones', 'value': 'milestones'}
        ],
        value=['open', 'milestones']
    )  
])

inputs = [Input('category-dropdown', 'value'), Input('options-checklist', 'value'), Input('creator-dropdown', 'value')] + filter_inputs


def prepare_df(category_issues, options, filter_map):
    filtered = category_issues[['issue', 'time', 'closed']]
    for column, filters in filter_map.items():
        for f in filters:
            if len(f) > 0:
                filtered = filtered.merge(issues[issues[column].isin(f)][['issue', 'time', 'closed']])
    data = filtered.drop_duplicates().copy()
    if 'open' in options:
        data['inc'] = 1
        data['dec'] = 0 if 'closed' in options else -1
    else:
        data['inc'] = 0
        data['dec'] = 1 if 'closed' in options else 0
    closed = data[['closed', 'dec']][data['closed'] < "2222"].rename(columns={'closed':'time', 'dec':'inc'})
    return pd.concat([data[['time', 'inc']], closed])

def update_count(df):
    df.sort_values(['time', 'inc'], ascending=[True, False], inplace=True)
    df['count'] = df['inc'].cumsum()
    return df

def count_issues(category, other, options, filters):
    result = {}
    if ighig_config.use_types:
        current = prepare_df(issues[issues.type==category], options, filters)
    else:
        current = prepare_df(issues[issues.label==category], options, filters)
    for other_label, other_df in other.items():
        copy = current.copy()
        copy['inc'] = 0
        other_copy = other_df.copy()
        other_copy['inc'] = 0
        current = pd.concat([current, other_copy])
        copy['label'] = other_label
        result[other_label] = update_count(pd.concat([other_df, copy]))
    current['label'] = category
    result[category] = update_count(current)
    return result

@app.callback(Output('graph-with-selector', 'figure'), inputs)
def update_figure(categories, options, creator_filter, *label_filters):
    filters = {"creator": [creator_filter], "label": label_filters}
    if len(categories) == 0:
        data = update_count(prepare_df(issues, options, filters))
        fig = px.area(data, x="time", y="count")
    else:
        data_map = {}
        for category in categories:
            data_map = count_issues(category, data_map, options, filters)
        data = pd.concat(data_map.values()).sort_values('time')
#        print(data)
        if data.empty:
            return px.scatter(x=[0], y=[0])
        fig = px.area(data, x="time", y="count", color='label', color_discrete_map=label_colors)
    if 'milestones' in options:
        for milestone in milestones.values:
            if not pd.isnull(milestone[1]):
                fig.add_annotation(x=milestone[1], y=0, text=milestone[0])
        fig.update_layout(shapes=milestone_lines)
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run(debug=True)

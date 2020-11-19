#!/usr/bin/env python3

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import ghis_config

issues = pd.read_csv(ghis_config.issue_file, parse_dates=['time', 'closed'])
label_colors = pd.read_csv(ghis_config.label_file).set_index('label').to_dict()['color']
milestones = pd.read_csv(ghis_config.milestone_file, parse_dates=['due'])
milestone_lines = []
for milestone in milestones.values:
    if not pd.isnull(milestone[1]):
        milestone_lines.append(dict(
            type='line', yref='paper', y0=0, y1=1,
            xref='x', x0=milestone[1], x1=milestone[1]
        ))

app = dash.Dash(__name__, requests_pathname_prefix=ghis_config.requests_pathname_prefix)

app.layout = html.Div([
    dcc.Graph(id='graph-with-selector'),
    dcc.Dropdown(
        id='label-dropdown',
        options=[{'label': label, 'value': label} for label in ghis_config.stacked_labels],
        value=ghis_config.default_labels,
        multi=True
    ),
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


def prepare_df(filtered, options):
    data = filtered[['issue', 'time', 'closed']].drop_duplicates()
    if 'open' in options:
        data['inc'] = 1
        data['dec'] = 0 if 'closed' in options else -1
    else:
        data['inc'] = 0
        data['dec'] = 1 if 'closed' in options else 0
    closed = data[['closed', 'dec']][data['closed'] < pd.Timestamp.now()].rename(columns={'closed':'time', 'dec':'inc'})
    return pd.concat([data[['time', 'inc']], closed])

def update_count(df):
    df.sort_values('time', inplace=True)
    df['count'] = df['inc'].cumsum()
    return df

def count_issues(label, other, options):
    result = {}
    current = prepare_df(issues[issues['label']==label], options)
    for other_label, other_df in other.items():
        copy = current.copy()
        copy['inc'] = 0
        other_copy = other_df.copy()
        other_copy['inc'] = 0
        current = current.append(other_copy)
        copy['label'] = other_label
        result[other_label] = update_count(other_df.append(copy))
    current['label'] = label
    result[label] = update_count(current)
    return result

@app.callback(
    Output('graph-with-selector', 'figure'),
    [Input('label-dropdown', 'value'), Input('options-checklist', 'value')])
def update_figure(labels, options):
    if len(labels) == 0:
        data = update_count(prepare_df(issues, options))
        fig = px.area(data, x="time", y="count")
    else:
        data_map = {}
        for label in labels:
            data_map = count_issues(label, data_map, options)
        data = pd.concat(data_map.values()).sort_values('time')
#        print(data)
        fig = px.area(data, x="time", y="count", color='label', color_discrete_map=label_colors)
    if 'milestones' in options:
        for milestone in milestones.values:
            if not pd.isnull(milestone[1]):
                fig.add_annotation(x=milestone[1], y=0, text=milestone[0])
        fig.update_layout(shapes=milestone_lines)
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

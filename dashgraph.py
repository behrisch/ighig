#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

issues = pd.read_csv('issues.csv', parse_dates=['time', 'closed'])
label_colors = pd.read_csv('labels.csv').set_index('label').to_dict()['color']
milestones = pd.read_csv('milestones.csv', parse_dates=['due'])
milestone_lines = []
for milestone in milestones.values:
    if not pd.isnull(milestone[1]):
        milestone_lines.append(dict(
            type='line', yref='paper', y0=0, y1=1,
            xref='x', x0=milestone[1], x1=milestone[1]
        ))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='graph-with-selector'),
    dcc.Dropdown(
        id='label-dropdown',
        options=[
            {'label': 'bug', 'value': 'bug'},
            {'label': 'enhancement', 'value': 'enhancement'},
            {'label': 'question', 'value': 'question'}
        ],
        value=['bug'],
        multi=True
    )
])


def count_issues(label=None, earlier=None):
    if label:
        filtered = issues[issues['label']==label]
    else:
        filtered = issues
    data = filtered[['issue', 'time', 'closed']].drop_duplicates()
    data['inc'] = 1
    data['dec'] = -1
    closed = data[['closed', 'dec']][data['closed'] < pd.Timestamp.now()].rename(columns={'closed':'time', 'dec':'inc'})
    d = pd.concat([data[['time', 'inc']], closed]).sort_values('time')
    if earlier is not None:
        copy = earlier.copy()
        copy['inc'] = 0
        d = d.append(copy).sort_values('time')
    if label:
        d['label'] = label
    d['count'] = d['inc'].cumsum()
    d = d.append(earlier).sort_values('time')
    print(d)
    return d

@app.callback(
    Output('graph-with-selector', 'figure'),
    [Input('label-dropdown', 'value')])
def update_figure(labels):
    if len(labels) == 0:
        data = count_issues()
        fig = px.area(data, x="time", y="count")
    else:
        data = None
        for label in labels:
            data = count_issues(label, data)
        print(data)
        fig = px.area(data, x="time", y="count", color='label', color_discrete_map=label_colors)
    for milestone in milestones.values:
        if not pd.isnull(milestone[1]):
            fig.add_annotation(x=milestone[1], y=0, text=milestone[0])
    fig.update_layout(transition_duration=500, shapes=milestone_lines)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

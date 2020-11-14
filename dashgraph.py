#!/usr/bin/env python3

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd

df = pd.read_csv('out.csv', parse_dates=['time', 'closed'])

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


@app.callback(
    Output('graph-with-selector', 'figure'),
    [Input('label-dropdown', 'value')])
def update_figure(labels):
    if len(labels) == 0:
        labels = ["bug"]
    data = df[df['label']==labels[0]][['number', 'time', 'closed', 'label_color']].drop_duplicates()
    data['inc'] = 1
    data['dec'] = -1
    closed = data[['closed', 'dec', 'label_color']][data['closed'] < pd.Timestamp.now()].rename(columns={'closed':'time','dec':'inc'})
    d = pd.concat([data[['time', 'inc', 'label_color']], closed]).sort_values('time')
    d['sum'] = d['inc'].cumsum()
#    print(d)

    fig = px.area(d, x="time", y="sum", color="label_color")
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

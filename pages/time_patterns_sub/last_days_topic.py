import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, bar_graph
from datetime import date
from html_parser import category_mapping
import plotly.express as px


def last_days_layout():

    return html.Div([

        html.Br(),
        dcc.Slider(1, 30, 1, value=7, id='slider_last_days'),
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_last_days',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='last_days_graph'),
        dbc.Accordion(id='last_days_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("last_days_graph", "figure"),
    Output("last_days_table", "children"),
    Input('slider_last_days', "value"),
    Input('dropdown_last_days', 'value')
)
def update_graph(limit, chosen):
    df = query.last_days_trend(category_or_type=chosen, limit=limit)
    figure = bar_graph(df, chosen, x_axis='Date' , y_axis='Sub Count', hover=['Total Count', 'Day of Week'])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]
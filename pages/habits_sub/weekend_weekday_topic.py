import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px
import pandas as pd


def weekend_weekday_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='date_range_weekend_weekday',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        dcc.Graph(id='weekend_weekday_graph'),
        dbc.Accordion(id='weekend_weekday_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("weekend_weekday_graph", "figure"),
    Output("weekend_weekday_table", "children"),
    Input('date_range_weekend_weekday', 'start_date'),
    Input('date_range_weekend_weekday', 'end_date')
)
def update_graph(start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.weekday_vs_weekend(lower_range=start_date, upper_range=end_date)
    df = df.melt(id_vars="Video Type", var_name="Day type", value_name="Average")

    figure = px.bar(df, x="Video Type", y="Average", color="Day type", barmode="group")

    return figure, [dbc.AccordionItem(table(df), title="Show data")]
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
import plotly.express as px


def format_trend_layout():
    df = query.video_length_trend_over_month()

    figure = px.bar(df.melt(id_vars="Video Type", var_name="Month",
                    value_name="Videos"),
            x="Month", y="Videos", color="Video Type")

    return html.Div([
        html.Div([
            dcc.Graph(id='format_trend_graph', figure=figure),
            dbc.Accordion( [dbc.AccordionItem(table(df), title="Show data")], id='format_trend_table', start_collapsed=True, flush=True
            )
        ])
    ])
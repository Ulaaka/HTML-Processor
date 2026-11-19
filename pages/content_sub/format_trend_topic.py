import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import bar_graph, table
from datetime import date
import plotly.express as px
from html_parser import category_mapping

def format_trend_layout():
    return html.Div([
        html.P("Category:"),
        dcc.Dropdown(id='dropdown_format_trend',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
            ),
        dcc.Graph(id='format_trend_graph'),
        dbc.Accordion(id='format_trend_table', start_collapsed=True, flush=True)
    ])


@callback(
    Output("format_trend_graph", "figure"),
    Output("format_trend_table", "children"),
    Input('dropdown_format_trend', 'value')
)

def update_graph(video_category):

    if video_category == 'All':
        video_category = None

    df = query.video_length_trend_over_month(video_category=video_category)
    df = df.melt(id_vars="Video Type", var_name="Month", value_name="Videos")

    figure = bar_graph(df, "Video Type", x_axis='Month' , y_axis='Videos', hover="Videos")

    return figure, [dbc.AccordionItem(table(df), title="Show data")]

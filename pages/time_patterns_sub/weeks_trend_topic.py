import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px


def weeks_trend_layout():

    return html.Div([

        html.Br(),
        dcc.Slider(1, 52, 1, value=7, id='slider_weeks_trend'),
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_weeks_trend',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='weeks_trend_graph'),
        dbc.Accordion(id='weeks_trend_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("weeks_trend_graph", "figure"),
    Output("weeks_trend_table", "children"),
    Input('slider_weeks_trend', "value"),
    Input('dropdown_weeks_trend', 'value')
)
def update_graph(limit, chosen):
    df = query.weekly_trend_updated(category_or_type=chosen, limit=limit)

    figure = px.bar(
        df,
        x='Week',
        y='Sub Count',
        color=chosen,
        barmode='stack',
        hover_data=['Total Count'],
    )
    figure.update_xaxes(type='category')

    return figure, [dbc.AccordionItem(table(df), title="Show data")]
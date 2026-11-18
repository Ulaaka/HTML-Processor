import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px

def months_trend_layout():

    return html.Div([

        html.Br(),
        dcc.Slider(1, 12, 1, value=4, id='slider_months_trend'),
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_months_trend',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='months_trend_graph'),
        dbc.Accordion(id='months_trend_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("months_trend_graph", "figure"),
    Output("months_trend_table", "children"),
    Input('slider_months_trend', "value"),
    Input('dropdown_months_trend', 'value')
)
def update_graph(limit, chosen):
    df = query.monthly_trend_updated(category_or_type=chosen, limit=limit)

    figure = px.bar(
        df,
        x='Month',
        y='Sub Count',
        color=chosen,
        barmode='stack',
        hover_data=['Total Count'],
    )
    figure.update_xaxes(type='category')

    return figure, [dbc.AccordionItem(table(df), title="Show data")]
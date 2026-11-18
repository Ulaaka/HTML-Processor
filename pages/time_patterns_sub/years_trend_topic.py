import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px
def years_trend_layout():
    return html.Div([
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_yearly_trend_category',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='yearly_trend_graph'),
        dbc.Accordion(id='yearly_trend_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("yearly_trend_graph", "figure"),
    Output("yearly_trend_table", "children"),
    Input('dropdown_yearly_trend_category', "value")
)
def update_graph(chosen):
    df = query.yearly_trend_update(category_or_type=chosen)

    figure = px.bar(
        df,
        x='Year',
        y='Sub Count',
        color=chosen,
        barmode='stack',
        hover_data=['Total Count', "Year Start", "Year End"],
    )
    figure.update_xaxes(type='category')

    return figure, [dbc.AccordionItem(table(df), title="Show data")]
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px

def quarters_trend_layout():
    years = query.all_years()
    return html.Div([

        html.Br(),
        html.P("Year:"),
        dcc.Dropdown(id='dropdown_quarter_trend_year',
                options=years,
                value=max(years), clearable=False
            ),
        html.Br(),
        html.P("Show by:"),
        dcc.Dropdown(id='dropdown_quarter_trend_category',
                options=['Category', 'Video Type'],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id='quarter_trend_graph'),
        dbc.Accordion(id='quarter_trend_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("quarter_trend_graph", "figure"),
    Output("quarter_trend_table", "children"),
    Input('dropdown_quarter_trend_year', "value"),
    Input('dropdown_quarter_trend_category', 'value')
)
def update_graph(year, chosen):
    df = query.quarter_trend_updated(category_or_type=chosen, year=year)

    figure = px.bar(
        df,
        x='Year-Quarter',
        y='Sub Count',
        color=chosen,
        barmode='stack',
        hover_data=['Total Count', 'Start Date', 'End Date'],
    )
    figure.update_xaxes(type='category')

    return figure, [dbc.AccordionItem(table(df), title="Show data")]
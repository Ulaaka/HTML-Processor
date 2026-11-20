import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, bar_graph

def months_trend_layout():

    return html.Div([
        dbc.Card(" Watch Activity For Each Selected Month", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(1, 12, 1, value=4, id='slider_months_trend'),
        html.Br(),
        html.H6("Show by:", className="content"),
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

    figure = bar_graph(df, chosen, x_axis='Month' , y_axis='Sub Count', hover="Total Count")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]
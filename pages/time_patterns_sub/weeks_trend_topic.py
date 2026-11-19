import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, bar_graph

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

    figure = bar_graph(df, chosen, x_axis='Week' , y_axis='Sub Count', hover="Total Count")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]
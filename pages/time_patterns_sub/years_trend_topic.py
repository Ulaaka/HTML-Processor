import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, bar_graph

def years_trend_layout():
    return html.Div([
        dbc.Card(" Watch Activity For All Years", body=True, className="mt-2"),
        html.Br(),
        html.H6("Show By:", className="content"),
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
    figure = bar_graph(df, chosen, x_axis='Year' , y_axis='Sub Count', hover=['Total Count', "Year Start", "Year End"])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]
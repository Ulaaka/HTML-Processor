import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date

def interests_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_category_count',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Categories to show:"),
        dcc.Slider(5, 40, 5, value=20, id='slider_category_count'),
        html.Br(),
        html.Div([
            dcc.Graph(id='category_count_graph'),
            dbc.Accordion(id='category_count_table', start_collapsed=True, flush=True)
        ])
    ])

@callback(
    Output("category_count_graph", "figure"),
    Output("category_count_table", "children"),
    Input('slider_category_count', "value"),
    Input('data_range_category_count', 'start_date'),
    Input('data_range_category_count', 'end_date')
)

def update_table(value, start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.interest_analysis(limit=value, lower_range=start_date, upper_range=end_date)

    return hbar(df, x ='Total Count', y="Category").update_layout(height=420) , [dbc.AccordionItem(table(df), title="Show data")]

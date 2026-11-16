import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date

def format_mix_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_format_mix',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.Div([
            dcc.Graph(id='format_mix_graph'),
            dbc.Accordion(id='format_mix_table', start_collapsed=True, flush=True)
        ])
    ])

@callback(
    Output("format_mix_graph", "figure"),
    Output("format_mix_table", "children"),
    Input('data_range_format_mix', 'start_date'),
    Input('data_range_format_mix', 'end_date')
)

def update_table(start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.video_length_preference(lower_range=start_date, upper_range=end_date)

    return hbar(df, x ="Total Count", y="Type").update_layout(height=420) , [dbc.AccordionItem(table(df), title="Show data")]

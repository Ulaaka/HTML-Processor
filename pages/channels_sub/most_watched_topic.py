import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date

def most_watched_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_most_watched_channels',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Channels to Show:"),
        dcc.Slider(5, 40, 5, value=20, id='slider_most_watched_channels'),
        html.Br(),
        html.Div([
            dcc.Graph(id='most_watched_channels'),
            dbc.Accordion(id='most_watched_channels_table', start_collapsed=True, flush=True)
        ])
    ])

@callback(
    Output("most_watched_channels", "figure"),
    Output("most_watched_channels_table", "children"),
    Input('slider_most_watched_channels', "value"),
    Input('data_range_most_watched_channels', 'start_date'),
    Input('data_range_most_watched_channels', 'end_date')
)

def update_table(value, start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.the_most_watched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    return hbar(df, x ="Total Watch", y="Channel Name").update_layout(height=420) , [dbc.AccordionItem(table(df), title="Show data")]

import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table
from datetime import date
import plotly.express as px

def channel_month_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_channel_month',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.Div([
            dcc.Graph(id='channel_month_graph'),
            dbc.Accordion(id='channel_month_table', start_collapsed=True, flush=True)
        ])
    ])

@callback(
    Output("channel_month_graph", "figure"),
    Output("channel_month_table", "children"),
    Input('data_range_channel_month', 'start_date'),
    Input('data_range_channel_month', 'end_date')
)

def update_table(start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.most_watched_channel_per_month(lower_range=start_date, upper_range=end_date)

    return px.bar(df, x ='Year - Month', y='Total Watch', color="Channel Name", barmode="group").update_layout(height=420) , [dbc.AccordionItem(table(df), title="Show data")]

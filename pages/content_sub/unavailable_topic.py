import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, dash_table
from visual_functions import TABLE_STYLE, table
from datetime import date

def unavailable_layout():
    first_day = query.first_day()
    last_day = query.last_day()
    return html.Div([
        dcc.DatePickerRange(
            id='data_range_unavailable_content',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Search:"),
        dcc.Input(id="search_unavailable_content", type="text", placeholder="Search"),
        html.Br(),
        dash_table.DataTable(
            id="table_unavailable_content",
            **TABLE_STYLE
        )
    ])

@callback(
    Output("table_unavailable_content", "data"),
    Output("table_unavailable_content", "columns"),
    Input("search_unavailable_content", "value"),
    Input('data_range_unavailable_content', 'start_date'),
    Input('data_range_unavailable_content', 'end_date')
)
def update_table(search, start_date, end_date):

    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.unavailable_videos(lower_range=start_date, upper_range=end_date)

    data, cols = table(table_df=df, url="Channel URL", search=search, accordion=False)

    return data, cols
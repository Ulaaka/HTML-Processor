import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, dash_table
from visual_functions import hbar, table, TABLE_STYLE
from datetime import date
from html_parser import category_mapping
import plotly.express as px


def explorer_layout():

    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='data_range_time',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        dcc.Input(id="rows_to_show_time", value=20, type="number", min=1),
        html.Br(),
        html.P("Time:"),
        dcc.Dropdown(id='dropdown_time',
                options=["All", "Morning", "Afternoon", "Evening", "Night"],
                value='Morning', clearable=False
            ),
        html.Br(),
        html.P("Category:"),
        dcc.Dropdown(id='dropdown_time_category',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
        ),
        html.Br(),
        html.P("Video Type:"),
        dcc.Dropdown(id='dropdown_time_type',
                options=['All', 'Video', 'Reel', 'Unavailable'],
                value='All', clearable=False
        ),
        html.Br(),
        dcc.Input(id="search_explorer", type="text", placeholder="Search"),
        dash_table.DataTable(
            id="time_table",
            **TABLE_STYLE
        )
    ])

@callback(
    Output("time_table", "data"),
    Output("time_table", "columns"),
    Input('data_range_time', 'start_date'),
    Input('data_range_time', 'end_date'),
    Input('rows_to_show_time', "value"),
    Input('dropdown_time', 'value'),
    Input('dropdown_time_category', 'value'),
    Input('dropdown_time_type', 'value'),
    Input('search_explorer', 'value')

)
def update_graph(start_date, end_date, limit, time, video_category, video_type, search):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()
    time = None if time == 'All' else time.lower()

    df = query.date_type_time_func(limit=limit, video_type=video_type, video_category = video_category, time = time, lower_range=start_date, upper_range=end_date)

    url_list = ['Video URL', 'Channel URL']
    data, cols = table(table_df=df, url=url_list, accordion=False, search=search)

    return data, cols
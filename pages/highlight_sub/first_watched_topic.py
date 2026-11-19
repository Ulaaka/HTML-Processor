
from queries.query_connection import query
from dash import html, Input, Output, dash_table, dcc, callback
from visual_functions import TABLE_STYLE, table
from html_parser import category_mapping
import dash_bootstrap_components as dbc

def first_watched_layout():
    return html.Div([
        dbc.Card("Shows Firs Watched Content Based On Filters", body=True),
        html.Br(),
        html.H6("Rows to show:", className="content"),
        dcc.Input(id="rows_to_show_first", value=20, type="number", min=1),
        html.Br(),
        html.Br(),
        html.H6("Category:", className="content"),
        dcc.Dropdown(id='dropdown_first_watched_category',
                options=['All'] + list(category_mapping.values()),
                value='All', clearable=False
        ),
        html.Br(),
        html.H6("Video Type:", className="content"),
        dcc.Dropdown(id='dropdown_first_watched_type',
                options=['All', 'Video', 'Reel', 'Unavailable'],
                value='All', clearable=False
        ),
        html.Br(),
        dcc.Input(id="search_first", type="text", placeholder="Search"),
        html.Br(),
        dash_table.DataTable(
            id="table_first",
            **TABLE_STYLE
        )
    ])

@callback(
    Output("table_first", "data"),
    Output("table_first", "columns"),
    Input("rows_to_show_first", "value"),
    Input("search_first", "value"),
    Input("dropdown_first_watched_category", "value"),
    Input("dropdown_first_watched_type", "value")
)
def update_table(rows, search, video_category, video_type):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.first_last_videos_ever_watched(rows, video_category=video_category, video_type=video_type, first_or_last=True)

    data, cols = table(table_df=df, url='URL', accordion=False, search=search)
    return data, cols
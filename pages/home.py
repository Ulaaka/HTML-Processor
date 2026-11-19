import dash
from dash import html, dcc, dash_table, Input, Output, callback

from queries.query_connection import query
from visual_functions import TABLE_STYLE, table

dash.register_page(__name__, path="/", name="Home")

# Load once when the app starts
df = (
    query.table.copy()
    .rename(columns={
        "video_url": "Video URL",
        "video_name": "Video Name",
        "video_type": "Video Type",
        "video_category": "Video Category",
        "channel_url": "Channel URL",
        "channel_name": "Channel name",
        "time_stamp": "Timestamp",
    })
    .sort_values("Timestamp")
    .drop(columns="historyID")
)

layout = html.Div([
    html.H3("Your Watch history"),
    dcc.Input(
        id="search_home",
        type="text",
        placeholder="Search anything (videos, channel etc...)"
    ),
    html.Br(),
    html.Br(),
    dash_table.DataTable(id="table_home", **TABLE_STYLE),
])


@callback(
    Output("table_home", "data"),
    Output("table_home", "columns"),
    Input("search_home", "value"),
)
def update_home_table(search):
    url_list = ['Video URL', 'Channel URL']
    data, cols = table(table_df=df, url=url_list, accordion=False, search=search)
    return data, cols
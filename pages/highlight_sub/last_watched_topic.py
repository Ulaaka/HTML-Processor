import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, Input, Output, State, dash_table, dcc, callback
from visual_functions import TABLE_STYLE, table
from html_parser import category_mapping

def last_watched_layout():
    return html.Div([
        dbc.Card("Shows Last Watched Content Based On Filters", body=True),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Results to show:", className="content"),
                dcc.Input(id="rows_to_show_last", value=20, type="number", min=1)
            ], md=4),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_last_watched_category',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                )
            ], md=4),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(id='dropdown_last_watched_type',
                        options=['All', 'Video', 'Reel', 'Unavailable'],
                        value='All', clearable=False
                )
            ], md=4),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Input(id="search_last", type="text", placeholder="Search"), md=6),
            dbc.Col(html.Button("Download CSV", id="download_last_watched_btn"), md=2, className="ms-auto text-end"),
        ]),
        html.Br(),
        dash_table.DataTable(
            id="table_last",
            **TABLE_STYLE
        ),
        dcc.Download(id="download_last_watched"),
    ])

@callback(
    Output("table_last", "data"),
    Output("table_last", "columns"),
    Input("rows_to_show_last", "value"),
    Input("search_last", "value"),
    Input("dropdown_last_watched_category", "value"),
    Input("dropdown_last_watched_type", "value")
)
def update_table(rows, search, video_category, video_type):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.first_last_videos_ever_watched(rows, video_category=video_category, video_type=video_type, first_or_last=False)

    data, cols = table(table_df=df, url='URL', accordion=False, search=search)
    return data, cols

@callback(
    Output("download_last_watched", "data"),
    Input("download_last_watched_btn", "n_clicks"),
    State("rows_to_show_last", "value"),
    State("search_last", "value"),
    State("dropdown_last_watched_category", "value"),
    State("dropdown_last_watched_type", "value"),
    prevent_initial_call=True,
)
def download_last_watched_csv(_, rows, search, video_category, video_type):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.first_last_videos_ever_watched(rows, video_category=video_category, video_type=video_type, first_or_last=False)

    if search:
        df = df[df.astype(str).apply(lambda c: c.str.contains(search, case=False, regex=False)).any(axis=1)]

    return dcc.send_data_frame(df.to_csv, "last_watched.csv", index=False)
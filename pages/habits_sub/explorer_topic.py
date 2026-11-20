from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State, dash_table
from visual_functions import table, TABLE_STYLE
from datetime import date
from html_parser import category_mapping
import dash_bootstrap_components as dbc

def explorer_layout():

    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Explore Your Data", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_time',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Rows to show:", className="content"),
                dcc.Input(id="rows_to_show_time", value=20, type="number", min=1),
            ], md=4),
            dbc.Col([
                html.H6("Time:", className="content"),
                dcc.Dropdown(id='dropdown_time',
                        options=["All", "Morning", "Afternoon", "Evening", "Night"],
                        value='Morning', clearable=False
                    ),
            ], md=4),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_time_category',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                ),
            ], md=4),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(id='dropdown_time_type',
                        options=['All', 'Video', 'Reel', 'Unavailable'],
                        value='All', clearable=False
                ),
            ], md=4),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Input(id="search_explorer", type="text", placeholder="Search"), md=6),
            dbc.Col(html.Button("Download CSV", id="download_explorer_btn"), md=2, className="ms-auto text-end"),
        ]),
        html.Br(),
        dash_table.DataTable(
            id="time_table",
            **TABLE_STYLE
        ),
        dcc.Download(id="download_explorer"),
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

    df = query.date_type_time_func(limit=limit, video_type=video_type, video_category=video_category, time=time, lower_range=start_date, upper_range=end_date)

    url_list = ['Video URL', 'Channel URL']
    data, cols = table(table_df=df, url=url_list, accordion=False, search=search)

    return data, cols

@callback(
    Output("download_explorer", "data"),
    Input("download_explorer_btn", "n_clicks"),
    State('data_range_time', 'start_date'),
    State('data_range_time', 'end_date'),
    State('rows_to_show_time', "value"),
    State('dropdown_time', 'value'),
    State('dropdown_time_category', 'value'),
    State('dropdown_time_type', 'value'),
    State('search_explorer', 'value'),
    prevent_initial_call=True,
)
def download_explorer_csv(_, start_date, end_date, limit, time, video_category, video_type, search):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()
    time = None if time == 'All' else time.lower()

    df = query.date_type_time_func(limit=limit, video_type=video_type, video_category=video_category, time=time, lower_range=start_date, upper_range=end_date)

    if search:
        df = df[df.astype(str).apply(lambda c: c.str.contains(search, case=False, regex=False)).any(axis=1)]

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"explorer_{start_date}_to_{end_date}.csv", index=False)
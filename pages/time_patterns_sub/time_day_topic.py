import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, clock
from html_parser import category_mapping

def time_day_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card(" Watch Activity For Each Hour Given Selected Duration", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_time_day',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(
                    id='dropdown_time_day_category',
                    options=['All'] + list(category_mapping.values()),
                    value='All', clearable=False
                ),
            ], md=4),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(
                    id='dropdown_time_day_type',
                    options=['All', 'Video', 'Reel', 'Unavailable'],
                    value='All', clearable=False
                ),
            ], md=4),
        ]),
        html.Br(),

        dcc.Graph(id='time_day_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_time_day_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='time_day_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_time_day"),
    ])

@callback(
    Output("time_day_graph", "figure"),
    Output("time_day_table", "children"),
    Input('dropdown_time_day_category', "value"),
    Input('dropdown_time_day_type', "value"),
    Input('data_range_time_day', "start_date"),
    Input('data_range_time_day', "end_date")
)
def update_graph(video_category, video_type, start_date, end_date):

    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()

    df = query.time_of_the_day(lower_range=start_date, upper_range=end_date, video_type=video_type, video_category=video_category)

    return clock(df), [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_time_day", "data"),
    Input("download_time_day_btn", "n_clicks"),
    State('dropdown_time_day_category', "value"),
    State('dropdown_time_day_type', "value"),
    State('data_range_time_day', "start_date"),
    State('data_range_time_day', "end_date"),
    prevent_initial_call=True,
)
def download_time_day_csv(_, video_category, video_type, start_date, end_date):
    video_category = None if video_category == 'All' else video_category
    video_type = None if video_type == 'All' else video_type.lower()

    df = query.time_of_the_day(lower_range=start_date, upper_range=end_date, video_type=video_type, video_category=video_category)

    if start_date is None:
        start_date = query.first_day()
    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"time_of_day_{start_date}_to_{end_date}.csv", index=False)
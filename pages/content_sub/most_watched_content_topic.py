import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping

def most_watched_content_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Most Watched Content During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 40, 5, value=20, id='slider_most_watched_content'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_most_watched_content',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_most_watched_content_category',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                ),
            ], md=4),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(id='dropdown_most_watched_content_type',
                        options=['All', 'Video', 'Reel', 'Unavailable'],
                        value='All', clearable=False
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='most_watched_content_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_most_watched_content_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='most_watched_content_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_most_watched_content"),
    ])

@callback(
    Output("most_watched_content_graph", "figure"),
    Output("most_watched_content_table", "children"),
    Input('slider_most_watched_content', "value"),
    Input('data_range_most_watched_content', 'start_date'),
    Input('data_range_most_watched_content', 'end_date'),
    Input('dropdown_most_watched_content_category', 'value'),
    Input('dropdown_most_watched_content_type', 'value')
)
def update_table(value, start_date, end_date, video_category, video_type):

    if video_category == "All":
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_most_watched_videos(limit=value, video_type=video_type, video_category=video_category, lower_range=start_date, upper_range=end_date)

    return hbar(df, x='Total Watch', y="Name").update_layout(height=420), [dbc.AccordionItem(table(df, url="URL"), title="Show data")]

@callback(
    Output("download_most_watched_content", "data"),
    Input("download_most_watched_content_btn", "n_clicks"),
    State('slider_most_watched_content', "value"),
    State('data_range_most_watched_content', 'start_date'),
    State('data_range_most_watched_content', 'end_date'),
    State('dropdown_most_watched_content_category', 'value'),
    State('dropdown_most_watched_content_type', 'value'),
    prevent_initial_call=True,
)
def download_most_watched_content_csv(_, value, start_date, end_date, video_category, video_type):
    if video_category == "All":
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_most_watched_videos(limit=value, video_type=video_type, video_category=video_category, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"most_watched_content_{start_date}_to_{end_date}.csv", index=False)
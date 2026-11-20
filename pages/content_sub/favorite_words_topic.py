import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import hbar, table
from html_parser import category_mapping

def favorite_words_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Favorite Words During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 40, 5, value=20, id='slider_most_repeated_words'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_most_repeated_words',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_favorite_words_category',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                ),
            ], md=4),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(id='dropdown_favorite_words_type',
                        options=['All', 'Video', 'Reel', 'Unavailable'],
                        value='All', clearable=False
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='most_repeated_words_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_favorite_words_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='most_repeated_words_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_favorite_words"),
    ])

@callback(
    Output("most_repeated_words_graph", "figure"),
    Output("most_repeated_words_table", "children"),
    Input('slider_most_repeated_words', "value"),
    Input('data_range_most_repeated_words', 'start_date'),
    Input('data_range_most_repeated_words', 'end_date'),
    Input('dropdown_favorite_words_category', 'value'),
    Input('dropdown_favorite_words_type', 'value')
)
def update_table(value, start_date, end_date, video_category, video_type):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_most_repeated_words(limit=value, video_type=video_type, video_category=video_category, lower_range=start_date, upper_range=end_date)

    return hbar(df, x='Total Count', y="Word").update_layout(height=420), [dbc.AccordionItem(table(df), title="Show data")]

@callback(
    Output("download_favorite_words", "data"),
    Input("download_favorite_words_btn", "n_clicks"),
    State('slider_most_repeated_words', "value"),
    State('data_range_most_repeated_words', 'start_date'),
    State('data_range_most_repeated_words', 'end_date'),
    State('dropdown_favorite_words_category', 'value'),
    State('dropdown_favorite_words_type', 'value'),
    prevent_initial_call=True,
)
def download_favorite_words_csv(_, value, start_date, end_date, video_category, video_type):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_most_repeated_words(limit=value, video_type=video_type, video_category=video_category, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"favorite_words_{start_date}_to_{end_date}.csv", index=False)
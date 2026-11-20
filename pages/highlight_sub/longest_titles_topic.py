from queries.query_connection import query
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, dcc, callback
from visual_functions import table, hbar
from html_parser import category_mapping

def longest_titles_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Shows Longest Titles Based On Filters", body=True),
        html.Br(),
        dcc.Slider(5, 40, 5, value=20, id='rows_to_show_longest'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_longest',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_longest_category',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                ),
            ], md=4),
            dbc.Col([
                html.H6("Video Type:", className="content"),
                dcc.Dropdown(id='dropdown_longest_type',
                        options=['All', 'Video', 'Reel', 'Unavailable'],
                        value='All', clearable=False
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='longest_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Input(id="search_longest", type="text", placeholder="Search"), md=6),
            dbc.Col(html.Button("Download CSV", id="download_longest_btn"), md=2, className="ms-auto text-end"),
        ]),
        html.Br(),
        dbc.Accordion(id='table_longest', start_collapsed=True, flush=True),
        dcc.Download(id="download_longest"),
    ])

@callback(
    Output('longest_graph', 'figure'),
    Output("table_longest", "children"),
    Input("rows_to_show_longest", "value"),
    Input('data_range_longest', 'start_date'),
    Input('data_range_longest', 'end_date'),
    Input('dropdown_longest_category', 'value'),
    Input('dropdown_longest_type', 'value'),
    Input('search_longest', 'value')
)
def update_table(rows, start_date, end_date, video_category, video_type, search):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_longest_titled_video(video_limit=rows, video_category=video_category, video_type=video_type, lower_range=start_date, upper_range=end_date)

    return hbar(df, x ='Title Length', y="Name").update_layout(height=420), [dbc.AccordionItem(table(table_df=df, url='URL', search=search), title="Show Table")]

@callback(
    Output("download_longest", "data"),
    Input("download_longest_btn", "n_clicks"),
    State("rows_to_show_longest", "value"),
    State('data_range_longest', 'start_date'),
    State('data_range_longest', 'end_date'),
    State('dropdown_longest_category', 'value'),
    State('dropdown_longest_type', 'value'),
    State('search_longest', 'value'),
    prevent_initial_call=True,
)
def download_longest_csv(_, rows, start_date, end_date, video_category, video_type, search):
    if video_category == 'All':
        video_category = None

    if video_type == 'All':
        video_type = None
    else:
        video_type = video_type.lower()

    df = query.the_longest_titled_video(video_limit=rows, video_category=video_category, video_type=video_type, lower_range=start_date, upper_range=end_date)

    if search:
        df = df[df.astype(str).apply(lambda c: c.str.contains(search, case=False, regex=False)).any(axis=1)]

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"longest_titles_{start_date}_to_{end_date}.csv", index=False)
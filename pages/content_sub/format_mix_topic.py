import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, pie_graph
from html_parser import category_mapping

def format_mix_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Composition of Video Formats During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_format_mix',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
            dbc.Col([
                html.H6("Category:", className="content"),
                dcc.Dropdown(id='dropdown_format_fix',
                        options=['All'] + list(category_mapping.values()),
                        value='All', clearable=False
                    ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='format_mix_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_format_mix_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='format_mix_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_format_mix"),
    ])

@callback(
    Output("format_mix_graph", "figure"),
    Output("format_mix_table", "children"),
    Input('data_range_format_mix', 'start_date'),
    Input('data_range_format_mix', 'end_date'),
    Input('dropdown_format_fix', 'value')
)
def update_table(start_date, end_date, category):
    if category == 'All':
        category = None

    df = query.video_length_preference(video_category=category, lower_range=start_date, upper_range=end_date)

    figure = pie_graph(graph_df=df, value_col=df['Total Count'], name_col=df['Type'])

    return figure, [dbc.AccordionItem(table(df), title="Show data")]

@callback(
    Output("download_format_mix", "data"),
    Input("download_format_mix_btn", "n_clicks"),
    State('data_range_format_mix', 'start_date'),
    State('data_range_format_mix', 'end_date'),
    State('dropdown_format_fix', 'value'),
    prevent_initial_call=True,
)
def download_format_mix_csv(_, start_date, end_date, category):
    if category == 'All':
        category = None

    df = query.video_length_preference(video_category=category, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"format_mix_{start_date}_to_{end_date}.csv", index=False)
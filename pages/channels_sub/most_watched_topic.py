import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import hbar, table

def most_watched_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Most Watched Channels During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 40, 5, value=20, id='slider_most_watched_channels'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_most_watched_channels',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='most_watched_channels'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_most_watched_channels_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='most_watched_channels_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_most_watched_channels"),
    ])

@callback(
    Output("most_watched_channels", "figure"),
    Output("most_watched_channels_table", "children"),
    Input('slider_most_watched_channels', "value"),
    Input('data_range_most_watched_channels', 'start_date'),
    Input('data_range_most_watched_channels', 'end_date')
)
def update_table(value, start_date, end_date):
    df = query.the_most_watched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    return hbar(df, x="Total Watch", y="Channel Name").update_layout(height=420), [dbc.AccordionItem(table(table_df=df, url="URL"), title="Show data")]

@callback(
    Output("download_most_watched_channels", "data"),
    Input("download_most_watched_channels_btn", "n_clicks"),
    State('slider_most_watched_channels', "value"),
    State('data_range_most_watched_channels', 'start_date'),
    State('data_range_most_watched_channels', 'end_date'),
    prevent_initial_call=True,
)
def download_most_watched_channels_csv(_, value, start_date, end_date):
    df = query.the_most_watched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"most_watched_channels_{start_date}_to_{end_date}.csv", index=False)
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, generic_bar

def channel_month_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Most Watched Channels For Each Month", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_channel_month',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='channel_month_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_channel_month_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='channel_month_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_channel_month"),
    ])

@callback(
    Output("channel_month_graph", "figure"),
    Output("channel_month_table", "children"),
    Input('data_range_channel_month', 'start_date'),
    Input('data_range_channel_month', 'end_date')
)
def update_table(start_date, end_date):
    df = query.most_watched_channel_per_month(lower_range=start_date, upper_range=end_date)

    figure = generic_bar(graph_df=df, x_axis='Year - Month', y_axis='Total Watch', chosen="Channel Name")
    return figure, [dbc.AccordionItem(table(df), title="Show data")]

@callback(
    Output("download_channel_month", "data"),
    Input("download_channel_month_btn", "n_clicks"),
    State('data_range_channel_month', 'start_date'),
    State('data_range_channel_month', 'end_date'),
    prevent_initial_call=True,
)
def download_channel_month_csv(_, start_date, end_date):
    df = query.most_watched_channel_per_month(lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"channel_month_{start_date}_to_{end_date}.csv", index=False)
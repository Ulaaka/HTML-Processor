from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State, dash_table
from visual_functions import TABLE_STYLE, table
import dash_bootstrap_components as dbc

def unavailable_layout():
    first_day = query.first_day()
    last_day = query.last_day()
    return html.Div([
        dbc.Card("Unavailable Videos During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='data_range_unavailable_content',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Input(id="search_unavailable_content", type="text", placeholder="Search"), md=6),
            dbc.Col(html.Button("Download CSV", id="download_unavailable_btn"), md=2, className="ms-auto text-end"),
        ]),
        html.Br(),
        dash_table.DataTable(
            id="table_unavailable_content",
            **TABLE_STYLE
        ),
        dcc.Download(id="download_unavailable"),
    ])

@callback(
    Output("table_unavailable_content", "data"),
    Output("table_unavailable_content", "columns"),
    Input("search_unavailable_content", "value"),
    Input('data_range_unavailable_content', 'start_date'),
    Input('data_range_unavailable_content', 'end_date')
)
def update_table(search, start_date, end_date):
    df = query.unavailable_videos(lower_range=start_date, upper_range=end_date)

    data, cols = table(table_df=df, url="Channel URL", search=search, accordion=False)

    return data, cols

@callback(
    Output("download_unavailable", "data"),
    Input("download_unavailable_btn", "n_clicks"),
    State("search_unavailable_content", "value"),
    State('data_range_unavailable_content', 'start_date'),
    State('data_range_unavailable_content', 'end_date'),
    prevent_initial_call=True,
)
def download_unavailable_csv(_, search, start_date, end_date):
    df = query.unavailable_videos(lower_range=start_date, upper_range=end_date)

    if search:
        df = df[df.astype(str).apply(lambda c: c.str.contains(search, case=False, regex=False)).any(axis=1)]

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"unavailable_videos_{start_date}_to_{end_date}.csv", index=False)
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, streaks_graph
from datetime import date
import pandas as pd

def streaks_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Longest Streaks During Selected Period", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(5, 20, 1, value=10, id='slider_streak'),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Date Range:"),
                dcc.DatePickerRange(
                    id='date_range_streak',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=first_day,
                    end_date=last_day
                ),
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='streak_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_streak_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='streak_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_streak"),
    ])

@callback(
    Output("streak_graph", "figure"),
    Output("streak_table", "children"),
    Input('slider_streak', "value"),
    Input('date_range_streak', 'start_date'),
    Input('date_range_streak', 'end_date')
)
def update_graph(limit, start_date, end_date):
    df = query.streak_analysis(limit=limit, lower_range=start_date, upper_range=end_date)

    df = df.assign(Start = pd.to_datetime(df["Start"]), End = pd.to_datetime(df["End"]) + pd.Timedelta(days=1), Streak = [f"{n} days" for n in df["Total Days"]])

    figure = streaks_graph(graph_df=df, x_start="Start", x_end="End", y_axis="Streak", chosen="Total Days")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_streak", "data"),
    Input("download_streak_btn", "n_clicks"),
    State('slider_streak', "value"),
    State('date_range_streak', 'start_date'),
    State('date_range_streak', 'end_date'),
    prevent_initial_call=True,
)
def download_streak_csv(_, limit, start_date, end_date):

    df = query.streak_analysis(limit=limit, lower_range=start_date, upper_range=end_date)

    if start_date is None:
        start_date = query.first_day()

    if end_date is None:
        end_date = query.last_day()

    return dcc.send_data_frame(df.to_csv, f"streaks_{start_date}_to_{end_date}.csv", index=False)
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import hbar, table
from datetime import date
from html_parser import category_mapping
import plotly.express as px
import pandas as pd

def streaks_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='date_range_streak',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        dcc.Slider(5, 20, 1, value=10, id='slider_streak'),
        html.Br(),
        dcc.Graph(id='streak_graph'),
        dbc.Accordion(id='streak_table', start_collapsed=True, flush=True)
    ])

@callback(
    Output("streak_graph", "figure"),
    Output("streak_table", "children"),
    Input('slider_streak', "value"),
    Input('date_range_streak', 'start_date'),
    Input('date_range_streak', 'end_date')
)
def update_graph(limit, start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

    df = query.streak_analysis(limit=limit, lower_range=start_date, upper_range=end_date)


    df = df.assign(Start = pd.to_datetime(df["Start"]), End = pd.to_datetime(df["End"]) + pd.Timedelta(days=1), Streak = [f"{n} days" for n in df["Total Days"]])

    figure = px.timeline(df, x_start="Start", x_end="End", y="Streak", color="Total Days", color_continuous_scale="Blues")\
                    .update_yaxes(autorange="reversed", title=None)

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]
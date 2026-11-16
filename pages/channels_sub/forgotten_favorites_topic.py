import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table
from datetime import date
import plotly.express as px

def forgotten_favorites_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dcc.DatePickerRange(
            id='date_range_forgotten',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
        html.H6("Channels to Show:"),
        dcc.Slider(5, 150, 1, value=20, id='slider_forgotten'),
        html.Br(),
        html.Div([
            dcc.Graph(id='forgotten_channels'),
            dbc.Accordion(id='forgotten_channels_table', start_collapsed=True, flush=True)
        ])
    ])

@callback(
    Output("forgotten_channels", "figure"),
    Output("forgotten_channels_table", "children"),
    Input('slider_forgotten', "value"),
    Input('date_range_forgotten', 'start_date'),
    Input('date_range_forgotten', 'end_date')
)

def update_table(value, start_date, end_date):
    if start_date:
        start_date = date.fromisoformat(start_date).strftime('%Y-%m-%d')

    if end_date:
        end_date = date.fromisoformat(end_date).strftime('%Y-%m-%d')

#{'channel_name': 'Channel Name', 'channel_url' : 'URL', 'total_count' : 'Total Watch', 'days_since_last' : 'Since Last Watched', 'neglect_score' : 'Neglect Score'}

    df = query.the_longest_untouched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    figure = px.scatter(df, x="Since Last Watched", y="Total Watch", size="Neglect Score", hover_name="Channel Name", size_max=40)
    return figure , [dbc.AccordionItem(table(df), title="Show data")]

import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input
from visual_functions import table, scatter_graph
from datetime import date

def forgotten_favorites_layout():
    first_day = query.first_day()
    last_day = query.last_day()

    return html.Div([
        dbc.Card("Channels You Used Watch a Lot Before (based on neglect score)", body=True, className="mt-2"),
        html.Br(),
        dcc.DatePickerRange(
            id='date_range_forgotten',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=first_day,
            end_date=last_day
        ),
        html.Br(),
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

    df = query.the_longest_untouched_channel(limit=value, lower_range=start_date, upper_range=end_date)

    figure = scatter_graph(graph_df=df, x_axis="Since Last Watched", y_axis="Total Watch", size_value="Neglect Score", hover_value="Channel Name")
    return figure , [dbc.AccordionItem(table(table_df=df, url="URL"), title="Show data")]
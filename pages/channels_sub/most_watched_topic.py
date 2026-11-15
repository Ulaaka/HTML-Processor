import dash_bootstrap_components as dbc
from query_connection import query
from dash import html, dcc
from visual_functions import graph, hbar
def most_watched_layout():
    df = query.the_most_watched_channel()

    return html.Div([
        html.H6("Most Watched Channels:"),
        html.Br(),
        graph(hbar(df, "Total Watch", "Channel Name"), df)
    ])

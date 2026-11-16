import dash_bootstrap_components as dbc
from dash import html

def months_trend_layout():
    return dbc.Card("Videos per month, with the change versus the previous month", body=True, className="mt-2")
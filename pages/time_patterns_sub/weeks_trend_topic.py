import dash_bootstrap_components as dbc
from dash import html

def weeks_trend_layout():
    return dbc.Card("Videos per week over the last few weeks", body=True, className="mt-2")
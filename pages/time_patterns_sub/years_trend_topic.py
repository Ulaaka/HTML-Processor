import dash_bootstrap_components as dbc
from dash import html

def years_trend_layout():
    return dbc.Card("Videos per year, with the change versus the previous year", body=True, className="mt-2")
import dash_bootstrap_components as dbc
from dash import html

def busiest_weeks_layout():
    return dbc.Card("Your Busiest Weeks.", body=True, className="mt-2")
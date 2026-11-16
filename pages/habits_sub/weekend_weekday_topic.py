import dash_bootstrap_components as dbc
from dash import html

def weekend_weekday_layout():
    return  dbc.Card("Average videos per weekday compared to per weekend day", body=True, className="mt-2")
import dash_bootstrap_components as dbc
from dash import html


def favorite_words_layout():
    return dbc.Card("Favorite Words", body=True, className="mt-2")
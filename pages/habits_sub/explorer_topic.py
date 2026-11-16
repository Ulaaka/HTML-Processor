import dash_bootstrap_components as dbc


def explorer_layout():
    return dbc.Card("Filter your history by format, time of day and category", body=True, className="mt-2")
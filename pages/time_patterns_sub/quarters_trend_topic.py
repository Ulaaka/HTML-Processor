import dash_bootstrap_components as dbc

def quarters_trend_layout():
    return dbc.Card("Videos per quarter, with the change versus the previous quarter", body=True, className="mt-2")
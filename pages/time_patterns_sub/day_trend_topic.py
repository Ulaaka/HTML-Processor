import dash_bootstrap_components as dbc


def day_trend_layout():
    return dbc.Card("Hour-by-hour activity for one day. Leave the date empty for your latest day", body=True, className="mt-2")
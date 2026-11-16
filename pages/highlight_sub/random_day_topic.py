import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dash_table
from visual_functions import TABLE_STYLE


def random_day_layout():
    df = query.random_day_discovery()


    cols = [{"name": str(c), "id": str(c), **({"presentation": "markdown"} if c == "URL" else {})} for c in df.columns]

    df["URL"] = df["URL"].map(lambda u: f"[open]({u})")

    return html.Div([
        dbc.Card("Shows Random Day Activity", body=True, className="mt-2"),
        html.Br(),
        dash_table.DataTable(
            id="table_random",
            data=df.to_dict("records"),
            columns=cols,
            **TABLE_STYLE
        )
    ])



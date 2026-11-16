
from queries.query_connection import query
from dash import html, Input, Output, dash_table, dcc, callback
from visual_functions import TABLE_STYLE


def longest_titles_layout():
    return html.Div([
        html.H6("Rows to show:"),
        dcc.Input(id="rows_to_show_longest", value=20, type="number", min=1),
        html.H6("Search:"),
        dcc.Input(id="search_longest", type="text", placeholder="Search"),
        html.Br(),
        dash_table.DataTable(
            id="table_longest",
            **TABLE_STYLE
        )
    ])

@callback(
    Output("table_longest", "data"),
    Output("table_longest", "columns"),
    Input("rows_to_show_longest", "value"),
    Input("search_longest", "value")
)
def update_table(rows, search):
    df = query.the_longest_titled_video(video_limit=rows)

    if search:
        df = df[df.astype(str).apply(lambda row: row.str.contains(search, case=False)).any(axis=1)]

    cols = [
        {"name": str(c), "id": str(c),
         **({"presentation": "markdown"} if c == "URL" else {})}
        for c in df.columns
    ]

    df["URL"] = df["URL"].apply(lambda u: f"[open]({u})")

    return df.to_dict("records"), cols
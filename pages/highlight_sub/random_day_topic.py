import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dash_table, dcc, Output, Input, callback, State
from visual_functions import TABLE_STYLE
import plotly.express as px

def random_day_layout():
    random_date  = query.random_date()
    return html.Div([
        dbc.Card("Shows Random Day Activity", body=True, className="mt-2"),
        html.Br(),
        dcc.Store(id="day_random", data=random_date),
        html.Br(),
        dcc.Dropdown(id='dropdown_random_day',
                options=["Category", "Type"],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id = "graph_random"),
        html.Br(),
        dcc.Input(id="search_random_day", type="text", placeholder="Search"),
        dash_table.DataTable(id="table_random", **TABLE_STYLE)
    ])

@callback(
    Output("table_random", "data"),
    Output("table_random", "columns"),
    Output("graph_random", "figure"),
    Input("dropdown_random_day", "value"),
    Input("search_random_day", "value"),
    State("day_random", "data")

)
def update(category_or_type, search, day):

    table_df, graph_df = query.random_day_discovery(category_or_type, day)

    figure = px.line(
        graph_df,
        markers=True,
        title=f"Activity counts by hour on {day}",
        labels={"Hour": "Hour", "value": "Count", "variable": category_or_type},
    ).update_layout(
        xaxis=dict(tickmode="linear", dtick=1),
        template="plotly_white",
        legend_title_text=category_or_type,
    )

    if search:
        table_df = table_df[table_df.astype(str).apply(lambda row: row.str.contains(search, case=False)).any(axis=1)]

    cols = [
        {"name": str(c), "id": str(c),
         **({"presentation": "markdown"} if c == "URL" else {})}
        for c in table_df.columns
    ]

    table_df["URL"] = table_df["URL"].apply(lambda u: f"[open]({u})")

    return table_df.to_dict("records"), cols, figure
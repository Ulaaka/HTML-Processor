import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, dash_table
from visual_functions import hbar, table, TABLE_STYLE
from datetime import date
from html_parser import category_mapping
import plotly.express as px

def day_trend_layout():
    first_day = query.first_day()
    last_day = query.last_day()
    return html.Div([
        dbc.Card("Day Activity", body=True, className="mt-2"),
        html.Br(),
        dcc.DatePickerSingle(
            id='date_day_trend',
            min_date_allowed=first_day,
            max_date_allowed=last_day,
            initial_visible_month=last_day,
            date=last_day
        ),
        html.Br(),
        dcc.Dropdown(id='dropdown_day_trend',
                options=["Category", "Type"],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id = "graph_day_trend"),
        html.Br(),
        dcc.Input(id="search_day_trend", type="text", placeholder="Search"),
        dash_table.DataTable(id="table_day_trend", **TABLE_STYLE)
    ])

@callback(
    Output("table_day_trend", "data"),
    Output("table_day_trend", "columns"),
    Output("graph_day_trend", "figure"),
    Input("date_day_trend", "date"),
    Input("dropdown_day_trend", "value"),
    Input("search_day_trend", "value")
)
def update(day, category_or_type, search):

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
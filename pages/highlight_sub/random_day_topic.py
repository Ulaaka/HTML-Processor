import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dash_table, dcc, Output, Input, callback, State
from visual_functions import TABLE_STYLE, table
import plotly.express as px

def random_day_layout():
    random_date  = query.random_date()
    return html.Div([
        dbc.Card("Shows Random Day Activity", body=True),
        dcc.Store(id="day_random", data=random_date),
        html.Br(),
        html.H6("Filter By:", className="content"),
        dcc.Dropdown(id='dropdown_random_day',
                options=["Category", "Type"],
                value='Category', clearable=False
            ),
        html.Br(),
        dcc.Graph(id = "graph_random"),
        html.Br(),
        dcc.Input(id="search_random_day", type="text", placeholder="Search"),
        dbc.Accordion(id='table_random', start_collapsed=True, flush=True)
    ])

@callback(
    Output("graph_random", "figure"),
    Output("table_random", "children"),
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

    return figure, [dbc.AccordionItem(table(table_df=table_df, url='URL', search=search), title="Show Table")]
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, Output, Input, callback, State
from visual_functions import table, line_graph

def random_day_layout():
    random_date  = query.random_date()
    return html.Div([
        dbc.Card("Shows Random Day Watch Activity", body=True),
        dcc.Store(id="day_random", data=random_date),
        html.Br(),
        dbc.Row([
            dbc.Col(
                [
                html.H6("Filter By:", className="content"),
                dcc.Dropdown(id='dropdown_random_day',
                        options=["Category", "Type"],
                        value='Category', clearable=False
                    )
                ],
                md=4
            ),
        ]),
        html.Br(),
        dcc.Graph(id = "graph_random"),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Input(id="search_random_day", type="text", placeholder="Search"), md=6),
            dbc.Col(html.Button("Download CSV", id="download_random_day_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='table_random', start_collapsed=True, flush=True),
        dcc.Download(id="download_random_day"),
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
    figure = line_graph(graph_df=graph_df, chosen=category_or_type, title=f"Activity counts by hour on {day}")

    return figure, [dbc.AccordionItem(table(table_df=table_df, url='URL', search=search), title="Show Table")]

@callback(
    Output("download_random_day", "data"),
    Input("download_random_day_btn", "n_clicks"),
    State("dropdown_random_day", "value"),
    State("search_random_day", "value"),
    State("day_random", "data"),
    prevent_initial_call=True,
)
def download_random_day_csv(_, category_or_type, search, day):
    table_df, _ = query.random_day_discovery(category_or_type, day)

    if search:
        table_df = table_df[table_df.astype(str).apply(lambda c: c.str.contains(search, case=False, regex=False)).any(axis=1)]

    return dcc.send_data_frame(table_df.to_csv, f"random_day_{day}.csv", index=False)
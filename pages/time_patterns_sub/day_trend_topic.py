import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, line_graph


def day_trend_layout():
    first_day = query.first_day()
    last_day = query.last_day()
    return html.Div([
        dbc.Card(" Watch Activity For Selected Day By Hour", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Day:"),
                dcc.DatePickerSingle(
                    id='date_day_trend',
                    min_date_allowed=first_day,
                    max_date_allowed=last_day,
                    initial_visible_month=last_day,
                    date=last_day
                )
            ], md=4),
            dbc.Col([
                html.H6("Filter By:", className="content"),
                dcc.Dropdown(
                    id='dropdown_day_trend',
                    options=["Category", "Type"],
                    value='Category', clearable=False
                )
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id="graph_day_trend"),
        html.Br(),
        dbc.Row([
            dbc.Col(dcc.Input(id="search_day_trend", type="text", placeholder="Search"), md=6),
            dbc.Col(html.Button("Download CSV", id="download_day_trend_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='table_day_trend', start_collapsed=True, flush=True),
        dcc.Download(id="download_day_trend"),
    ])

@callback(
    Output("graph_day_trend", "figure"),
    Output("table_day_trend", "children"),
    Input("date_day_trend", "date"),
    Input("dropdown_day_trend", "value"),
    Input("search_day_trend", "value")
)
def update(day, category_or_type, search):

    table_df, graph_df = query.random_day_discovery(category_or_type, day)

    figure = line_graph(graph_df=graph_df, chosen=category_or_type, title=f"Activity counts by hour on {day}")

    return figure,  [dbc.AccordionItem(table(table_df, url="URL", search=search), title="Show Table")]

@callback(
    Output("download_day_trend", "data"),
    Input("download_day_trend_btn", "n_clicks"),
    State("date_day_trend", "date"),
    State("dropdown_day_trend", "value"),
    State("search_day_trend", "value"),
    prevent_initial_call=True,
)
def download_day_trend_csv(_, day, category_or_type, search):
  table_df, _ = query.random_day_discovery(category_or_type, day)

  if search:
    table_df = table_df[table_df.astype(str).apply(lambda c: c.str.contains(search, case=False, regex=False)).any(axis=1)]

  return dcc.send_data_frame(table_df.to_csv, f"day_trend_{day}.csv", index=False)
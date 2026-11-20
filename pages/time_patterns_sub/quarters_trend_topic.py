import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, bar_graph

def quarters_trend_layout():
    years = query.all_years()
    return html.Div([
        dbc.Card(" Watch Activity For Selected Year By Quarters", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col([
                html.H6("Year:", className="content"),
                dcc.Dropdown(id='dropdown_quarter_trend_year',
                        options=years,
                        value=max(years), clearable=False
                    )
            ], md=4),
            dbc.Col([
                html.H6("Show By:", className="content"),
                dcc.Dropdown(id='dropdown_quarter_trend_category',
                        options=['Category', 'Video Type'],
                        value='Category', clearable=False
                )
            ], md=4),
        ]),
        html.Br(),
        dcc.Graph(id='quarter_trend_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_quarter_trend_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='quarter_trend_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_quarter_trend"),
    ])

@callback(
    Output("quarter_trend_graph", "figure"),
    Output("quarter_trend_table", "children"),
    Input('dropdown_quarter_trend_year', "value"),
    Input('dropdown_quarter_trend_category', 'value')
)
def update_graph(year, chosen):
    df = query.quarter_trend_updated(category_or_type=chosen, year=year)

    figure = bar_graph(df, chosen, x_axis='Year-Quarter' , y_axis='Sub Count', hover=['Total Count', 'Start Date', 'End Date'])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_quarter_trend", "data"),
    Input("download_quarter_trend_btn", "n_clicks"),
    State("dropdown_quarter_trend_year", "value"),
    State("dropdown_quarter_trend_category", "value"),
    prevent_initial_call=True,
)
def download_quarter_trend_csv(_, year, chosen):
    df = query.quarter_trend_updated(category_or_type=chosen, year=year)

    return dcc.send_data_frame(df.to_csv, f"quarter_trend_{year}.csv", index=False)
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, bar_graph

def years_trend_layout():
    return html.Div([
        dbc.Card(" Watch Activity For All Years", body=True, className="mt-2"),
        html.Br(),
        dbc.Row([
            dbc.Col(
                [
                html.H6("Show By:", className="content"),
                dcc.Dropdown(id='dropdown_yearly_trend_category',
                        options=['Category', 'Video Type'],
                        value='Category', clearable=False
                    )
                ],
                md=4
            ),
        ]),
        html.Br(),
        dcc.Graph(id='yearly_trend_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_year_trend_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='yearly_trend_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_year_trend"),
    ])

@callback(
    Output("yearly_trend_graph", "figure"),
    Output("yearly_trend_table", "children"),
    Input('dropdown_yearly_trend_category', "value")
)
def update_graph(chosen):
    df = query.yearly_trend_update(category_or_type=chosen)
    figure = bar_graph(df, chosen, x_axis='Year' , y_axis='Sub Count', hover=['Total Count', "Year Start", "Year End"])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_year_trend", "data"),
    Input("download_year_trend_btn", "n_clicks"),
    State("dropdown_yearly_trend_category", "value"),
    prevent_initial_call=True,
)
def download_year_trend_csv(_, chosen):
    df = query.yearly_trend_update(category_or_type=chosen)

    return dcc.send_data_frame(df.to_csv, "year_trend_all_years.csv", index=False)
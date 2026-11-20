import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, bar_graph

def months_trend_layout():

    return html.Div([
        dbc.Card(" Watch Activity For Each Selected Month", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(1, 12, 1, value=4, id='slider_months_trend'),
        html.Br(),
        dbc.Row([
            dbc.Col(
                [
                    html.H6("Show by:", className="mb-1"),
                    dcc.Dropdown(
                        id="dropdown_months_trend",
                        options=["Category", "Video Type"],
                        value="Category",
                        clearable=False,
                    )
                ],
                md=4
            ),
        ]),
        html.Br(),
        dcc.Graph(id='months_trend_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_month_trend_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='months_trend_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_month_trend"),
    ])

@callback(
    Output("months_trend_graph", "figure"),
    Output("months_trend_table", "children"),
    Input('slider_months_trend', "value"),
    Input('dropdown_months_trend', 'value')
)
def update_graph(limit, chosen):
    df = query.monthly_trend_updated(category_or_type=chosen, limit=limit)

    figure = bar_graph(df, chosen, x_axis='Month' , y_axis='Sub Count', hover="Total Count")

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_month_trend", "data"),
    Input("download_month_trend_btn", "n_clicks"),
    State("slider_months_trend", "value"),
    State("dropdown_months_trend", "value"),
    prevent_initial_call=True,
)
def download_month_trend_csv(_, limit, chosen):
    df = query.monthly_trend_updated(category_or_type=chosen, limit=limit)

    return dcc.send_data_frame(df.to_csv, f"month_trend_{limit}_months.csv", index=False)
import dash_bootstrap_components as dbc
from queries.query_connection import query
from dash import html, dcc, callback, Output, Input, State
from visual_functions import table, bar_graph

def last_days_layout():

    return html.Div([
        dbc.Card(" Watch Activity For Selected Last Days", body=True, className="mt-2"),
        html.Br(),
        dcc.Slider(1, 30, 1, value=7, id='slider_last_days'),
        html.Br(),
        dbc.Row([
            dbc.Col(
                [
                html.H6("Show By:", className="content"),
                dcc.Dropdown(id='dropdown_last_days',
                        options=['Category', 'Video Type'],
                        value='Category', clearable=False
                    )
                ],
                md=4
            ),
        ]),
        html.Br(),
        dcc.Graph(id='last_days_graph'),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Button("Download CSV", id="download_last_days_btn"), md=2, className="ms-auto text-end"),
        ]),
        dbc.Accordion(id='last_days_table', start_collapsed=True, flush=True),
        dcc.Download(id="download_last_days"),
    ])

@callback(
    Output("last_days_graph", "figure"),
    Output("last_days_table", "children"),
    Input('slider_last_days', "value"),
    Input('dropdown_last_days', 'value')
)
def update_graph(limit, chosen):
    df = query.last_days_trend(category_or_type=chosen, limit=limit)
    figure = bar_graph(df, chosen, x_axis='Date' , y_axis='Sub Count', hover=['Total Count', 'Day of Week'])

    return figure, [dbc.AccordionItem(table(table_df=df), title="Show Table")]

@callback(
    Output("download_last_days", "data"),
    Input("download_last_days_btn", "n_clicks"),
    State('slider_last_days', "value"),
    State('dropdown_last_days', 'value'),
    prevent_initial_call=True,
)
def download_last_days_csv(_, limit, chosen):
    df = query.last_days_trend(category_or_type=chosen, limit=limit)

    return dcc.send_data_frame(df.to_csv, f"last_{limit}_days.csv", index=False)